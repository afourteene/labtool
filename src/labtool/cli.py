import click

from labtool.adapters.cloudflared import CloudflaredGateway, YamlConfigStore
from labtool.adapters.lab_file import load_lab
from labtool.domain import LabError
from labtool.services import ensure_login, init_tunnel
from labtool.adapters import system
from labtool.services import install_cloudflared





@click.group()
def cli():
    """Cloudflare Tunnel management."""
    
@cli.command()
def login():
    """Logs in to Cloudflare (creates cert.pem)."""
    try:
        ensure_login(CloudflaredGateway(), log=click.echo)
    except LabError as e:
        raise click.ClickException(str(e))
@cli.command()
def install():
    """Installs cloudflared on this system."""
    try:
        install_cloudflared(system.detect_platform, system.is_installed,
                            system.run_commands, log=click.echo)
    except LabError as e:
        raise click.ClickException(str(e))
    
    
@cli.command()
@click.option("-f", "--file", default="lab.yaml")
def init(file):
    """Initializes the tunnel, DNS, and config.yml."""
    try:
        lab = load_lab(file)
        init_tunnel(lab, CloudflaredGateway(), YamlConfigStore(), log=click.echo)
    except LabError as e:
        raise click.ClickException(str(e))