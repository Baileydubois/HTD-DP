import re
import shlex
import subprocess
import sys


SERVICES = [
    "htd-machine-logic.service",
    "htd-machine-layer.service",
    "htd-runtime.service",
    "htd-runtime-bridge.service",
    "htd-do-apply.service",
]


REMOTE_SCRIPT = r'''
set -u

EDGE_ROOT="$1"

SERVICES="
htd-machine-logic.service
htd-machine-layer.service
htd-runtime.service
htd-runtime-bridge.service
htd-do-apply.service
"

SCRIPTS="
$EDGE_ROOT/core/runtime/machine_logic.py
$EDGE_ROOT/core/runtime/machine_layer.py
$EDGE_ROOT/core/runtime/runtime_loop.py
$EDGE_ROOT/core/output/runtime_bridge.py
$EDGE_ROOT/core/output/apply_do.py
"

CONFIG_FILES="
$EDGE_ROOT/core/config/machine_definition.yaml
$EDGE_ROOT/core/config/machine_mapping.yaml
$EDGE_ROOT/core/config/output_map.yaml
$EDGE_ROOT/core/config/physical_output_map.yaml
"

STATE_FILES="
$EDGE_ROOT/core/state/machine_commands.json
$EDGE_ROOT/core/state/machine_resolved_outputs.json
$EDGE_ROOT/data/state/runtime_outputs.json
$EDGE_ROOT/data/state/physical_outputs.json
$EDGE_ROOT/data/state/do_apply_state.json
"

echo "============================================================"
echo "HTD Dev Agent V1 — Output Chain Inspection"
echo "============================================================"
echo

echo "[SYSTEM]"
echo "Hostname : $(hostname)"
echo "Date     : $(date)"
echo "Root     : $EDGE_ROOT"
echo

if [ ! -d "$EDGE_ROOT" ]; then
    echo "[ERREUR]"
    echo "Répertoire HTD introuvable : $EDGE_ROOT"
    exit 1
fi

echo "[MODE]"
echo "Inspection lecture seule."
echo "Aucun service ne sera redémarré."
echo "Aucun fichier ne sera modifié."
echo "Aucune sortie physique ne sera actionnée."
echo

echo "============================================================"
echo "[1 — SERVICES DE LA CHAÎNE]"
echo "============================================================"
echo

for SERVICE in $SERVICES; do
    echo "------------------------------------------------------------"
    echo "SERVICE : $SERVICE"
    echo "------------------------------------------------------------"

    systemctl show "$SERVICE" \
        -p Id \
        -p LoadState \
        -p ActiveState \
        -p SubState \
        -p ExecStart \
        -p Environment \
        --no-pager 2>/dev/null \
        || echo "[ERREUR] Impossible de lire $SERVICE"

    echo
done

echo "============================================================"
echo "[2 — SCRIPTS EXÉCUTÉS]"
echo "============================================================"
echo

for SCRIPT in $SCRIPTS; do
    if [ -f "$SCRIPT" ]; then
        echo "$SCRIPT"
    else
        echo "[ABSENT] $SCRIPT"
    fi
done

echo
echo "============================================================"
echo "[3 — RÉFÉRENCES DÉTECTÉES DANS LE CODE]"
echo "============================================================"
echo

for SCRIPT in $SCRIPTS; do
    echo "------------------------------------------------------------"
    echo "SCRIPT : $SCRIPT"
    echo "------------------------------------------------------------"

    if [ ! -f "$SCRIPT" ]; then
        echo "[ABSENT]"
        echo
        continue
    fi

    grep -nE \
        '(/opt/htd/|\.json|\.yaml|legacy|fallback|HTD_|HR30|REG_OUTPUTS|machine_commands|machine_resolved_outputs|runtime_outputs|physical_outputs|write_json|read_json|load_)' \
        "$SCRIPT" \
        2>/dev/null \
        || echo "Aucune référence ciblée détectée."

    echo
done

echo "============================================================"
echo "[4 — CONFIGURATIONS DE SORTIES]"
echo "============================================================"
echo

for CFG in $CONFIG_FILES; do
    echo "------------------------------------------------------------"
    echo "CONFIG : $CFG"
    echo "------------------------------------------------------------"

    if [ -f "$CFG" ]; then
        cat "$CFG"
    else
        echo "[ABSENT]"
    fi

    echo
done

echo "============================================================"
echo "[5 — ÉTATS JSON COURANTS]"
echo "============================================================"
echo

for STATE in $STATE_FILES; do
    echo "------------------------------------------------------------"
    echo "STATE : $STATE"
    echo "------------------------------------------------------------"

    if [ ! -f "$STATE" ]; then
        echo "[ABSENT]"
        echo
        continue
    fi

    echo "Métadonnées :"
    stat \
        --printf='size=%s bytes | owner=%U | group=%G | mode=%a | modified=%y\n' \
        "$STATE" \
        2>/dev/null \
        || true

    echo
    echo "Contenu :"

    if python3 -m json.tool "$STATE" 2>/dev/null; then
        :
    else
        echo "[AVERTISSEMENT] JSON non parsable — contenu brut :"
        cat "$STATE"
    fi

    echo
done

echo "============================================================"
echo "[6 — PRODUCTEURS / CONSOMMATEURS DÉTECTÉS]"
echo "============================================================"
echo

for STATE in $STATE_FILES; do
    BASENAME="$(basename "$STATE")"

    echo "------------------------------------------------------------"
    echo "FICHIER : $BASENAME"
    echo "------------------------------------------------------------"

    grep -nH \
        "$BASENAME" \
        $SCRIPTS \
        2>/dev/null \
        || echo "Aucune référence trouvée dans les scripts ciblés."

    echo
done

echo "============================================================"
echo "[7 — LEGACY / FALLBACK]"
echo "============================================================"
echo

echo "[runtime_loop.py]"
grep -nE \
    'legacy_do_cmd|legacy_do_index|fallback|output_interlocks|forced_by_permissive' \
    "$EDGE_ROOT/core/runtime/runtime_loop.py" \
    2>/dev/null \
    || echo "Aucun chemin legacy/fallback détecté."

echo

echo "[runtime_bridge.py]"
grep -nE \
    'STRICT_NAMED|strict_named|legacy|fallback|source_used' \
    "$EDGE_ROOT/core/output/runtime_bridge.py" \
    2>/dev/null \
    || echo "Aucun chemin legacy/fallback détecté."

echo

echo "[physical_outputs.json]"
if [ -f "$EDGE_ROOT/data/state/physical_outputs.json" ]; then
    grep -oE \
        '"legacy_fallback_active"[[:space:]]*:[[:space:]]*(true|false)' \
        "$EDGE_ROOT/data/state/physical_outputs.json" \
        2>/dev/null \
        || echo "legacy_fallback_active non trouvé."
else
    echo "[ABSENT]"
fi

echo

echo "[Service runtime bridge]"
systemctl show \
    htd-runtime-bridge.service \
    -p Environment \
    --no-pager 2>/dev/null

echo

echo "============================================================"
echo "[8 — SORTIE PHYSIQUE FINALE]"
echo "============================================================"
echo

echo "Service : htd-do-apply.service"

systemctl show \
    htd-do-apply.service \
    -p ActiveState \
    -p SubState \
    -p Environment \
    --no-pager 2>/dev/null

echo

echo "Références matérielles dans apply_do.py :"

grep -nE \
    'DO_HOST|DO_PORT|DO_DEVICE_ID|DO_REG_OUTPUTS|DO_BIT_|DRY_RUN|HR30|write_hr_word|read_hr_word' \
    "$EDGE_ROOT/core/output/apply_do.py" \
    2>/dev/null \
    || echo "Aucune référence matérielle détectée."

echo

echo "============================================================"
echo "[9 — RÉSUMÉ DE LA CHAÎNE INSPECTÉE]"
echo "============================================================"
echo

echo "Les sections précédentes contiennent les preuves observées"
echo "pour les services, scripts, configurations et états."
echo
echo "Séquence ciblée par cette inspection :"
echo
echo "machine_logic.py"
echo "  -> machine_commands.json"
echo "  -> machine_layer.py"
echo "  -> machine_resolved_outputs.json"
echo "  -> runtime_loop.py"
echo "  -> runtime_outputs.json"
echo "  -> runtime_bridge.py"
echo "  -> physical_outputs.json"
echo "  -> apply_do.py"
echo "  -> sortie matérielle configurée"
echo
echo "IMPORTANT : cette séquence décrit la portée de l'inspection."
echo "Les sections [1] à [8] constituent les preuves de l'état réel."
echo

echo "============================================================"
echo "[FIN]"
echo "============================================================"
echo
echo "Inspection terminée."
echo "Aucune modification effectuée sur le HTD Edge."
echo "============================================================"
'''


