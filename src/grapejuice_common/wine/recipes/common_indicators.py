from grapejuice_common.wine.wineprefix import Wineprefix


def roblox_is_installed(prefix: Wineprefix):
    path = prefix.roblox.roblox_player_launcher_path

    if path is None:
        return False

    return path.exists() and path.is_file()
