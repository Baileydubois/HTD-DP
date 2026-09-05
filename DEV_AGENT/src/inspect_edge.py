import re
import shlex
import subprocess
import sys


REMOTE_SCRIPT = r'''
set -u

EDGE_ROOT="$1"

echo "============================================================"
echo "HTD Dev Agent V1 — HTD Edge Inspection"
echo "============================================================"
echo

echo "[SYSTEM]"
echo "Hostname : $(hostname)"
echo "Date     : $(date)"
echo "Root     : ${EDGE_ROOT}"
echo

if [ ! -d "$EDGE_ROOT" ]; then
    echo "[ERREUR] Le répertoire HTD Edge n'existe pas : $EDGE_ROOT"
    exit 1
fi

echo "[GIT]"
if git -C "$EDGE_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Dépôt Git : OUI"
    echo "Racine Git : $(git -C "$EDGE_ROOT" rev-parse --show-toplevel 2>/dev/null)"
    echo "Branche    : $(git -C "$EDGE_ROOT" branch --show-current 2>/dev/null)"
    echo
    echo "État Git :"
    STATUS="$(git -C "$EDGE_ROOT" status --short 2>/dev/null)"
    if [ -n "$STATUS" ]; then
        printf '%s\n' "$STATUS"
    else
        echo "Working tree clean"
    fi
else
    echo "Dépôt Git : NON"
fi

echo
echo "[STRUCTURE HTD]"
find "$EDGE_ROOT" \
    -maxdepth 3 \
    -type f \
    ! -path '*/.git/*' \
    ! -path '*/venv/*' \
    ! -path '*/.venv/*' \
    ! -path '*/__pycache__/*' \
    ! -path '*/backups/*' \
    ! -path '*/*.BAK_*/*' \
    ! -path '*/*.bak_*/*' \
    ! -path '*/*.BACKUP_*/*' \
    ! -name '*.pyc' \
    ! -name '*.BAK_*' \
    ! -name '*.bak_*' \
    ! -name '*.BACKUP_*' \
    ! -name '*.save' \
    ! -name '*.BEFORE_*' \
    ! -name '*.VALIDATED' \
    ! -name '*_VALIDATED' \
    | sort

echo
echo "[SERVICES HTD PRÉSENTS]"
systemctl list-unit-files \
    --type=service \
    --no-pager 2>/dev/null \
    | grep -i '^htd-' \
    || echo "Aucun service HTD trouvé."

echo
echo "[SERVICES HTD — ÉTAT ACTUEL]"
systemctl \
    --no-pager \
    --type=service \
    --all 2>/dev/null \
    | grep -i 'htd-' \
    || echo "Aucun service HTD trouvé."

echo
echo "[TIMERS HTD — ÉTAT ACTUEL]"
systemctl \
    --no-pager \
    --type=timer \
    --all 2>/dev/null \
    | grep -i 'htd-' \
    || echo "Aucun timer HTD trouvé."

echo
echo "============================================================"
echo "Inspection terminée — aucune modification effectuée."
echo "============================================================"
'''


def validate_target(target):
    pattern = r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.:-]+$"
    return re.fullmatch(pattern, target) is not None


def inspect_edge(target, edge_root):
    if not validate_target(target):
        print("[ERREUR] Cible SSH invalide.")
        print("Format attendu : utilisateur@adresse")
        return 1

    quoted_root = shlex.quote(edge_root)

    command = [
        "ssh",
        target,
        "bash",
        "-s",
        "--",
        quoted_root,
    ]

    print(f"Connexion à : {target}")
    print(f"HTD Edge    : {edge_root}")
    print()

    try:

        remote_script = (
            REMOTE_SCRIPT
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .encode("utf-8")
        )

        result = subprocess.run(
            command,
            input=remote_script,
            check=False,
        )

    except FileNotFoundError:
        print("[ERREUR] La commande ssh n'est pas disponible.")
        return 1
    except KeyboardInterrupt:
        print()
        print("[ANNULÉ] Inspection interrompue par l'utilisateur.")
        return 130

    if result.returncode != 0:
        print()
        print(
            f"[ERREUR] L'inspection distante s'est terminée "
            f"avec le code {result.returncode}."
        )
        return result.returncode

    return 0


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage :")
        print(
            "python inspect_edge.py "
            "<utilisateur@adresse> [chemin_htd]"
        )
        print()
        print("Exemple :")
        print(
            "python inspect_edge.py "
            "hydrotech@192.168.1.124 /opt/htd"
        )
        return 1

    target = sys.argv[1]

    if len(sys.argv) == 3:
        edge_root = sys.argv[2]
    else:
        edge_root = "/opt/htd"

    return inspect_edge(target, edge_root)


if __name__ == "__main__":
    sys.exit(main())