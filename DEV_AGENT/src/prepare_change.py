import os
import re
import shlex
import subprocess
import sys
from datetime import datetime


BACKUP_ROOT = "/opt/htd/backups/dev_agent"
STAGING_ROOT = f"{BACKUP_ROOT}/staging"
# Restriction temporaire : seul un fichier de ce répertoire peut être actif.
TRIAL_ACTIVE_DIR = ("var", "tmp", "htd-deployment-v1-trial")

# Exécuté sur l'Edge. Les ouvertures utilisent O_NOFOLLOW.
# Le fichier actif est remplacé par renameat dans le même répertoire.
# Course résiduelle : entre le dernier contrôle du nom et renameat,
# ce nom peut changer. Un lien n'est pas suivi. L'ancien inode n'est
# pas tronqué.
EDGE_OPS_SOURCE = r'''
import errno
import hashlib
import os
import stat
import sys
import time


def literal_parts(path):
    if not isinstance(path, str) or "\x00" in path:
        raise SystemExit(33)
    if not path.startswith("/") or path == "/" or path.endswith("/"):
        raise SystemExit(33)
    parts = path.split("/")
    if parts[0] != "":
        raise SystemExit(33)
    body = parts[1:]
    if not body:
        raise SystemExit(33)
    for part in body:
        if part in ("", ".", ".."):
            raise SystemExit(33)
    return body


def assert_resolved(path, allow_missing_final):
    parts = literal_parts(path)
    current = ""
    for index, part in enumerate(parts):
        current += "/" + part
        last = index == len(parts) - 1
        if os.path.islink(current):
            raise SystemExit(33)
        if os.path.lexists(current):
            if os.path.realpath(current) != current:
                raise SystemExit(33)
        elif last and allow_missing_final:
            parent = current.rsplit("/", 1)[0] or "/"
            if os.path.islink(parent) or os.path.realpath(parent) != parent:
                raise SystemExit(33)
        else:
            raise SystemExit(33)


def walk_open(path, final_flags, create_mode=None):
    parts = literal_parts(path)
    assert_resolved(path, allow_missing_final=create_mode is not None)
    nofollow = os.O_NOFOLLOW
    directory = os.O_DIRECTORY
    current = None
    try:
        try:
            current = os.open("/", os.O_RDONLY | directory | nofollow)
        except OSError:
            raise SystemExit(33)
        for index, part in enumerate(parts):
            last = index == len(parts) - 1
            try:
                if last and create_mode is not None:
                    opened = os.open(
                        part,
                        final_flags | nofollow | os.O_CREAT | os.O_EXCL,
                        create_mode,
                        dir_fd=current,
                    )
                elif last:
                    opened = os.open(
                        part,
                        final_flags | nofollow,
                        dir_fd=current,
                    )
                else:
                    opened = os.open(
                        part,
                        os.O_RDONLY | directory | nofollow,
                        dir_fd=current,
                    )
            except OSError as exc:
                if getattr(exc, "errno", None) == errno.EEXIST:
                    raise SystemExit(11)
                raise SystemExit(33)
            os.close(current)
            current = opened
        result = current
        current = None
        return result
    finally:
        if current is not None:
            os.close(current)


def sha256_fd(fd):
    os.lseek(fd, 0, os.SEEK_SET)
    digest = hashlib.sha256()
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
    return digest.hexdigest()


def read_fd(fd):
    os.lseek(fd, 0, os.SEEK_SET)
    chunks = []
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


def write_all(fd, data):
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    view = memoryview(data)
    offset = 0
    while offset < len(view):
        written = os.write(fd, view[offset:])
        if written <= 0:
            raise SystemExit(39)
        offset += written
    os.fsync(fd)


def open_parent_and_file(path, file_flags):
    parts = literal_parts(path)
    assert_resolved(path, allow_missing_final=False)
    nofollow = os.O_NOFOLLOW
    directory = os.O_DIRECTORY
    current = None
    try:
        try:
            current = os.open("/", os.O_RDONLY | directory | nofollow)
        except OSError:
            raise SystemExit(33)
        for part in parts[:-1]:
            try:
                opened = os.open(
                    part,
                    os.O_RDONLY | directory | nofollow,
                    dir_fd=current,
                )
            except OSError:
                raise SystemExit(33)
            os.close(current)
            current = opened
        final_name = parts[-1]
        try:
            file_fd = os.open(
                final_name,
                file_flags | nofollow,
                dir_fd=current,
            )
        except OSError:
            raise SystemExit(33)
        dir_fd = current
        current = None
        return dir_fd, final_name, file_fd
    finally:
        if current is not None:
            os.close(current)


def unlink_at(dir_fd, name):
    try:
        os.unlink(name, dir_fd=dir_fd)
        return
    except TypeError:
        pass
    parent = os.readlink("/proc/self/fd/%d" % dir_fd)
    os.unlink(parent.rstrip("/") + "/" + name)


def create_exclusive(path, mode):
    parts = literal_parts(path)
    assert_resolved(path, allow_missing_final=True)
    nofollow = os.O_NOFOLLOW
    directory = os.O_DIRECTORY
    current = None
    try:
        try:
            current = os.open("/", os.O_RDONLY | directory | nofollow)
        except OSError:
            raise SystemExit(33)
        for part in parts[:-1]:
            try:
                opened = os.open(
                    part,
                    os.O_RDONLY | directory | nofollow,
                    dir_fd=current,
                )
            except OSError:
                raise SystemExit(33)
            os.close(current)
            current = opened
        final_name = parts[-1]
        try:
            # O_RDWR : le SHA est relu sur ce descripteur. O_WRONLY
            # produit EBADF. O_EXCL refuse un nom déjà présent.
            # Un lien donne ELOOP, donc 33, et non 11.
            file_fd = os.open(
                final_name,
                os.O_RDWR | os.O_CREAT | os.O_EXCL | nofollow,
                mode,
                dir_fd=current,
            )
        except OSError as exc:
            if getattr(exc, "errno", None) == errno.EEXIST:
                raise SystemExit(11)
            raise SystemExit(33)
        dir_fd = current
        current = None
        return dir_fd, final_name, file_fd
    finally:
        if current is not None:
            os.close(current)


def discard_unvalidated(dir_fd, name, inode, device):
    try:
        current = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
    except OSError:
        return
    if (
        not stat.S_ISREG(current.st_mode)
        or current.st_ino != inode
        or current.st_dev != device
    ):
        return
    # Course résiduelle : le nom peut changer entre ce contrôle et unlink.
    unlink_at(dir_fd, name)


def replace_in_directory(
    dir_fd,
    final_name,
    active_fd,
    payload,
    expected_sha,
    uid,
    gid,
    mode,
):
    info = os.fstat(active_fd)
    if not stat.S_ISREG(info.st_mode):
        raise SystemExit(33)
    if (
        info.st_uid != uid
        or info.st_gid != gid
        or (info.st_mode & 0o777) != mode
    ):
        raise SystemExit(35)
    temp_fd = None
    temp_name = None
    replaced = False
    try:
        for _ in range(8):
            temp_name = "." + final_name + ".HTD_NEW_" + os.urandom(6).hex()
            if len(temp_name) > 255:
                raise SystemExit(33)
            try:
                temp_fd = os.open(
                    temp_name,
                    os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=dir_fd,
                )
                break
            except OSError as exc:
                if getattr(exc, "errno", None) != errno.EEXIST:
                    raise SystemExit(33)
        if temp_fd is None:
            raise SystemExit(33)
        view = memoryview(payload)
        offset = 0
        while offset < len(view):
            written = os.write(temp_fd, view[offset:])
            if written <= 0:
                raise SystemExit(39)
            offset += written
        os.fsync(temp_fd)
        if sha256_fd(temp_fd) != expected_sha:
            raise SystemExit(30)
        try:
            os.fchown(temp_fd, uid, gid)
            os.fchmod(temp_fd, mode)
        except OSError:
            raise SystemExit(35)
        os.fsync(temp_fd)
        if sha256_fd(temp_fd) != expected_sha:
            raise SystemExit(30)
        current = os.stat(
            final_name,
            dir_fd=dir_fd,
            follow_symlinks=False,
        )
        still = os.fstat(active_fd)
        if (
            not stat.S_ISREG(current.st_mode)
            or current.st_ino != still.st_ino
            or current.st_dev != still.st_dev
        ):
            raise SystemExit(35)
        # Course résiduelle : entre ce contrôle et renameat, un autre
        # processus peut remplacer le nom. renameat ne suit pas un lien.
        # L'inode déjà vérifié n'est pas tronqué.
        os.rename(
            temp_name,
            final_name,
            src_dir_fd=dir_fd,
            dst_dir_fd=dir_fd,
        )
        replaced = True
        try:
            os.fsync(dir_fd)
        except OSError:
            sys.stderr.write(
                "REMPLACEMENT EFFECTUE ; "
                "synchronisation du repertoire en echec.\n"
            )
            raise SystemExit(39)
    except BaseException:
        if not replaced and temp_name is not None:
            try:
                unlink_at(dir_fd, temp_name)
            except OSError:
                pass
        raise
    finally:
        if temp_fd is not None:
            os.close(temp_fd)


def apply_checked(
    active_path,
    candidate_path,
    expected_active,
    expected_candidate,
    uid,
    gid,
    mode,
):
    dir_fd, final_name, active_fd = open_parent_and_file(
        active_path,
        os.O_RDWR,
    )
    try:
        candidate_fd = walk_open(candidate_path, os.O_RDONLY)
        try:
            active_sha = sha256_fd(active_fd)
            payload = read_fd(candidate_fd)
            candidate_sha = hashlib.sha256(payload).hexdigest()
            if (
                active_sha != expected_active
                or candidate_sha != expected_candidate
            ):
                raise SystemExit(30)
            replace_in_directory(
                dir_fd,
                final_name,
                active_fd,
                payload,
                expected_candidate,
                uid,
                gid,
                mode,
            )
        finally:
            os.close(candidate_fd)
    finally:
        os.close(active_fd)
        os.close(dir_fd)


def rollback_checked(
    active_path,
    backup_path,
    expected_backup_sha,
    uid,
    gid,
    mode,
    inode,
    device,
):
    dir_fd, final_name, active_fd = open_parent_and_file(
        active_path,
        os.O_RDWR,
    )
    try:
        backup_fd = walk_open(backup_path, os.O_RDONLY)
        try:
            info = os.fstat(active_fd)
            actual_mode = info.st_mode & 0o777
            if (
                info.st_uid != uid
                or info.st_gid != gid
                or actual_mode != mode
                or info.st_ino != inode
                or info.st_dev != device
            ):
                raise SystemExit(35)
            payload = read_fd(backup_fd)
            backup_sha = hashlib.sha256(payload).hexdigest()
            if backup_sha != expected_backup_sha:
                raise SystemExit(30)
            replace_in_directory(
                dir_fd,
                final_name,
                active_fd,
                payload,
                expected_backup_sha,
                uid,
                gid,
                mode,
            )
        finally:
            os.close(backup_fd)
    finally:
        os.close(active_fd)
        os.close(dir_fd)


def backup_checked(source_path, backup_path, expected_source_sha):
    source_fd = walk_open(source_path, os.O_RDONLY)
    try:
        payload = read_fd(source_fd)
        source_sha = hashlib.sha256(payload).hexdigest()
        if source_sha != expected_source_sha:
            raise SystemExit(10)
        info = os.fstat(source_fd)
        dir_fd, final_name, backup_fd = create_exclusive(
            backup_path,
            info.st_mode & 0o777,
        )
        created = os.fstat(backup_fd)
        validated = False
        try:
            write_all(backup_fd, payload)
            written_sha = sha256_fd(backup_fd)
            if written_sha != source_sha:
                raise SystemExit(12)
            validated = True
        finally:
            os.close(backup_fd)
            if not validated:
                try:
                    discard_unvalidated(
                        dir_fd,
                        final_name,
                        created.st_ino,
                        created.st_dev,
                    )
                except OSError:
                    pass
            os.close(dir_fd)
        sys.stdout.write(source_sha + "\n" + written_sha + "\n")
    finally:
        os.close(source_fd)


def describe(path):
    import grp
    import pwd

    fd = walk_open(path, os.O_RDONLY)
    try:
        info = os.fstat(fd)
        digest = sha256_fd(fd)
        try:
            user = pwd.getpwuid(info.st_uid).pw_name
        except KeyError:
            user = str(info.st_uid)
        try:
            group = grp.getgrgid(info.st_gid).gr_name
        except KeyError:
            group = str(info.st_gid)
        modified = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(info.st_mtime),
        )
        mode = format(info.st_mode & 0o777, "o")
        line = "|".join(
            [
                str(info.st_size),
                user,
                group,
                str(info.st_uid),
                str(info.st_gid),
                mode,
                modified,
                str(info.st_ino),
                str(info.st_dev),
            ]
        )
        sys.stdout.write(line + "\n" + digest + "\n")
    finally:
        os.close(fd)


def assert_literal(path):
    fd = walk_open(path, os.O_RDONLY)
    os.close(fd)


def ensure_dir(path):
    parts = literal_parts(path)
    nofollow = os.O_NOFOLLOW
    directory = os.O_DIRECTORY
    current = os.open("/", os.O_RDONLY | directory | nofollow)
    try:
        built = ""
        for part in parts:
            parent = built or "/"
            built += "/" + part
            if os.path.islink(built):
                raise SystemExit(33)
            if os.path.lexists(built) and os.path.realpath(built) != built:
                raise SystemExit(33)
            try:
                opened = os.open(
                    part,
                    os.O_RDONLY | directory | nofollow,
                    dir_fd=current,
                )
            except OSError as exc:
                if getattr(exc, "errno", None) != errno.ENOENT:
                    raise SystemExit(33)
                if (
                    os.path.islink(parent)
                    or os.path.realpath(parent) != parent
                ):
                    raise SystemExit(33)
                os.mkdir(part, 0o755, dir_fd=current)
                opened = os.open(
                    part,
                    os.O_RDONLY | directory | nofollow,
                    dir_fd=current,
                )
            os.close(current)
            current = opened
        if os.path.realpath(path) != path:
            raise SystemExit(33)
    finally:
        os.close(current)


def stage_receive(path):
    payload = sys.stdin.buffer.read()
    parent = path.rsplit("/", 1)[0]
    ensure_dir(parent)
    fd = walk_open(path, os.O_WRONLY, create_mode=0o644)
    try:
        write_all(fd, payload)
    finally:
        os.close(fd)


def yaml_check(path):
    import yaml

    fd = walk_open(path, os.O_RDONLY)
    try:
        payload = read_fd(fd)
    finally:
        os.close(fd)
    yaml.safe_load(payload.decode("utf-8"))


def verify_checked(active_path, backup_path, candidate_path, expected_active):
    active_fd = walk_open(active_path, os.O_RDONLY)
    try:
        backup_fd = walk_open(backup_path, os.O_RDONLY)
        try:
            candidate_fd = walk_open(candidate_path, os.O_RDONLY)
            try:
                active_sha = sha256_fd(active_fd)
                backup_sha = sha256_fd(backup_fd)
                candidate_sha = sha256_fd(candidate_fd)
            finally:
                os.close(candidate_fd)
        finally:
            os.close(backup_fd)
    finally:
        os.close(active_fd)
    if active_sha != expected_active:
        sys.stdout.write("__HTD_ACTIVE_CHANGED__\n")
        raise SystemExit(30)
    if active_sha != backup_sha:
        sys.stdout.write("__HTD_BACKUP_INVALID__\n")
        raise SystemExit(31)
    sys.stdout.write(active_sha + "\n" + candidate_sha + "\n")


def run(argv):
    operation = argv[1]
    if operation == "describe":
        describe(argv[2])
    elif operation == "assert":
        assert_literal(argv[2])
    elif operation == "verify":
        verify_checked(argv[2], argv[3], argv[4], argv[5])
    elif operation == "backup":
        backup_checked(argv[2], argv[3], argv[4])
    elif operation == "apply":
        apply_checked(
            argv[2],
            argv[3],
            argv[4],
            argv[5],
            int(argv[6]),
            int(argv[7]),
            int(argv[8], 8),
        )
    elif operation == "rollback":
        rollback_checked(
            argv[2],
            argv[3],
            argv[4],
            int(argv[5]),
            int(argv[6]),
            int(argv[7], 8),
            int(argv[8]),
            int(argv[9]),
        )
    elif operation == "stage":
        stage_receive(argv[2])
    elif operation == "yaml":
        yaml_check(argv[2])
    else:
        raise SystemExit(33)
'''


