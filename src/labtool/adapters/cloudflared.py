import json
import subprocess
from pathlib import Path

import yaml

from ..domain import LabError, Tunnel

CF_DIR = Path.home() / ".cloudflared"


def _run(cmd):
    """Run a command; raise LabError with stderr on failure."""
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise LabError(f"{' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout


class CloudflaredGateway:
    """Talks to Cloudflare through the cloudflared binary."""

    def find(self, name):
        """Return the Tunnel with this name, or None."""
        out = _run(["cloudflared", "tunnel", "list", "--output", "json"])
        for t in json.loads(out) or []:
            if t["name"] == name:
                return Tunnel(id=t["id"], name=t["name"])
        return None

    def create(self, name):
        _run(["cloudflared", "tunnel", "create", name])
        return self.find(name)

    def route_dns(self, tunnel_name, hostname):
        """Create or overwrite the CNAME record for hostname."""
        _run(["cloudflared", "tunnel", "route", "dns",
              "--overwrite-dns", tunnel_name, hostname])

    def delete(self, name):
        """Delete the tunnel; -f also cleans up stale connections."""
        _run(["cloudflared", "tunnel", "delete", "-f", name])

    def credentials_path(self, tunnel):
        return str(CF_DIR / f"{tunnel.id}.json")

    def is_logged_in(self):
        """cert.pem exists only after `cloudflared tunnel login`."""
        return (CF_DIR / "cert.pem").exists()

    def login(self, log=print):
        """Run the interactive login; the URL prints straight to the terminal."""
        log("Open the displayed URL in your browser and click Authorize...")
        r = subprocess.run(["cloudflared", "tunnel", "login"])
        if r.returncode != 0:
            raise LabError("Login failed.")


class YamlConfigStore:
    """Writes the cloudflared config.yml file."""

    def __init__(self, path=CF_DIR / "config.yml"):
        self.path = path

    def save(self, config):
        # sort_keys=False: ingress order matters to cloudflared
        self.path.write_text(yaml.safe_dump(config, sort_keys=False))