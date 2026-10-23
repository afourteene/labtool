import pytest
from labtool.domain import LabError, Platform, plan_install
from labtool.services import install_cloudflared


def test_mac_uses_brew():
    assert plan_install(Platform("darwin", "arm64", has_brew=True)) == [
        ["brew", "install", "cloudflared"]]


def test_mac_without_brew_fails():
    with pytest.raises(LabError):
        plan_install(Platform("darwin", "arm64"))


def test_ubuntu_uses_deb_for_arch():
    cmds = plan_install(Platform("linux", "arm64", has_apt=True))
    assert cmds[0][-1].endswith("cloudflared-linux-arm64.deb")
    assert cmds[1][:3] == ["sudo", "dpkg", "-i"]


def test_skips_when_installed():
    ran = []
    result = install_cloudflared(lambda: None, lambda: True,
                                 lambda c, l: ran.append(c), log=lambda m: None)
    assert result is False and ran == []