import os
import sys


DEFAULT_IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
}


def scan_tree(root_path, max_depth=3):
    root_path = os.path.abspath(root_path)

    print("=" * 60)
    print("HTD Dev Agent V1 — Repository Tree Scan")
    print("=" * 60)
    print(f"Chemin : {root_path}")
    print(f"Profondeur maximale : {max_depth}")
    print()

    if not os.path.exists(root_path):
        print("[ERREUR] Le chemin n'existe pas.")
        return 1

    if not os.path.isdir(root_path):
        print("[ERREUR] Le chemin n'est pas un dossier.")
        return 1

    print(os.path.basename(root_path) + os.sep)

    walk_directory(
        current_path=root_path,
        prefix="",
        current_depth=0,
        max_depth=max_depth,
    )

    return 0


def walk_directory(current_path, prefix, current_depth, max_depth):
    if current_depth >= max_depth:
        return

    try:
        entries = sorted(
            os.listdir(current_path),
            key=lambda name: (
                not os.path.isdir(os.path.join(current_path, name)),
                name.lower(),
            ),
        )
    except OSError as error:
        print(f"{prefix}[ERREUR] Impossible de lire : {error}")
        return

    entries = [
        entry
        for entry in entries
        if entry not in DEFAULT_IGNORED_DIRS
    ]

    for index, entry in enumerate(entries):
        full_path = os.path.join(current_path, entry)
        is_last = index == len(entries) - 1

        connector = "└── " if is_last else "├── "
        child_prefix = "    " if is_last else "│   "

        if os.path.isdir(full_path):
            print(f"{prefix}{connector}{entry}{os.sep}")

            walk_directory(
                current_path=full_path,
                prefix=prefix + child_prefix,
                current_depth=current_depth + 1,
                max_depth=max_depth,
            )
        else:
            print(f"{prefix}{connector}{entry}")


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage :")
        print("python scan_tree.py <chemin_du_depot> [profondeur]")
        return 1

    root_path = sys.argv[1]

    if len(sys.argv) == 3:
        try:
            max_depth = int(sys.argv[2])
        except ValueError:
            print("[ERREUR] La profondeur doit être un nombre entier.")
            return 1

        if max_depth < 1:
            print("[ERREUR] La profondeur doit être au minimum 1.")
            return 1
    else:
        max_depth = 3

    return scan_tree(root_path, max_depth)


if __name__ == "__main__":
    sys.exit(main())