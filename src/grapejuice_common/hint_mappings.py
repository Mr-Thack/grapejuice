from typing import Dict, Tuple, TypeVar

from grapejuice_common.roblox_renderer import RobloxRenderer
from grapejuice_common.wine.wineprefix_hints import WineprefixHint

K = TypeVar("K")
V = TypeVar("V")


def _swap_tuple(t: Tuple[K, V]) -> Tuple[V, K]:
    return t[1], t[0]


def _swap_dict(d: Dict[K, V]) -> Dict[V, K]:
    return dict(map(_swap_tuple, d.items()))


renderer_hint_mapping = {
    RobloxRenderer.Vulkan: WineprefixHint.render_vulkan,
    RobloxRenderer.OpenGL: WineprefixHint.render_opengl,
    RobloxRenderer.DX11: WineprefixHint.render_dx11
}

hint_renderer_mapping = _swap_dict(renderer_hint_mapping)
