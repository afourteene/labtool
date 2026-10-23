import yaml

from ..domain import Lab, LabError, Node


def load_lab(path):
    try:
        with open(path) as f:
            raw = yaml.safe_load(f)
        nodes = tuple(Node(**n) for n in raw["nodes"])
        return Lab(domain=raw["domain"], tunnel_name=raw["tunnel_name"], nodes=nodes)
    except FileNotFoundError:
        raise LabError(f"File {path} not found")
    except (KeyError, TypeError, ValueError) as e:
        raise LabError(f"lab.yaml is invalid: {e}")