def load_edge_ops(os_module=None):
    namespace = {"__name__": "htd_edge_ops"}
    exec(EDGE_OPS_SOURCE, namespace)
    if os_module is not None:
        namespace["os"] = os_module
    return namespace


def validate_literal_remote_path(path):
    if not isinstance(path, str) or "\x00" in path:
        return False
    if not path.startswith("/") or path == "/" or path.endswith("/"):
        return False
    parts = path.split("/")
    if parts[0] != "" or len(parts) < 2:
        return False
    for part in parts[1:]:
        if part in ("", ".", ".."):
            return False
    return True


def remote_path_problem(path):
    if not isinstance(path, str) or not path.startswith("/"):
        return 1, "Le chemin distant doit être absolu."
    if not validate_literal_remote_path(path):
        return (
            33,
            "Chemin refusé : composant '.', '..' ou vide, "
            "ou barre oblique finale.",
        )
    return None


def trial_active_path_allowed(path):
    if not isinstance(path, str) or "\x00" in path:
        return False
    if not path.startswith("/") or path.endswith("/"):
        return False
    parts = path.split("/")
    if parts[0] != "":
        return False
    body = parts[1:]
    if any(part in ("", ".", "..") for part in body):
        return False
    if len(body) != len(TRIAL_ACTIVE_DIR) + 1:
        return False
    if tuple(body[:-1]) != TRIAL_ACTIVE_DIR:
        return False
    return True


