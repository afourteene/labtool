import click


def success(msg):
    click.echo(click.style("✔ ", fg="green", bold=True) + msg)


def info(msg):
    click.echo(click.style("ℹ ", fg="cyan") + msg)


def warn(msg):
    click.echo(click.style("! ", fg="yellow", bold=True) + click.style(msg, fg="yellow"))


def error(msg):
    click.echo(click.style("✖ ", fg="red", bold=True) + click.style(msg, fg="red"), err=True)


def step(msg):
    """A command being run, shown dimmed."""
    click.echo(click.style(f"$ {msg}", dim=True))


def smart_log(msg):
    """Pick a color by message content so services stay UI-agnostic."""
    if "created" in msg or "started" in msg or "stopped" in msg or "deleted" in msg:
        success(msg)
    elif "already exists" in msg or "does not exist" in msg or "not found" in msg:
        warn(msg)
    elif msg.startswith("$"):
        step(msg[2:])
    else:
        info(msg)