def validate_target(target):
    pattern = r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.:-]+$"
    return re.fullmatch(pattern, target) is not None


def inspect_output_chain(target, edge_root):
    if not validate_target(target):
        print("[ERREUR] Cible SSH invalide.")
        print("Format attendu : utilisateur@adresse")
        return 1

    if not edge_root.startswith("/"):
        print("[ERREUR] Le chemin HTD Edge doit être absolu.")
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
    print("Inspection de la chaîne de sorties en lecture seule.")
    print()

    remote_script = (
        REMOTE_SCRIPT
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .encode("utf-8")
    )

    try:
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
            "[ERREUR] L'inspection distante s'est terminée "
            f"avec le code {result.returncode}."
        )
        return result.returncode

    return 0


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage :")
        print(
            "python inspect_output_chain.py "
            "<utilisateur@adresse> [chemin_htd]"
        )
        print()
        print("Exemple :")
        print(
            "python inspect_output_chain.py "
            "hydrotech@192.168.1.124 /opt/htd"
        )
        return 1

    target = sys.argv[1]

    if len(sys.argv) == 3:
        edge_root = sys.argv[2]
    else:
        edge_root = "/opt/htd"

    return inspect_output_chain(
        target,
        edge_root,
    )


if __name__ == "__main__":
    sys.exit(main())