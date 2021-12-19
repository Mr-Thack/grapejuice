import logging
from dataclasses import dataclass
from typing import Optional

from grapejuice_common.gtk.components.grape_setting import GrapeSetting
from grapejuice_common.gtk.components.grape_settings_group import GrapeSettingsGroup
from grapejuice_common.gtk.components.grape_settings_pane import GrapeSettingsPane
from grapejuice_common.hardware_info.xrandr import XRandR, XRandRProvider
from grapejuice_common.hint_mappings import hint_renderer_mapping, renderer_hint_mapping
from grapejuice_common.roblox_product import RobloxProduct
from grapejuice_common.roblox_renderer import RobloxRenderer
from grapejuice_common.wine.wineprefix import Wineprefix
from grapejuice_common.wine.wineprefix_hints import WineprefixHint

log = logging.getLogger(__name__)


def _app_hints(prefix: Wineprefix) -> GrapeSettingsGroup:
    product_map = {
        RobloxProduct.app: {
            "display_name": "Desktop App",
            "hint": WineprefixHint.app
        },
        RobloxProduct.studio: {
            "display_name": "Studio",
            "hint": WineprefixHint.studio
        },
        RobloxProduct.player: {
            "display_name": "Experience Player",
            "hint": WineprefixHint.player
        }
    }

    def map_product(product: RobloxProduct):
        info = product_map[product]

        return GrapeSetting(
            key=info["hint"].value,
            display_name=info["display_name"],
            value=info["hint"].value in prefix.configuration.hints
        )

    return GrapeSettingsGroup(
        title="Application Hints",
        description="Grapejuice uses application hints to determine which prefix should be used to launch a Roblox "
                    "application. If you toggle the hint for a Roblox application on for this prefix, Grapejuice will "
                    "use this prefix for that application.",
        settings=list(map(map_product, iter(RobloxProduct)))
    )


def _graphics_settings(prefix: Wineprefix) -> Optional[GrapeSettingsGroup]:
    from grapejuice_common.features.settings import current_settings

    def _get_renderer():
        for hint in prefix.configuration.hints:
            renderer = hint_renderer_mapping.get(WineprefixHint(hint), None)
            if renderer:
                return renderer

        return RobloxRenderer.Undetermined

    def _renderer_setting():
        return GrapeSetting(
            key="roblox_renderer",
            display_name="Roblox Renderer",
            value_type=RobloxRenderer,
            value=_get_renderer()
        )

    def _prime_offload_sink():
        try:
            xrandr = XRandR()
            profile = current_settings.hardware_profile

        except Exception as e:
            log.error(str(e))
            return []

        def provider_to_string(provider: XRandRProvider):
            return f"{provider.index}: {provider.name}"

        provider_list = list(map(provider_to_string, xrandr.providers))

        return [
            GrapeSetting(
                key="should_prime",
                display_name="Use PRIME offloading",
                value=profile.should_prime
            ),
            GrapeSetting(
                key="prime_offload_sink",
                display_name="PRIME offload sink",
                value_type=provider_list,
                value=provider_list
            )
        ]

    def _mesa_gl_override():
        try:
            profile = current_settings.hardware_profile

        except Exception as e:
            log.error(e)
            return None

        return GrapeSetting(
            key="use_mesa_gl_override",
            display_name="Use Mesa OpenGL version override",
            value=profile.use_mesa_gl_override
        )

    settings = list(filter(
        None,
        [
            _renderer_setting(),
            *_prime_offload_sink(),
            _mesa_gl_override()
        ]
    ))

    if not settings:
        return None

    return GrapeSettingsGroup(
        title="Graphics Settings",
        description="Grapejuice can assist with graphics performance in Roblox. These are the settings that control "
                    "Grapejuice's graphics acceleration features.",
        settings=settings
    )


def _wine_debug_settings(prefix: Wineprefix):
    return GrapeSettingsGroup(
        title="Wine debugging settings",
        description="Wine has an array of debugging options that can be used to improve wine. Some of them can cause "
                    "issues, be careful!",
        settings=[
            GrapeSetting(
                key="enable_winedebug",
                display_name="Enable Wine debugging",
                value=prefix.configuration.enable_winedebug,
            ),
            GrapeSetting(
                key="winedebug_string",
                display_name="WINEDEBUG string",
                value=prefix.configuration.winedebug_string
            )
        ]
    )


def _third_party(prefix: Wineprefix):
    return GrapeSettingsGroup(
        title="Third party application integrations",
        description="Grapejuice can assist in installing third party tools that will improve the Roblox experience",
        settings=[
            GrapeSetting(
                key="enable_fps_unlocker",
                display_name="Use Roblox FPS Unlocker",
                value=False
            ),
            GrapeSetting(
                key="use_dxvk",
                display_name="Use DXVK D3D implementation",
                value=False
            )
        ]
    )


@dataclass
class ToggleSettings:
    pass


@dataclass(frozen=True)
class Groups:
    app_hints: GrapeSettingsGroup
    winedebug: GrapeSettingsGroup
    graphics_settings: GrapeSettingsGroup
    third_party: GrapeSettingsGroup

    @property
    def as_list(self):
        return list(filter(
            None,
            [
                self.app_hints,
                self.winedebug,
                self.graphics_settings,
                self.third_party
            ]
        ))


class PrefixFeatureToggles:
    _target_widget = None
    _current_pane: Optional[GrapeSettingsPane] = None
    _groups: Optional[Groups] = None
    _prefix: Optional[Wineprefix] = None

    def __init__(self, target_widget):
        self._target_widget = target_widget

    def _destroy_pane(self):
        if self._current_pane:
            self._target_widget.remove(self._current_pane)
            self._current_pane.destroy()
            self._current_pane = None
            self._groups = None

    def use_prefix(self, prefix: Wineprefix):
        self._destroy_pane()

        self._prefix = prefix
        self._groups = Groups(*list(
            map(
                lambda c: c(prefix),
                filter(
                    None,
                    [
                        _app_hints,
                        _wine_debug_settings,
                        _graphics_settings,
                        _third_party
                    ]
                )
            )
        ))

        pane = GrapeSettingsPane(groups=self._groups.as_list, min_content_height=200)

        self._target_widget.add(pane)
        pane.show_all()

        self._current_pane = pane

    def destroy(self):
        self._destroy_pane()

    @property
    def configured_model(self):
        model = self._prefix.configuration.copy()
        product_hints = list(map(lambda h: h.value, [WineprefixHint.player, WineprefixHint.app, WineprefixHint.studio]))

        hints = model.hints
        hints = list(filter(lambda h: h not in product_hints, hints))
        for k, v in self._groups.app_hints.settings_dictionary.items():
            if v:
                hints.append(k)

        model.hints = hints

        model.apply_dict(self._groups.winedebug.settings_dictionary)

        renderer_hints = list(map(
            lambda h: h.value,
            [WineprefixHint.render_vulkan,
             WineprefixHint.render_opengl,
             WineprefixHint.render_dx11
             ]
        ))
        hints = model.hints
        hints = list(filter(lambda h: h not in renderer_hints, hints))

        graphics = self._groups.graphics_settings.settings_dictionary
        hints.append(renderer_hint_mapping[graphics["roblox_renderer"]].value)
        model.hints = hints
        graphics.pop("roblox_renderer")

        if graphics["should_prime"]:
            model.prime_offload_sink = int(graphics["prime_offload_sink"].split(":")[0])

        else:
            model.prime_offload_sink = -1

        graphics.pop("should_prime")
        graphics.pop("prime_offload_sink")

        model.apply_dict(graphics)

        return model

    def __del__(self):
        self._destroy_pane()
