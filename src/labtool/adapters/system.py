import platform
import shutil
import subprocess

from ..domain import LabError, Platform


def detect_platform():
    system = platform.system().lower()          # darwin | linux | windows
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "amd64"
    return Platform(
        system=system,
        arch=arch,
        has_apt=shutil.which("apt-get") is not None,
        has_brew=shutil.which("brew") is not None,
    )


def is_installed():
    return shutil.which("cloudflared") is not None


def run_commands(commands, log=print):
    for cmd in commands:
        log("$ " + " ".join(cmd))
        r = subprocess.run(cmd)
        if r.returncode != 0:
            raise LabError(f"دستور شکست خورد: {' '.join(cmd)}")