import ipaddress

import click
import yaml


def load_lab(path):
    with open(path) as f:
        lab = yaml.safe_load(f)
    for node in lab["nodes"]:
        ipaddress.ip_address(node["ip"])
    return lab


@click.group()
def cli():
    """lab tool management"""


@cli.command()
@click.option("--file", "-f", default="lab.yaml")
@click.option("--tunnel-id", required=True)
@click.option("--creds", default="~/.cloudflared/TUNNEL_ID.json")
def render(file, tunnel_id, creds):
    """print tunnel config.yml"""
    lab = load_lab(file)
    ingress = []
    for node in lab["nodes"]:
        ingress.append({
            "hostname": f"{node['name']}.{lab['domain']}",
            "service": f"ssh://{node['ip']}:22",
        })
    ingress.append({"service": "http_status:404"})
    config = {"tunnel": tunnel_id, "credentials-file": creds, "ingress": ingress}
    click.echo(yaml.safe_dump(config, sort_keys=False))


if __name__ == "__main__":
    cli()