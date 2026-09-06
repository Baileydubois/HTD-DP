import os
import re
import shlex
import subprocess
import sys
from datetime import datetime


def validate_target(target):
    pattern = r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.:-]+$"
    return re.fullmatch(pattern, target) is not None


def run_ssh(target, remote_command):
    try:
        result = subprocess.run(
            ["ssh", target, remote_command],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return 1, "", "La commande ssh n'est pas disponible."

    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_remote_file_info(target, remote_path):
    quoted_path = shlex.quote(remote_path)

    command = (
        f"if [ ! -f {quoted_path} ]; then "
        f"echo '__HTD_NOT_FILE__'; exit 2; "
        f"fi; "
        f"stat -c '%s|%U|%G|%a|%y' {quoted_path}; "
        f"sha256sum {quoted_path} | awk '{{print $1}}'"
    )

    code, stdout, stderr = run_ssh(target, command)

    if code != 0:
        return code, None, stderr or stdout

    lines = stdout.splitlines()

    if not lines or lines[0] == "__HTD_NOT_FILE__":
        return 2, None, "Le chemin distant n'est pas un fichier valide."

    if len(lines) < 2:
        return 3, None, "Réponse distante incomplète."

    stat_parts = lines[0].split("|", 4)

    if len(stat_parts) != 5:
        return 4, None, "Format stat distant inattendu."

    size, owner, group, mode, modified = stat_parts
    sha256 = lines[1].strip()

    info = {
        "size": size,
        "owner": owner,
        "group": group,
        "mode": mode,
        "modified": modified,
        "sha256": sha256,
    }

    return 0, info, ""


def build_backup_path(remote_path):
    filename = os.path.basename(remote_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_name = f"{filename}.HTD_BACKUP_{timestamp}"

    return f"/opt/htd/backups/dev_agent/{backup_name}"


def create_remote_backup(target, remote_path, backup_path, expected_sha256):
    quoted_source = shlex.quote(remote_path)
    quoted_backup = shlex.quote(backup_path)
    quoted_expected_sha256 = shlex.quote(expected_sha256)

    command = (
        f"set -e; "
        f"CURRENT_SHA=$(sha256sum {quoted_source} | awk '{{print $1}}'); "
        f"if [ \"$CURRENT_SHA\" != {quoted_expected_sha256} ]; then "
        f"echo '__HTD_SOURCE_CHANGED__'; exit 10; "
        f"fi; "
        f"if [ -e {quoted_backup} ]; then "
        f"echo '__HTD_BACKUP_EXISTS__'; exit 11; "
        f"fi; "
        f"cp -p {quoted_source} {quoted_backup}; "
        f"BACKUP_SHA=$(sha256sum {quoted_backup} | awk '{{print $1}}'); "
        f"echo \"$CURRENT_SHA\"; "
        f"echo \"$BACKUP_SHA\"; "
        f"if [ \"$CURRENT_SHA\" != \"$BACKUP_SHA\" ]; then "
        f"echo '__HTD_BACKUP_MISMATCH__'; exit 12; "
        f"fi"
    )

    code, stdout, stderr = run_ssh(target, command)

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


def print_plan(target, remote_path, info, backup_path):
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
    print(f"Propriétaire : {info['owner']}")
    print(f"Groupe       : {info['group']}")
    print(f"Permissions  : {info['mode']}")
    print(f"Modifié      : {info['modified']}")
    print(f"SHA-256      : {info['sha256']}")
    print()

    print("[PLAN]")
    print("1. Inspecter le contenu nécessaire.")
    print("2. Définir précisément la modification.")
    print("3. Faire approuver la modification.")
    print("4. Créer une sauvegarde ciblée du fichier.")
    print("5. Appliquer la modification contrôlée.")
    print("6. Valider le résultat.")
    print("7. Comparer avant/après et produire un rapport.")
    print("8. Restaurer la sauvegarde si nécessaire.")
    print()

    print("[BACKUP PRÉVU]")
    print(f"Chemin : {backup_path}")
    print()


def print_no_backup_status():
    print("[STATUT]")
    print("Aucune sauvegarde créée.")
    print("Aucune modification effectuée.")
    print("APPLY n'est pas disponible dans cette version.")
    print()
    print("=" * 60)


def print_backup_result(backup_path, result):
    print("[BACKUP]")
    print(f"Créé         : {backup_path}")
    print(f"SHA source   : {result['source_sha256']}")
    print(f"SHA backup   : {result['backup_sha256']}")
    print("Vérification : IDENTIQUE")
    print()

    print("[STATUT]")
    print("Sauvegarde ciblée créée et vérifiée.")
    print("Le fichier actif n'a pas été modifié.")
    print("APPLY n'est pas disponible dans cette version.")
    print()
    print("=" * 60)


def main():
    if len(sys.argv) not in (3, 4):
        print("Usage :")
        print(
            "python prepare_change.py "
            "<utilisateur@adresse> <fichier_distant> [--backup]"
        )
        print()
        print("PLAN seulement :")
        print(
            "python prepare_change.py "
            "hydrotech@192.168.1.124 "
            "/opt/htd/core/config/points.yaml"
        )
        print()
        print("PLAN + BACKUP :")
        print(
            "python prepare_change.py "
            "hydrotech@192.168.1.124 "
            "/opt/htd/core/config/points.yaml --backup"
        )
        return 1

    target = sys.argv[1]
    remote_path = sys.argv[2]
    backup_requested = len(sys.argv) == 4

    if backup_requested and sys.argv[3] != "--backup":
        print("[ERREUR] Option inconnue.")
        print("Option permise : --backup")
        return 1

    if not validate_target(target):
        print("[ERREUR] Cible SSH invalide.")
        print("Format attendu : utilisateur@adresse")
        return 1

    if not remote_path.startswith("/"):
        print("[ERREUR] Le chemin distant doit être absolu.")
        return 1

    code, info, error = get_remote_file_info(
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
        info,
        backup_path,
    )

    if not backup_requested:
        print_no_backup_status()
        return 0

    code, result, error = create_remote_backup(
        target,
        remote_path,
        backup_path,
        info["sha256"],
    )

    if code != 0:
        print("[ERREUR BACKUP]")
        print(error)
        print()
        print("Aucune modification volontaire du fichier actif.")
        print("=" * 60)
        return code

    print_backup_result(
        backup_path,
        result,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())