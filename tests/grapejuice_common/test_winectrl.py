from grapejuice_common import winectrl


def test_vanilla_ok():
    assert winectrl.wine_ok(system_wine="wine-6.0.1", show_dialog=False)
    assert winectrl.wine_ok(system_wine="wine-6.0-rc6", show_dialog=False)


def test_git_build_not_ok():
    assert not winectrl.wine_ok(system_wine="wine-5.5-436-g2b0977fc71", show_dialog=False)
    assert not winectrl.wine_ok(system_wine="wine-5.8-173-g9e26bc8116", show_dialog=False)


def test_tkg_build_ok():
    assert winectrl.wine_ok(system_wine="wine-6.17.r0.g5f19a815 ( TkG Staging Esync Fsync )", show_dialog=False)


def test_vanilla_not_ok():
    assert not winectrl.wine_ok(system_wine="wine-5.0", show_dialog=False)
    assert not winectrl.wine_ok(system_wine="wine-5.0-rc6", show_dialog=False)


def test_ubuntu_ok():
    assert winectrl.wine_ok(system_wine="wine-6.0.1 (Ubuntu 6.0.1-1)", show_dialog=False)


def test_ubuntu_not_ok():
    assert not winectrl.wine_ok(system_wine="wine-5.0.1 (Ubuntu 5.0.1-1)", show_dialog=False)