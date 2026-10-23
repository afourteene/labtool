import ipaddress
from dataclasses import dataclass


class LabError(Exception):
    """A user-facing error."""


@dataclass(frozen=True)
class Node:
    name: str
    ip: str
    port: int = 22

    def __post_init__(self):
        ipaddress.ip_address(self.ip)  # An invalid IP triggers an error here.

    @property
    def service(self):
        return f"ssh://{self.ip}:{self.port}"


@dataclass(frozen=True)
class Lab:
    domain: str
    tunnel_name: str
    nodes: tuple

    def __post_init__(self):
        names = [n.name for n in self.nodes]
        if len(names) != len(set(names)):
            raise LabError("The node names are duplicated.")

    def hostname(self, node):
        return f"{node.name}.{self.domain}"


@dataclass(frozen=True)
class Tunnel:
    id: str
    name: str
    
@dataclass(frozen=True)
class Platform:
    system: str   # "darwin" | "linux" | "windows"
    arch: str     # "amd64" | "arm64"
    has_apt: bool = False
    has_brew: bool = False

@dataclass(frozen=True)
class RunState:
    """Whether the tunnel process is running, and its PID if so."""
    running: bool
    pid: int | None = None
    
    
def plan_install(p):
    """List of commands required to install cloudflared on this platform."""
    if p.system == "darwin":
        if not p.has_brew:
            raise LabError("brew is required to install cloudflared on macOS")
        return [["brew", "install", "cloudflared"]]

    if p.system == "linux":
        url = ("https://github.com/cloudflare/cloudflared/releases/latest/download/"
               f"cloudflared-linux-{p.arch}")
        if p.has_apt:
            return [
                ["curl", "-fsSL", "-o", "/tmp/cloudflared.deb", url + ".deb"],
                ["sudo", "dpkg", "-i", "/tmp/cloudflared.deb"],
            ]
        return [
            ["curl", "-fsSL", "-o", "/tmp/cloudflared", url],
            ["sudo", "install", "/tmp/cloudflared", "/usr/local/bin/cloudflared"],
        ]

    if p.system == "windows":
        return [["winget", "install", "--id", "Cloudflare.cloudflared", "-e"]]

    raise LabError(f"Unsupported operating system: {p.system}")