"""Vérifie la restriction temporaire du fichier actif. Aucun SSH."""

import subprocess
import sys

import prepare_change as pc

ALLOWED = "/var/tmp/htd-deployment-v1-trial/htd_essai_isole.txt"
FORBIDDEN = [
    "/opt/htd/config.yaml",
    "/opt/htd",
    "/etc/passwd",
    "/usr/bin/python3",
    "/home/hydrotech/htd_essai_isole.txt",
    "/var/tmp/autre.txt",
    "/var/tmp/htd-deployment-v1-trial-evil/htd_essai_isole.txt",
    "/var/tmp/htd-deployment-v1-trial2/htd_essai_isole.txt",
    "/var/tmp/htd-deployment-v1-trial",
    "/var/tmp/htd-deployment-v1-trial/",
    "/var/tmp/htd-deployment-v1-trial/sous/htd_essai_isole.txt",
    "/var/tmp/htd-deployment-v1-trial/../tmp/htd_essai_isole.txt",
    "/VAR/tmp/htd-deployment-v1-trial/htd_essai_isole.txt",
]


def test_allowed():
    assert pc.trial_active_path_allowed(ALLOWED) is True
    assert pc.active_path_problem(ALLOWED) is None


def test_forbidden_components():
    for path in FORBIDDEN:
        assert pc.trial_active_path_allowed(path) is False, path
        problem = pc.active_path_problem(path)
        assert problem is not None and problem[0] == 33, path


def test_main_refuses_before_ssh():
    calls = []

    def forbid_run(*args, **kwargs):
        calls.append(args)
        raise AssertionError("SSH invoqué")

    original = subprocess.run
    subprocess.run = forbid_run
    previous = sys.argv
    try:
        for option in (None, "--backup", "--apply", "--rollback"):
            for path in (
                "/opt/htd/config.yaml",
                "/etc/passwd",
                "/home/hydrotech/x",
                "/var/tmp/htd-deployment-v1-trial-evil/x",
            ):
                if option is None:
                    sys.argv = ["prepare_change.py", "hydrotech@192.168.1.124", path]
                elif option == "--backup":
                    sys.argv = [
                        "prepare_change.py",
                        "hydrotech@192.168.1.124",
                        path,
                        "--backup",
                    ]
                else:
                    extra = (
                        "/opt/htd/backups/dev_agent/backup.txt"
                        if option == "--rollback"
                        else r"C:\Users\Usitech HD\AppData\Local\Temp\htd_essai_isole_candidat.txt"
                    )
                    sys.argv = [
                        "prepare_change.py",
                        "hydrotech@192.168.1.124",
                        path,
                        option,
                        extra,
                    ]
                code = pc.main()
                assert code == 33, (option, path, code)
                assert calls == []
    finally:
        subprocess.run = original
        sys.argv = previous


def main():
    test_allowed()
    test_forbidden_components()
    test_main_refuses_before_ssh()
    print("TRIAL_SCOPE_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