def active_path_problem(path):
    if trial_active_path_allowed(path):
        return None
    return (
        33,
        "Chemin actif refusé : seul un fichier de "
        "/var/tmp/htd-deployment-v1-trial/ est autorisé.",
    )


def path_has_dot_component(path):
    normalized = str(path).replace("\\", "/")
    for part in normalized.split("/"):
        if part in (".", ".."):
            return True
    return False


def local_candidate_problem(path):
    if path_has_dot_component(path):
        return 33, "Le chemin candidat contient '.' ou '..'."
    if os.path.islink(path):
        return 33, "Le candidat local est un lien symbolique."
    if not os.path.isfile(path):
        return 20, "Le fichier candidat local n'existe pas."
    current = os.path.abspath(path)
    while True:
        if os.path.islink(current):
            return 33, "Le candidat local traverse un lien symbolique."
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def build_edge_command(arguments, privileged=False):
    script = EDGE_OPS_SOURCE + "\nrun(sys.argv)\n"
    quoted_arguments = " ".join(shlex.quote(argument) for argument in arguments)
    command = f"python3 -I -c {shlex.quote(script)} {quoted_arguments}"
    if privileged:
        command = "sudo " + command
    return command


def literal_path_error():
    return (
        "Chemin refusé : lien symbolique, composant '.' ou '..', "
        "ou chemin résolu différent."
    )


