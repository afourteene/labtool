import pytest
from labtool.domain import Lab, LabError, Node, RunState, Tunnel
from labtool.services import delete_tunnel, down_tunnel, up_tunnel


class FakeGateway:
    def __init__(self, tunnel=Tunnel("id1", "t")):
        self.tunnel, self.deleted = tunnel, []

    def find(self, name):
        return self.tunnel

    def delete(self, name):
        self.deleted.append(name)


class FakeRunner:
    log_path = "/tmp/x.log"

    def __init__(self, running=False):
        self.running, self.started, self.stopped = running, [], 0

    def state(self):
        return RunState(self.running, 123 if self.running else None)

    def start(self, name):
        self.started.append(name)
        self.running = True
        return 123

    def stop(self):
        self.stopped += 1
        self.running = False


def lab():
    return Lab("example.com", "t", (Node("a", "10.0.0.1"),))


def quiet(m):
    pass


def test_up_starts_when_stopped():
    r = FakeRunner()
    up_tunnel(lab(), FakeGateway(), r, log=quiet)
    assert r.started == ["t"]


def test_up_is_idempotent_when_running():
    r = FakeRunner(running=True)
    up_tunnel(lab(), FakeGateway(), r, log=quiet)
    assert r.started == []


def test_up_fails_without_tunnel():
    with pytest.raises(LabError):
        up_tunnel(lab(), FakeGateway(tunnel=None), FakeRunner(), log=quiet)


def test_down_stops_running():
    r = FakeRunner(running=True)
    assert down_tunnel(r, log=quiet) is True
    assert r.stopped == 1


def test_down_noop_when_stopped():
    assert down_tunnel(FakeRunner(), log=quiet) is False


def test_delete_stops_then_deletes():
    g, r = FakeGateway(), FakeRunner(running=True)
    assert delete_tunnel(lab(), g, r, log=quiet) is True
    assert r.stopped == 1 and g.deleted == ["t"]


def test_delete_missing_tunnel():
    g = FakeGateway(tunnel=None)
    assert delete_tunnel(lab(), g, FakeRunner(), log=quiet) is False
    assert g.deleted == []