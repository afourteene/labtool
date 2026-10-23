import json
import yaml
import subprocess
from pathlib import Path

from ..domain import LabError, Tunnel

CF_DIR = Path.home() / ".cloudflared"


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise LabError(f"{' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout


class CloudflaredGateway:
    
    def find(self, name):
        out = _run(["cloudflared", "tunnel", "list", "--output", "json"])
        for t in json.loads(out) or []:
            if t["name"] == name:
                return Tunnel(id=t["id"], name=t["name"])
        return None

    def create(self, name):
        
        _run(["cloudflared", "tunnel", "create", name])
        return self.find(name)

    def route_dns(self, tunnel_name, hostname):
        
        _run(["cloudflared", "tunnel", "route", "dns",
              "--overwrite-dns", tunnel_name, hostname])

    def credentials_path(self, tunnel):
        return str(CF_DIR / f"{tunnel.id}.json")


class YamlConfigStore:
    
    def __init__(self, path=CF_DIR / "config.yml"):
        self.path = path

    def save(self, config):
        self.path.write_text(yaml.safe_dump(config, sort_keys=False))
        
        
def login(self, log=print):
    
    """Runs cloudflared tunnel login and displays the output (URL) in real time."""
    log("Open the displayed URL in your browser and click Authorize...")
    r = subprocess.run(["cloudflared", "tunnel", "login"])
    if r.returncode != 0:
        raise LabError("Login failed.")

def is_logged_in(self):
    return (CF_DIR / "cert.pem").exists()