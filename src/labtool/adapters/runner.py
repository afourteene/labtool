import os
import signal
import subprocess
import time
from pathlib import Path

from ..domain import LabError, RunState

STATE_DIR = Path.home() / ".labtool"


class ProcessRunner:
    """Runs cloudflared in the background and tracks it via a PID file."""

    def __init__(self, state_dir=STATE_DIR):
        self.dir = Path(state_dir)
        self.pid_file = self.dir / "tunnel.pid"
        self.log_path = self.dir / "tunnel.log"

    def _read_pid(self):
        try:
            return int(self.pid_file.read_text())
        except (FileNotFoundError, ValueError):
            return None

    def _alive(self, pid):
        """Signal 0 sends nothing; it only checks that the process exists."""
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True  # exists, but owned by another user

    def state(self):
        """A stale PID file (dead process) counts as not running."""
        pid = self._read_pid()
        if pid and self._alive(pid):
            return RunState(True, pid)
        return RunState(False)

    def start(self, tunnel_name):
        self.dir.mkdir(parents=True, exist_ok=True)
        log = open(self.log_path, "ab")
        proc = subprocess.Popen(
            ["cloudflared", "tunnel", "run", tunnel_name],
            stdout=log, stderr=log,
            start_new_session=True,  # detach so it survives closing the terminal/SSH
        )
        self.pid_file.write_text(str(proc.pid))
        time.sleep(1)  # if it dies immediately, report it instead of hiding it
        if proc.poll() is not None:
            self.pid_file.unlink(missing_ok=True)
            raise LabError(f"cloudflared exited immediately. Log: {self.log_path}")
        return proc.pid

    def stop(self):
        """Send SIGTERM and wait up to 5 seconds for a clean exit."""
        pid = self._read_pid()
        if pid and self._alive(pid):
            os.kill(pid, signal.SIGTERM)
            for _ in range(50):
                if not self._alive(pid):
                    break
                time.sleep(0.1)
        self.pid_file.unlink(missing_ok=True)