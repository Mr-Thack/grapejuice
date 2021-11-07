from grapejuice_common.util.errors import RobloxExecutableNotFound
from grapejuice_common.wine.recipes.common_indicators import roblox_is_installed
from grapejuice_common.wine.recipes.recipe import Recipe
from grapejuice_common.wine.wineprefix import Wineprefix
from grapejuice_common.wine.wineprefix_hints import WineprefixHint


def roblox_studio_is_installed(prefix: Wineprefix):
    try:
        return prefix.roblox.roblox_studio_executable_path is not None

    except RobloxExecutableNotFound:
        return False


class RobloxStudioRecipe(Recipe):
    def __init__(self):
        super().__init__(
            indicators=[roblox_is_installed, roblox_studio_is_installed],
            hint=WineprefixHint.studio
        )

    def make_in(self, prefix: Wineprefix):
        if roblox_is_installed(prefix):
            prefix.roblox.run_roblox_studio()

        else:
            prefix.roblox.install_roblox(post_install_function=prefix.roblox.run_roblox_studio())
