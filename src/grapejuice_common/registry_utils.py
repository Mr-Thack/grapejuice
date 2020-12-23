from grapejuice_common import variables
from grapejuice_common.registry_file import RegistryFile


def logged_into_studio() -> bool:
    file = RegistryFile(variables.wine_user_reg())
    file.load()

    roblox_com = file.find_key(r"Software\\Roblox\\RobloxStudioBrowser\\roblox.com")
    if roblox_com:
        if roblox_com.get_attribute(".ROBLOSECURITY"):
            return True

    return False
