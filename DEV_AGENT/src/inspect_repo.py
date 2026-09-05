import os
import subprocess
import sys


def run_git_command(repo_path, args):
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, *args],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return 1, "", "Git n'est pas installé ou n'est pas accessible dans le PATH."


def inspect_repository(repo_path):
    repo_path = os.path.abspath(repo_path)

    print("=" * 60)
    print("HTD Dev Agent V1 — Repository Inspection")
    print("=" * 60)
    print(f"Chemin demandé : {repo_path}")
    print()

    if not os.path.exists(repo_path):
        print("[ERREUR] Le chemin n'existe pas.")
        return 1

    if not os.path.isdir(repo_path):
        print("[ERREUR] Le chemin n'est pas un dossier.")
        return 1

    code, git_root, error = run_git_command(
        repo_path,
        ["rev-parse", "--show-toplevel"],
    )

    if code != 0:
        print("Dépôt Git : NON")
        if error:
            print(f"Détail : {error}")
        print()
        print("Contenu de premier niveau :")
        list_top_level(repo_path)
        return 0

    print("Dépôt Git : OUI")
    print(f"Racine Git : {git_root}")

    code, branch, error = run_git_command(
        repo_path,
        ["branch", "--show-current"],
    )

    if code == 0 and branch:
        print(f"Branche courante : {branch}")
    else:
        print("Branche courante : inconnue")
        if error:
            print(f"Détail : {error}")

    code, status, error = run_git_command(
        repo_path,
        ["status", "--short"],
    )

    print()
    print("État Git :")

    if code != 0:
        print("[ERREUR] Impossible de lire l'état Git.")
        if error:
            print(error)
    elif status:
        print(status)
    else:
        print("Working tree clean")

    print()
    print("Contenu de premier niveau :")
    list_top_level(git_root)

    return 0


def list_top_level(path):
    try:
        entries = sorted(os.listdir(path))
    except OSError as error:
        print(f"[ERREUR] Impossible de lire le dossier : {error}")
        return

    if not entries:
        print("(dossier vide)")
        return

    for entry in entries:
        full_path = os.path.join(path, entry)

        if os.path.isdir(full_path):
            print(f"[DIR]  {entry}")
        else:
            print(f"[FILE] {entry}")


def main():
    if len(sys.argv) != 2:
        print("Usage :")
        print("python inspect_repo.py <chemin_du_depot>")
        return 1

    return inspect_repository(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())