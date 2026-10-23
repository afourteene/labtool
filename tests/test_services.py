from labtool.domain import Lab, Node, Tunnel
from labtool.services import init_tunnel


class FakeGateway:
    def __init__(self, existing=None, logged_in=True):
        self.existing, self.dns = existing, []
        self.logged_in, self.login_called = logged_in, False

    def is_logged_in(self):
        return self.logged_in

    def login(self, log=print):
        self.login_called = True
        self.logged_in = True

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


def quiet(m):
    pass


def test_creates_tunnel_when_missing():
    store = FakeStore()
    init_tunnel(make_lab(), FakeGateway(), store, log=quiet)
    assert store.config["tunnel"] == "new-id"
    assert store.config["ingress"][-1] == {"service": "http_status:404"}


def test_reuses_existing_tunnel_and_routes_all_hosts():
    gw, store = FakeGateway(Tunnel("old-id", "t")), FakeStore()
    init_tunnel(make_lab(), gw, store, log=quiet)
    assert store.config["tunnel"] == "old-id"
    assert gw.dns == ["a.example.com", "b.example.com"]


def test_init_logs_in_when_cert_missing():
    gw = FakeGateway(logged_in=False)
    init_tunnel(make_lab(), gw, FakeStore(), log=quiet)
    assert gw.login_called is True


def test_init_skips_login_when_already_logged_in():
    gw = FakeGateway(logged_in=True)
    init_tunnel(make_lab(), gw, FakeStore(), log=quiet)
    assert gw.login_called is False