def validate_target(target):
    pattern = r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.:-]+$"
    return re.fullmatch(pattern, target) is not None


def run_ssh(target, remote_command, stdin_bytes=None):
    try:
        if stdin_bytes is None:
            result = subprocess.run(
                ["ssh", target, remote_command],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            stdout = result.stdout
            stderr = result.stderr
        else:
            result = subprocess.run(
                ["ssh", target, remote_command],
                input=stdin_bytes,
                capture_output=True,
                check=False,
            )
            stdout = result.stdout.decode("utf-8", "replace")
            stderr = result.stderr.decode("utf-8", "replace")
    except FileNotFoundError:
        return 1, "", "La commande ssh n'est pas disponible."

    return result.returncode, stdout.strip(), stderr.strip()


def run_interactive_ssh(target, remote_command):
    try:
        result = subprocess.run(
            ["ssh", "-t", target, remote_command],
            check=False,
        )
    except FileNotFoundError:
        return 1

    return result.returncode


def run_scp(local_path, target, remote_path):
    try:
        result = subprocess.run(
            ["scp", local_path, f"{target}:{remote_path}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
)
    except FileNotFoundError:
        return 1, "La commande scp n'est pas disponible."

    if result.returncode != 0:
        return (
            result.returncode,
            result.stderr.strip()
            or result.stdout.strip()
            or "Échec du transfert SCP.",
        )

    return 0, ""


def get_remote_file_info(target, remote_path):
    problem = remote_path_problem(remote_path)
    if problem is not None:
        return problem[0], None, problem[1]

    code, stdout, stderr = run_ssh(
        target,
        build_edge_command(["describe", remote_path]),
    )

    if code == 33:
        return 33, None, stderr or stdout or literal_path_error()

    if code != 0:
        return code, None, stderr or stdout

    lines = stdout.splitlines()

    if not lines or lines[0] == "__HTD_NOT_FILE__":
        return 2, None, "Le chemin distant n'est pas un fichier valide."

    if len(lines) < 2:
        return 3, None, "Réponse distante incomplète."

    stat_parts = lines[0].split("|")

    if len(stat_parts) != 9:
        return 4, None, "Format stat distant inattendu."

    size, owner, group, uid, gid, mode, modified, inode, device = stat_parts
    sha256 = lines[1].strip()

    info = {
        "size": size,
        "owner": owner,
        "group": group,
        "uid": uid,
        "gid": gid,
        "mode": mode,
        "modified": modified,
        "inode": inode,
        "device": device,
        "sha256": sha256,
    }

    return 0, info, ""


def build_backup_path(remote_path):
    filename = os.path.basename(remote_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_name = f"{filename}.HTD_BACKUP_{timestamp}"

    return f"{BACKUP_ROOT}/{backup_name}"


def build_staging_path(remote_path):
    filename = os.path.basename(remote_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    staged_name = f"{filename}.HTD_CANDIDATE_{timestamp}"

    return f"{STAGING_ROOT}/{staged_name}"


def create_remote_backup(
    target,
    remote_path,
    backup_path,
    expected_sha256,
):
    problem = remote_path_problem(remote_path) or remote_path_problem(backup_path)
    if problem is not None:
        return problem[0], None, problem[1]

    code, stdout, stderr = run_ssh(
        target,
        build_edge_command(
            ["backup", remote_path, backup_path, expected_sha256]
        ),
    )
    lines = stdout.splitlines()

    if code == 10 or "__HTD_SOURCE_CHANGED__" in lines:
        return (
            10,
            None,
            "Le fichier source a changé depuis le PLAN. "
            "Backup annulé.",
        )

    if code == 11 or "__HTD_BACKUP_EXISTS__" in lines:
        return (
            11,
            None,
            "Le chemin de backup existe déjà. Backup annulé.",
        )

    if code == 12 or "__HTD_BACKUP_MISMATCH__" in lines:
        return (
            12,
            None,
            "Le SHA-256 du backup ne correspond pas à la source.",
        )

    if code == 33:
        return code, None, stderr or stdout or literal_path_error()

    if code != 0:
        return (
            code,
            None,
            stderr or stdout or "Échec du backup distant.",
        )

    if len(lines) < 2:
        return (
            13,
            None,
            "Réponse distante incomplète après le backup.",
        )

    result = {
        "source_sha256": lines[-2].strip(),
        "backup_sha256": lines[-1].strip(),
    }

    return 0, result, ""


def stage_candidate(target, local_candidate, remote_staging_path):
    problem = local_candidate_problem(local_candidate)
    if problem is not None:
        return problem[0], None, problem[1]

    remote_problem = remote_path_problem(remote_staging_path)
    if remote_problem is not None:
        return remote_problem[0], None, remote_problem[1]

    with open(local_candidate, "rb") as handle:
        payload = handle.read()

    code, stdout, stderr = run_ssh(
        target,
        build_edge_command(["stage", remote_staging_path]),
        stdin_bytes=payload,
    )

    if code != 0:
        return (
            code,
            None,
            stderr or stdout or literal_path_error(),
        )

    code, info, error = get_remote_file_info(
        target,
        remote_staging_path,
    )

    if code != 0:
        return code, None, error

    return 0, info, ""


def validate_staged_candidate(
    target,
    active_path,
    candidate_path,
):
    extension = os.path.splitext(active_path)[1].lower()

    if extension not in (".yaml", ".yml"):
        return 0, "Validation YAML non applicable."

    code, stdout, stderr = run_ssh(
        target,
        build_edge_command(["yaml", candidate_path]),
    )

    if code != 0:
        return (
            code,
            stderr
            or stdout
            or "Le candidat YAML est invalide.",
        )

    return 0, "YAML_OK"


def get_remote_diff(target, active_path, candidate_path):
    for path in (active_path, candidate_path):
        code, stdout, stderr = run_ssh(
            target,
            build_edge_command(["assert", path]),
        )
        if code != 0:
            return code, stdout, stderr or literal_path_error()

    quoted_active = shlex.quote(active_path)
    quoted_candidate = shlex.quote(candidate_path)

    command = (
        f"diff -u --label ACTIVE --label CANDIDATE "
        f"{quoted_active} {quoted_candidate}; "
        f"RC=$?; "
        f"if [ \"$RC\" -gt 1 ]; then exit \"$RC\"; fi; "
        f"exit 0"
    )

    return run_ssh(target, command)


def get_rollback_diff(
    target,
    active_path,
    backup_path,
):
    for path in (active_path, backup_path):
        code, stdout, stderr = run_ssh(
            target,
            build_edge_command(["assert", path]),
        )
        if code != 0:
            return code, stdout, stderr or literal_path_error()

    quoted_active = shlex.quote(active_path)
    quoted_backup = shlex.quote(backup_path)

    command = (
        "diff -u "
        "--label ACTIVE "
        "--label BACKUP "
        f"{quoted_active} {quoted_backup}"
    )

    code, stdout, stderr = run_ssh(
        target,
        command,
    )

    if code not in (0, 1):
        return code, stdout, stderr

    return 0, stdout, ""


def verify_before_apply(
    target,
    active_path,
    backup_path,
    candidate_path,
    expected_active_sha,
):
    for path in (active_path, backup_path, candidate_path):
        problem = remote_path_problem(path)
        if problem is not None:
            return problem[0], None, problem[1]

    code, stdout, stderr = run_ssh(
        target,
        build_edge_command(
            [
                "verify",
                active_path,
                backup_path,
                candidate_path,
                expected_active_sha,
            ]
        ),
    )
    lines = stdout.splitlines()

    if code == 30 or "__HTD_ACTIVE_CHANGED__" in lines:
        return (
            30,
            None,
            "Le fichier actif a changé depuis le PLAN. APPLY annulé.",
        )

    if code == 31 or "__HTD_BACKUP_INVALID__" in lines:
        return (
            31,
            None,
            "Le backup ne correspond plus au fichier actif. "
            "APPLY annulé.",
        )

    if code != 0:
        return (
            code,
            None,
            stderr or stdout or "Échec de la vérification pré-APPLY.",
        )

    if len(lines) < 2:
        return (
            32,
            None,
            "Réponse distante incomplète avant APPLY.",
        )

    result = {
        "active_sha256": lines[-2].strip(),
        "candidate_sha256": lines[-1].strip(),
    }

    return 0, result, ""


def apply_candidate(
    target,
    active_path,
    candidate_path,
    expected_active_sha,
    expected_candidate_sha,
    uid,
    gid,
    mode,
):
    # Temporaire dans le même répertoire, puis renameat. Course résiduelle
    # entre le dernier contrôle du nom et le remplacement : le nom peut
    # changer. Un lien n'est pas suivi et l'ancien inode n'est pas tronqué.
    command = build_edge_command(
        [
            "apply",
            active_path,
            candidate_path,
            expected_active_sha,
            expected_candidate_sha,
            str(uid),
            str(gid),
            str(mode),
        ],
        privileged=True,
    )

    return run_interactive_ssh(
        target,
        command,
    )


def rollback_backup(
    target,
    active_path,
    backup_path,
    expected_backup_sha,
    uid,
    gid,
    mode,
    inode,
    device,
):
    command = build_edge_command(
        [
            "rollback",
            active_path,
            backup_path,
            expected_backup_sha,
            str(uid),
            str(gid),
            str(mode),
            str(inode),
            str(device),
        ],
        privileged=True,
    )

    return run_interactive_ssh(
        target,
        command,
    )


def print_plan(
    target,
    remote_path,
    info,
    backup_path,
    include_procedure=True,
):
    print("=" * 60)
    print("HTD Dev Agent V1 — Change Preparation")
    print("=" * 60)
    print()

    print("[TARGET]")
    print(f"Machine      : {target}")
    print(f"Fichier      : {remote_path}")
    print()

    print("[FICHIER DISTANT]")
    print(f"Taille       : {info['size']} octets")
    print(f"Propriétaire : {info['owner']} (UID {info['uid']})")
    print(f"Groupe       : {info['group']} (GID {info['gid']})")
    print(f"Permissions  : {info['mode']}")
    print(f"Modifié      : {info['modified']}")
    print(f"SHA-256      : {info['sha256']}")
    print()

    if include_procedure:
        print("[PLAN]")
        print("1. Inspecter le contenu nécessaire.")
        print("2. Définir précisément la modification.")
        print("3. Faire approuver la modification.")
        print("4. Créer une sauvegarde ciblée du fichier.")
        print("5. Préparer et vérifier le fichier candidat.")
        print("6. Présenter le diff avant APPLY.")
        print("7. Exiger une confirmation humaine.")
        print("8. Appliquer avec élévation sudo interactive.")
        print("9. Valider le résultat.")
        print("10. Produire le rapport avant/après.")
        print("11. Restaurer le backup si nécessaire.")
        print()

    print("[BACKUP PRÉVU]")
    print(f"Chemin : {backup_path}")
    print()


def print_final_plan(
    target,
    remote_path,
    info,
    active_sha256,
    candidate_sha256,
    backup_path,
    backup_sha256,
):
    print("[PLAN FINAL]")
    print(f"Machine      : {target}")
    print(f"Fichier      : {remote_path}")
    print(f"UID          : {info['uid']}")
    print(f"GID          : {info['gid']}")
    print(f"Permissions  : {info['mode']}")
    print(f"SHA actif    : {active_sha256}")
    print(f"SHA candidat : {candidate_sha256}")
    print(f"Backup       : {backup_path}")
    print(f"SHA backup   : {backup_sha256}")
    print("Diff         : affiché ci-dessus.")
    print("Le fichier actif n'a pas été modifié.")
    print()


def print_no_backup_status():
    print("[STATUT]")
    print("Aucune sauvegarde créée.")
    print("Aucune modification effectuée.")
    print()
    print("=" * 60)


def print_backup_result(backup_path, result):
    print("[BACKUP]")
    print(f"Créé         : {backup_path}")
    print(f"SHA source   : {result['source_sha256']}")
    print(f"SHA backup   : {result['backup_sha256']}")
    print("Vérification : IDENTIQUE")
    print()


def print_candidate_result(
    local_candidate,
    remote_candidate,
    info,
):
    print("[CANDIDAT]")
    print(f"Local        : {local_candidate}")
    print(f"Staging Edge : {remote_candidate}")
    print(f"Taille       : {info['size']} octets")
    print(f"SHA-256      : {info['sha256']}")
    print()


def print_usage():
    print("Usage :")
    print(
        "python prepare_change.py "
        "<utilisateur@adresse> <fichier_distant>"
    )
    print()
    print("PLAN + BACKUP :")
    print(
        "python prepare_change.py "
        "<utilisateur@adresse> <fichier_distant> --backup"
    )
    print()
    print("Préparer un candidat sans APPLY :")
    print(
        "python prepare_change.py "
        "<utilisateur@adresse> <fichier_distant> "
        "--candidate <fichier_local>"
    )
    print()
    print("APPLY contrôlé :")
    print(
        "python prepare_change.py "
        "<utilisateur@adresse> <fichier_distant> "
        "--apply <fichier_local>"
    )
    print()
    print("ROLLBACK contrôlé :")
    print(
        "python prepare_change.py "
        "<utilisateur@adresse> <fichier_distant> "
        "--rollback <chemin_backup>"
    )


def main():
    if len(sys.argv) not in (3, 4, 5):
        print_usage()
        return 1

    target = sys.argv[1]
    remote_path = sys.argv[2]

    if not validate_target(target):
        print("[ERREUR] Cible SSH invalide.")
        print("Format attendu : utilisateur@adresse")
        return 1

    path_problem = remote_path_problem(remote_path)
    if path_problem is not None:
        print("[ERREUR]")
        print(path_problem[1])
        return path_problem[0]

    scope_problem = active_path_problem(remote_path)
    if scope_problem is not None:
        print("[ERREUR]")
        print(scope_problem[1])
        return scope_problem[0]

    mode = "plan"
    local_candidate = None
    rollback_path = None

    if len(sys.argv) == 4:
        if sys.argv[3] == "--backup":
            mode = "backup"
        else:
            print("[ERREUR] Option inconnue.")
            print_usage()
            return 1

    if len(sys.argv) == 5:
        if sys.argv[3] == "--candidate":
            mode = "candidate"
            local_candidate = sys.argv[4]
        elif sys.argv[3] == "--apply":
            mode = "apply"
            local_candidate = sys.argv[4]
        elif sys.argv[3] == "--rollback":
            mode = "rollback"
            rollback_path = sys.argv[4]
        else:
            print("[ERREUR] Option inconnue.")
            print_usage()
            return 1

    if rollback_path is not None:
        rollback_problem = remote_path_problem(rollback_path)
        if rollback_problem is not None:
            print("[ERREUR]")
            print(rollback_problem[1])
            return rollback_problem[0]

    code, original_info, error = get_remote_file_info(
        target,
        remote_path,
    )

    if code != 0:
        print("[ERREUR] Impossible de préparer la modification.")
        if error:
            print(error)
        return code

    backup_path = build_backup_path(remote_path)

    print_plan(
        target,
        remote_path,
        original_info,
        backup_path,
        include_procedure=(mode != "apply"),
    )

    if mode == "plan":
        print("[STATUT]")
        print("Aucune sauvegarde créée.")
        print("Aucun candidat transféré.")
        print("Aucune modification effectuée.")
        print()
        print("=" * 60)
        return 0

    if mode == "backup":
        code, backup_result, error = create_remote_backup(
            target,
            remote_path,
            backup_path,
            original_info["sha256"],
        )

        if code != 0:
            print("[ERREUR BACKUP]")
            print(error)
            print("=" * 60)
            return code

        print_backup_result(
            backup_path,
            backup_result,
        )

        print("[STATUT]")
        print("Sauvegarde ciblée créée et vérifiée.")
        print("Le fichier actif n'a pas été modifié.")
        print()
        print("=" * 60)
        return 0

    if mode == "rollback":
        code, backup_info, error = get_remote_file_info(
            target,
            rollback_path,
        )

        if code != 0:
            print("[ERREUR ROLLBACK]")
            print("Backup introuvable ou inaccessible.")
            if error:
                print(error)
            print("=" * 60)
            return code

        code, diff_output, diff_error = get_rollback_diff(
            target,
            remote_path,
            rollback_path,
        )

        if code != 0:
            print("[ERREUR DIFF ROLLBACK]")
            print(diff_error or diff_output)
            print("=" * 60)
            return code

        print("[ROLLBACK PRÉVU]")
        print(f"Backup        : {rollback_path}")
        print(f"SHA actif     : {original_info['sha256']}")
        print(f"SHA backup    : {backup_info['sha256']}")
        print()

        print("[DIFF AVANT ROLLBACK]")

        if diff_output:
            print(diff_output)
        else:
            print("Aucune différence entre ACTIVE et BACKUP.")

        print()

        if original_info["sha256"] == backup_info["sha256"]:
            print("[ARRÊT]")
            print("Le fichier actif est déjà identique au backup.")
            print("Aucun ROLLBACK nécessaire.")
            print("=" * 60)
            return 0

        print("ATTENTION :")
        print("La prochaine étape restaurera le contenu du backup")
        print("dans le fichier actif.")
        print("Une authentification sudo interactive sera requise.")
        print()

        confirmation = input(
            "Pour autoriser le ROLLBACK, tape exactement ROLLBACK : "
        )

        if confirmation != "ROLLBACK":
            print()
            print("[ANNULÉ]")
            print("Confirmation non reçue.")
            print("Le fichier actif n'a pas été modifié.")
            print("=" * 60)
            return 15

        print()
        print("[ROLLBACK]")
        print("Demande d'élévation sudo sur le HTD Edge...")

        code = rollback_backup(
            target,
            remote_path,
            rollback_path,
            backup_info["sha256"],
            original_info["uid"],
            original_info["gid"],
            original_info["mode"],
            original_info["inode"],
            original_info["device"],
        )

        if code != 0:
            print()
            print("[ERREUR ROLLBACK]")
            print(f"Code de retour : {code}")
            if code in (30, 33, 35):
                print("Écriture non commencée.")
                print("Le fichier actif n'a pas été remplacé.")
            elif code == 39:
                print(
                    "Si le terminal distant affiche REMPLACEMENT EFFECTUE, "
                    "le fichier actif a été remplacé et la synchronisation "
                    "du répertoire a échoué."
                )
            else:
                print("L'état du fichier actif doit être vérifié.")
            print("=" * 60)
            return code

        code, restored_info, error = get_remote_file_info(
            target,
            remote_path,
        )

        if code != 0:
            print("[ERREUR POST-ROLLBACK]")
            print(error)
            print("=" * 60)
            return code

        print()
        print("[POST-ROLLBACK]")
        print(f"SHA backup    : {backup_info['sha256']}")
        print(f"SHA actif     : {restored_info['sha256']}")
        print(f"Propriétaire  : {restored_info['owner']} (UID {restored_info['uid']})")
        print(f"Groupe        : {restored_info['group']} (GID {restored_info['gid']})")
        print(f"Permissions   : {restored_info['mode']}")
        print()

        if restored_info["sha256"] != backup_info["sha256"]:
            print("[ERREUR]")
            print("Le fichier actif ne correspond pas au backup.")
            print("=" * 60)
            return 50

        metadata_ok = (
            restored_info["uid"] == original_info["uid"]
            and restored_info["gid"] == original_info["gid"]
            and restored_info["mode"] == original_info["mode"]
        )

        if not metadata_ok:
            print("[ERREUR]")
            print("Les métadonnées du fichier actif ont changé.")
            print("=" * 60)
            return 51

        print("[RÉSULTAT]")
        print("ROLLBACK terminé.")
        print("Le contenu actif correspond au backup.")
        print("UID, GID et permissions sont préservés.")
        print("=" * 60)
        return 0

    staging_path = build_staging_path(remote_path)

    code, candidate_info, error = stage_candidate(
        target,
        local_candidate,
        staging_path,
    )

    if code != 0:
        print("[ERREUR CANDIDAT]")
        print(error)
        print("=" * 60)
        return code

    print_candidate_result(
        local_candidate,
        staging_path,
        candidate_info,
    )

    code, validation_result = validate_staged_candidate(
        target,
        remote_path,
        staging_path,
    )

    print("[VALIDATION CANDIDAT]")

    if code != 0:
        print("ÉCHEC")
        print(validation_result)
        print()
        print("[ARRÊT]")
        print("Le candidat n'est pas valide.")
        print("Le fichier actif n'a pas été modifié.")
        print("=" * 60)
        return code

    print(validation_result)
    print()

    code, diff_output, diff_error = get_remote_diff(
        target,
        remote_path,
        staging_path,
    )

    if code != 0:
        print("[ERREUR DIFF]")
        print(diff_error or diff_output)
        print("=" * 60)
        return code

    print("[DIFF AVANT APPLY]")

    if diff_output:
        print(diff_output)
    else:
        print("Aucune différence entre ACTIVE et CANDIDATE.")

    print()

    if mode == "candidate":
        print("[STATUT]")
        print("Le candidat a été transféré en staging.")
        print("Le fichier actif n'a pas été modifié.")
        print("Aucun backup APPLY n'a été créé.")
        print()
        print("=" * 60)
        return 0

    if not diff_output:
        print("[ARRÊT]")
        print("Le candidat est identique au fichier actif.")
        print("Aucun APPLY nécessaire.")
        print("=" * 60)
        return 14

    code, backup_result, error = create_remote_backup(
        target,
        remote_path,
        backup_path,
        original_info["sha256"],
    )

    if code != 0:
        print("[ERREUR BACKUP]")
        print(error)
        print("APPLY annulé.")
        print("=" * 60)
        return code

    print_backup_result(
        backup_path,
        backup_result,
    )

    code, pre_apply, error = verify_before_apply(
        target,
        remote_path,
        backup_path,
        staging_path,
        original_info["sha256"],
    )

    if code != 0:
        print("[ERREUR PRÉ-APPLY]")
        print(error)
        print("APPLY annulé.")
        print("=" * 60)
        return code

    print_final_plan(
        target,
        remote_path,
        original_info,
        pre_apply["active_sha256"],
        pre_apply["candidate_sha256"],
        backup_path,
        backup_result["backup_sha256"],
    )

    print("ATTENTION :")
    print("La prochaine étape modifiera le fichier actif.")
    print("Une authentification sudo interactive sera requise.")
    print()

    confirmation = input(
        "Pour autoriser l'APPLY, tape exactement APPLY : "
    )

    if confirmation != "APPLY":
        print()
        print("[ANNULÉ]")
        print("Confirmation non reçue.")
        print("Le fichier actif n'a pas été modifié.")
        print("=" * 60)
        return 15

    code, confirmed, error = verify_before_apply(
        target,
        remote_path,
        backup_path,
        staging_path,
        original_info["sha256"],
    )

    if code != 0:
        print("[ERREUR PRÉ-APPLY]")
        print(error)
        print("APPLY annulé.")
        print("Le fichier actif n'a pas été modifié.")
        print("=" * 60)
        return code

    plan_active_sha = pre_apply["active_sha256"]
    plan_candidate_sha = pre_apply["candidate_sha256"]

    if confirmed["active_sha256"] != plan_active_sha:
        print("[ERREUR PRÉ-APPLY]")
        print("Le fichier actif a changé depuis le PLAN. APPLY annulé.")
        print("Le fichier actif n'a pas été modifié.")
        print("=" * 60)
        return 30

    if confirmed["candidate_sha256"] != plan_candidate_sha:
        print("[ERREUR PRÉ-APPLY]")
        print("Le candidat a changé depuis le PLAN. APPLY annulé.")
        print("Le fichier actif n'a pas été modifié.")
        print("=" * 60)
        return 30

    print()
    print("[APPLY]")
    print("Demande d'élévation sudo sur le HTD Edge...")

    code = apply_candidate(
        target,
        remote_path,
        staging_path,
        plan_active_sha,
        plan_candidate_sha,
        original_info["uid"],
        original_info["gid"],
        original_info["mode"],
    )

    if code != 0:
        print()
        print("[ERREUR APPLY]")
        print(f"Code de retour : {code}")
        if code in (30, 33, 35):
            print("Écriture non commencée.")
            print("Le fichier actif n'a pas été remplacé.")
        elif code == 39:
            print(
                "Si le terminal distant affiche REMPLACEMENT EFFECTUE, "
                "le fichier actif a été remplacé et la synchronisation "
                "du répertoire a échoué."
            )
        else:
            print("L'état du fichier actif doit être vérifié.")
        print(f"Backup disponible : {backup_path}")
        print("=" * 60)
        return code

    code, final_info, error = get_remote_file_info(
        target,
        remote_path,
    )

    if code != 0:
        print("[ERREUR POST-APPLY]")
        print(error)
        print(f"Backup disponible : {backup_path}")
        print("=" * 60)
        return code

    print()
    print("[POST-APPLY]")
    print(f"SHA avant     : {original_info['sha256']}")
    print(f"SHA candidat  : {candidate_info['sha256']}")
    print(f"SHA actif     : {final_info['sha256']}")
    print(f"Propriétaire  : {final_info['owner']} (UID {final_info['uid']})")
    print(f"Groupe        : {final_info['group']} (GID {final_info['gid']})")
    print(f"Permissions   : {final_info['mode']}")
    print()

    if final_info["sha256"] != candidate_info["sha256"]:
        print("[ERREUR]")
        print("Le fichier actif ne correspond pas au candidat.")
        print(f"Backup disponible : {backup_path}")
        print("=" * 60)
        return 40

    metadata_ok = (
        final_info["uid"] == original_info["uid"]
        and final_info["gid"] == original_info["gid"]
        and final_info["mode"] == original_info["mode"]
    )

    if not metadata_ok:
        print("[ERREUR]")
        print("Les métadonnées du fichier actif ont changé.")
        print(f"Backup disponible : {backup_path}")
        print("=" * 60)
        return 41

    print("[RÉSULTAT]")
    print("APPLY terminé.")
    print("Le contenu actif correspond au candidat.")
    print("UID, GID et permissions sont préservés.")
    print(f"Backup de retour : {backup_path}")
    print()
    print("VALIDATE métier reste à développer.")
    print("ROLLBACK disponible avec --rollback <chemin_backup>.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())