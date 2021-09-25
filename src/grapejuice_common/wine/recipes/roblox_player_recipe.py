from grapejuice_common.wine.recipes.common_indicators import roblox_is_installed
from grapejuice_common.wine.recipes.recipe import Recipe
from grapejuice_common.wine.wineprefix import Wineprefix
from grapejuice_common.wine.wineprefix_hints import WineprefixHint


class RobloxPlayerRecipe(Recipe):
    def __init__(self):
        super().__init__(
            indicators=[roblox_is_installed],
            hint=WineprefixHint.player
        )

    def make_in(self, prefix: Wineprefix):
        prefix.roblox.install_roblox()
