from .config_builder import build_tunnel_config
from .domain import plan_install





def init_tunnel(lab, gateway, store, log=print):
    ensure_login(gateway, log)
    tunnel = gateway.find(lab.tunnel_name)
    if tunnel:
        log(f"tunnel {lab.tunnel_name} already exists.")
    else:
        tunnel = gateway.create(lab.tunnel_name)
        log(f"tunnel {lab.tunnel_name} created.")

    for node in lab.nodes:
        host = lab.hostname(node)
        gateway.route_dns(lab.tunnel_name, host)
        log(f"DNS: {host}")

    config = build_tunnel_config(lab, tunnel, gateway.credentials_path(tunnel))
    store.save(config)
    return tunnel





def install_cloudflared(detect, installed, run, log=print):
    if installed():
        log("cloudflared is already installed.")
        return False
    commands = plan_install(detect())
    run(commands, log)
    log("cloudflared installed.")
    return True

def ensure_login(gateway, log=print):
    if gateway.is_logged_in():
        log("Already logged in.")
        return False
    gateway.login(log)
    return True