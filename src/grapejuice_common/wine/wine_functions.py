import logging
from typing import List, Union

from grapejuice_common.features.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.wine.wineprefix import Wineprefix
from grapejuice_common.wine.wineprefix_hints import WineprefixHint

LOG = logging.getLogger(__name__)


def get_wineprefix(hints: List[WineprefixHint]):
    from grapejuice_common.features.settings import current_settings, k_wineprefixes

    for prefix_configuration in current_settings.get(k_wineprefixes):
        has_all_hints = True

        for hint in hints:
            has_all_hints = has_all_hints and hint.value in prefix_configuration.get("hints", [])

        if has_all_hints:
            return Wineprefix(
                configuration=WineprefixConfigurationModel(**prefix_configuration)
            )

    raise RuntimeError(f"No prefix with hint requirements found: {hints}")


def get_studio_wineprefix(other_hints: Union[List[WineprefixHint], None] = None):
    return get_wineprefix(hints=list({WineprefixHint.studio, *(other_hints or [])}))


def get_player_wineprefix(other_hints: Union[List[WineprefixHint], None] = None):
    return get_wineprefix(hints=list({WineprefixHint.player, *(other_hints or [])}))


def initialize_roblox_in_default_prefix():
    from grapejuice_common.wine.recipes.roblox_player_recipe import RobloxPlayerRecipe

    prefix = get_player_wineprefix()
    prefix.core_control.create_prefix()

    recipe = RobloxPlayerRecipe()
    recipe.make_in(prefix)
