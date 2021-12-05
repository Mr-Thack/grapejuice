from enum import Enum


class WineprefixHint(Enum):
    studio = "studio"
    player = "player"
    fps_unlocker = "fps_unlocker"
    app = "app"

    render_vulkan = "roblox_renderer_vulkan"
    render_opengl = "roblox_renderer_opengl"
    render_dx11 = "roblox_renderer_directd3d11"
