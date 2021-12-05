import logging
import uuid
from pathlib import Path
from typing import List, Optional, Dict

from grapejuice_common.errors import WineprefixNotFoundUsingHints, HardwareProfilingError
from grapejuice_common.hardware_info.hardware_profile import HardwareProfile
from grapejuice_common.models.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.roblox_renderer import RobloxRenderer
from grapejuice_common.wine.wineprefix import Wineprefix
from grapejuice_common.wine.wineprefix_hints import WineprefixHint

LOG = logging.getLogger(__name__)


def get_wineprefix(hints: List[WineprefixHint], when_not_found_prefix_factory: Optional[callable] = None):
    from grapejuice_common.features.settings import current_settings, k_wineprefixes

    for prefix_configuration in current_settings.get(k_wineprefixes):
        has_all_hints = True

        for hint in hints:
            has_all_hints = has_all_hints and hint.value in prefix_configuration.get("hints", [])

        if has_all_hints:
            return Wineprefix(
                configuration=WineprefixConfigurationModel.from_dict(prefix_configuration)
            )

    if callable(when_not_found_prefix_factory):
        when_not_found_prefix_factory()
        return get_wineprefix(hints)

    else:
        raise WineprefixNotFoundUsingHints(hints)


def _create_and_save_wineprefix(model_factory):
    def factory():
        from grapejuice_common.features.settings import current_settings

        model = model_factory()
        current_settings.save_prefix_model(model)

    return factory


OtherHints = Optional[List[WineprefixHint]]


def _get_wineprefix_with_other_hints(
    hint: WineprefixHint,
    other_hints: OtherHints,
    when_not_found_prefix_factory: Optional[callable] = None
) -> Wineprefix:
    return get_wineprefix(
        hints=list({hint, *(other_hints or [])}),
        when_not_found_prefix_factory=when_not_found_prefix_factory
    )


def find_wineprefix(prefix_id: str) -> Wineprefix:
    from grapejuice_common.features.settings import current_settings
    return Wineprefix(configuration=current_settings.find_wineprefix(prefix_id))


def _dll_overrides(settings) -> str:
    return settings.get("dll_overrides", "dxdiagn=;winemenubuilder.exe=")


def _env(settings) -> Dict[str, str]:
    return settings.get("env", dict())


def _wine_home(settings) -> str:
    if "wine_home" in settings:
        return settings.get("wine_home")

    if "wine_binary" in settings:
        return str(Path(settings["wine_binary"]).resolve().parent.parent)

    return "/usr"


renderer_hint_mapping = {
    RobloxRenderer.Vulkan: WineprefixHint.render_vulkan,
    RobloxRenderer.OpenGL: WineprefixHint.render_opengl,
    RobloxRenderer.DX11: WineprefixHint.render_dx11
}


def _hardware_profile() -> Optional[HardwareProfile]:
    from grapejuice_common.features.settings import current_settings

    try:
        return current_settings.hardware_profile

    except HardwareProfilingError as e:
        LOG.error(e)

    return None


def _profiled_hints() -> List[WineprefixHint]:
    profile = _hardware_profile()
    if profile is None:
        return []

    render_hint = renderer_hint_mapping.get(profile.preferred_roblox_renderer, None)

    return list(map(
        lambda h: h.value,
        filter(None, [
            render_hint
        ])
    ))


def _prime_offload_sink() -> int:
    profile = _hardware_profile()

    if profile and profile.should_prime:
        return profile.provider_index

    return -1


def create_player_prefix_model(settings: Optional[Dict] = None):
    settings = settings or dict()

    return WineprefixConfigurationModel(
        id=str(uuid.uuid4()),
        priority=0,
        name_on_disk="player",
        display_name="Player",
        wine_home=_wine_home(settings),
        dll_overrides=_dll_overrides(settings),
        env=_env(settings),
        hints=[WineprefixHint.player.value, WineprefixHint.app.value, *_profiled_hints()],
        prime_offload_sink=_prime_offload_sink()
    )


def create_studio_prefix_model(settings: Optional[Dict] = None):
    settings = settings or dict()

    return WineprefixConfigurationModel(
        id=str(uuid.uuid4()),
        priority=0,
        name_on_disk="studio",
        display_name="Studio",
        wine_home=_wine_home(settings),
        dll_overrides=_dll_overrides(settings),
        env=_env(settings),
        hints=[WineprefixHint.studio.value, WineprefixHint.render_dx11.value],
        prime_offload_sink=_prime_offload_sink()
    )


def create_new_model_for_user(settings: Optional[Dict] = None):
    settings = settings or dict()

    model = WineprefixConfigurationModel(
        id=str(uuid.uuid4()),
        priority=0,
        name_on_disk=".",
        display_name="New Wineprefix",
        wine_home=_wine_home(settings),
        dll_overrides=_dll_overrides(settings),
        env=_env(settings),
        hints=[*_profiled_hints()],
        prime_offload_sink=_prime_offload_sink()
    )

    model.create_name_on_disk_from_display_name()

    return model


def get_studio_wineprefix(other_hints: OtherHints = None) -> Wineprefix:
    return _get_wineprefix_with_other_hints(
        WineprefixHint.studio,
        other_hints,
        when_not_found_prefix_factory=_create_and_save_wineprefix(create_studio_prefix_model)
    )


def get_player_wineprefix(other_hints: OtherHints = None) -> Wineprefix:
    return _get_wineprefix_with_other_hints(
        WineprefixHint.player,
        other_hints,
        when_not_found_prefix_factory=_create_and_save_wineprefix(create_player_prefix_model)
    )


def get_app_wineprefix(other_hints: OtherHints = None) -> Wineprefix:
    return _get_wineprefix_with_other_hints(
        WineprefixHint.app,
        other_hints,
        when_not_found_prefix_factory=_create_and_save_wineprefix(create_player_prefix_model)
    )
