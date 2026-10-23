from labtool.domain import Lab, Node, Tunnel
from labtool.services import init_tunnel


class FakeGateway:
    def __init__(self, existing=None):
        self.existing, self.dns = existing, []

    def find(self, name):
        return self.existing

    def create(self, name):
        return Tunnel("new-id", name)

    def route_dns(self, tunnel_name, hostname):
        self.dns.append(hostname)

    def credentials_path(self, tunnel):
        return f"/creds/{tunnel.id}.json"


class FakeStore:
    def save(self, config):
        self.config = config


def make_lab():
    return Lab("example.com", "t", (Node("a", "10.0.0.1"), Node("b", "10.0.0.2")))


def test_creates_tunnel_when_missing():
    store = FakeStore()
    init_tunnel(make_lab(), FakeGateway(), store, log=lambda m: None)
    assert store.config["tunnel"] == "new-id"
    assert store.config["ingress"][-1] == {"service": "http_status:404"}


def test_reuses_existing_tunnel_and_routes_all_hosts():
    gw, store = FakeGateway(Tunnel("old-id", "t")), FakeStore()
    init_tunnel(make_lab(), gw, store, log=lambda m: None)
    assert store.config["tunnel"] == "old-id"
    assert gw.dns == ["a.example.com", "b.example.com"]