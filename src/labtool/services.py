from .config_builder import build_tunnel_config
from .domain import plan_install
from .domain import LabError






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


def ensure_login(gateway, log=print):
    """Start the interactive login only if cert.pem is missing."""
    if gateway.is_logged_in():
        log("Already logged in.")
        return False
    gateway.login(log)
    return True


def up_tunnel(lab, gateway, runner, log=print):
    """Run the tunnel in the background (no-op if already running)."""
    state = runner.state()
    if state.running:
        log(f"The tunnel is already running (PID {state.pid}).")
        return state

    tunnel = gateway.find(lab.tunnel_name)
    if not tunnel:
        raise LabError(f"The tunnel {lab.tunnel_name} does not exist. First run: labtool init")

    pid = runner.start(lab.tunnel_name)
    log(f"The tunnel is running (PID {pid}). Log: {runner.log_path}")
    return runner.state()


def down_tunnel(runner, log=print):
    """Stop the running tunnel. Returns True if something was stopped."""
    state = runner.state()
    if not state.running:
        log("The tunnel is not running.")
        return False
    runner.stop()
    log(f"The tunnel has been stopped (PID {state.pid}).")
    return True


def tunnel_status(runner):
    """Return the current RunState."""
    return runner.state()


def delete_tunnel(lab, gateway, runner, log=print):
    """Stop the tunnel, then delete it from Cloudflare."""
    tunnel = gateway.find(lab.tunnel_name)
    if not tunnel:
        log(f"Tunnel {lab.tunnel_name} does not exist.")
        return False

    down_tunnel(runner, log)  # a running tunnel cannot be deleted
    gateway.delete(lab.tunnel_name)
    log(f"Tunnel {lab.tunnel_name} has been deleted.")
    return True




def install_cloudflared(detect, installed, run, log=print):
    if installed():
        log("cloudflared is already installed.")
        return False
    commands = plan_install(detect())
    run(commands, log)
    log("cloudflared installed.")
    return True


