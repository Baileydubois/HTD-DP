import os
import re
import shlex
import subprocess
import sys
from datetime import datetime


BACKUP_ROOT = "/opt/htd/backups/dev_agent"
STAGING_ROOT = f"{BACKUP_ROOT}/staging"


def validate_target(target):
    pattern = r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.:-]+$"
    return re.fullmatch(pattern, target) is not None


def run_ssh(target, remote_command):
    try:
        result = subprocess.run(
            ["ssh", target, remote_command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
)
    except FileNotFoundError:
        return 1, "", "La commande ssh n'est pas disponible."

    return result.returncode, result.stdout.strip(), result.stderr.strip()


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
    quoted_path = shlex.quote(remote_path)

    command = (
        f"if [ ! -f {quoted_path} ]; then "
        f"echo '__HTD_NOT_FILE__'; exit 2; "
        f"fi; "
        f"stat -c '%s|%U|%G|%u|%g|%a|%y' {quoted_path}; "
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

    stat_parts = lines[0].split("|", 6)

    if len(stat_parts) != 7:
        return 4, None, "Format stat distant inattendu."

    size, owner, group, uid, gid, mode, modified = stat_parts
    sha256 = lines[1].strip()

    info = {
        "size": size,
        "owner": owner,
        "group": group,
        "uid": uid,
        "gid": gid,
        "mode": mode,
        "modified": modified,
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
    quoted_source = shlex.quote(remote_path)
    quoted_backup = shlex.quote(backup_path)
    quoted_expected = shlex.quote(expected_sha256)

    command = (
        f"set -e; "
        f"CURRENT_SHA=$(sha256sum {quoted_source} | awk '{{print $1}}'); "
        f"if [ \"$CURRENT_SHA\" != {quoted_expected} ]; then "
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


def stage_candidate(target, local_candidate, remote_staging_path):
    if not os.path.isfile(local_candidate):
        return (
            20,
            None,
            "Le fichier candidat local n'existe pas.",
        )

    quoted_staging_root = shlex.quote(STAGING_ROOT)

    code, stdout, stderr = run_ssh(
        target,
        f"mkdir -p {quoted_staging_root}",
    )

    if code != 0:
        return (
            code,
            None,
            stderr or stdout or "Impossible de créer la zone staging.",
        )

    code, error = run_scp(
        local_candidate,
        target,
        remote_staging_path,
    )

    if code != 0:
        return code, None, error

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

    quoted_candidate = shlex.quote(candidate_path)

    python_code = (
        "import sys, yaml; "
        "yaml.safe_load(open(sys.argv[1], encoding='utf-8'))"
    )

    command = (
        f"python3 -c {shlex.quote(python_code)} "
        f"{quoted_candidate}"
    )

    code, stdout, stderr = run_ssh(
        target,
        command,
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


def verify_before_apply(
    target,
    active_path,
    backup_path,
    candidate_path,
    expected_active_sha,
):
    quoted_active = shlex.quote(active_path)
    quoted_backup = shlex.quote(backup_path)
    quoted_candidate = shlex.quote(candidate_path)
    quoted_expected = shlex.quote(expected_active_sha)

    command = (
        f"set -e; "
        f"test -f {quoted_active}; "
        f"test -f {quoted_backup}; "
        f"test -f {quoted_candidate}; "
        f"ACTIVE_SHA=$(sha256sum {quoted_active} | awk '{{print $1}}'); "
        f"BACKUP_SHA=$(sha256sum {quoted_backup} | awk '{{print $1}}'); "
        f"if [ \"$ACTIVE_SHA\" != {quoted_expected} ]; then "
        f"echo '__HTD_ACTIVE_CHANGED__'; exit 30; "
        f"fi; "
        f"if [ \"$ACTIVE_SHA\" != \"$BACKUP_SHA\" ]; then "
        f"echo '__HTD_BACKUP_INVALID__'; exit 31; "
        f"fi; "
        f"echo \"$ACTIVE_SHA\"; "
        f"sha256sum {quoted_candidate} | awk '{{print $1}}'"
    )

    code, stdout, stderr = run_ssh(target, command)
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
):
    quoted_active = shlex.quote(active_path)
    quoted_candidate = shlex.quote(candidate_path)

    command = (
        "sudo sh -c "
        + shlex.quote(
            f"cat {quoted_candidate} > {quoted_active}"
        )
    )

    return run_interactive_ssh(
        target,
        command,
    )


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
    print(f"Propriétaire : {info['owner']} (UID {info['uid']})")
    print(f"Groupe       : {info['group']} (GID {info['gid']})")
    print(f"Permissions  : {info['mode']}")
    print(f"Modifié      : {info['modified']}")
    print(f"SHA-256      : {info['sha256']}")
    print()

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

    if not remote_path.startswith("/"):
        print("[ERREUR] Le chemin distant doit être absolu.")
        return 1

    mode = "plan"
    local_candidate = None

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
        else:
            print("[ERREUR] Option inconnue.")
            print_usage()
            return 1

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
        return 0

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

    print("[PRÉ-APPLY]")
    print(f"SHA actif     : {pre_apply['active_sha256']}")
    print(f"SHA candidat  : {pre_apply['candidate_sha256']}")
    print(f"Backup        : {backup_path}")
    print()

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
        return 0

    print()
    print("[APPLY]")
    print("Demande d'élévation sudo sur le HTD Edge...")

    code = apply_candidate(
        target,
        remote_path,
        staging_path,
    )

    if code != 0:
        print()
        print("[ERREUR APPLY]")
        print(f"Code de retour : {code}")
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
    print("VALIDATE métier et ROLLBACK restent à développer.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())