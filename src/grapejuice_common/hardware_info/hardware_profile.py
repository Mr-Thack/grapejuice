import logging
import sys
from itertools import chain
from subprocess import CalledProcessError
from typing import Dict

from grapejuice_common.hardware_info.chassis_type import is_mobile_chassis, ChassisType
from grapejuice_common.hardware_info.glx_info import GLXInfo
from grapejuice_common.hardware_info.graphics_card import GraphicsCard, GPU_VENDOR_PRIORITY, GPUVendor
from grapejuice_common.hardware_info.lspci import LSPci
from grapejuice_common.hardware_info.xrandr import XRandR, XRandRProvider
from grapejuice_common.roblox_renderer import RobloxRenderer

log = logging.getLogger(__name__)


def get_prime_env(card: GraphicsCard, provider: XRandRProvider) -> Dict[str, str]:
    prime_env = {"DRI_PRIME": str(provider.index)}

    if card.vendor is GPUVendor.NVIDIA:
        prime_env = {
            **prime_env,
            "__NV_PRIME_RENDER_OFFLOAD": str(provider.index),
            "__VK_LAYER_NV_optimus": "NVIDIA_only",
            "__GLX_VENDOR_LIBRARY_NAME": "nvidia"
        }

    return prime_env


def can_prime_card(card: GraphicsCard, provider: XRandRProvider):
    is_valid_sink = provider.sink_output or provider.sink_offload

    if not is_valid_sink:
        return False

    base_glx_info_hash = hash(GLXInfo())

    try:
        primed_glx_info_hash = hash(GLXInfo(env=get_prime_env(card, provider)))

    except CalledProcessError as e:
        return False

    return base_glx_info_hash != primed_glx_info_hash


def compute_parameters():
    log.info("Computing hardware profile parameters")

    log.info("Getting lspci and XRandR data")
    xrandr = XRandR()
    hardware_list = LSPci()
    graphics_hardware = hardware_list.graphics_cards

    if len(graphics_hardware) <= 0:
        raise RuntimeError("No graphics hardware")

    should_prime = len(graphics_hardware) > 1
    log.info(f"Got multiple graphics cards: {should_prime}")

    if should_prime:
        should_prime = is_mobile_chassis(ChassisType.local_chassis_type())
        log.info(f"We are on a mobile platform: {should_prime}")

    unordered_graphics_cards = list(map(GraphicsCard, graphics_hardware))
    graphics_cards = list(sorted(unordered_graphics_cards, key=lambda card: GPU_VENDOR_PRIORITY[card.vendor]))

    # Let's just hope cards and providers always follow the same order here
    card_provider_lookup = dict(zip(unordered_graphics_cards, xrandr.providers))
    can_prime_lookup = dict(zip(
        unordered_graphics_cards,
        map(lambda card: can_prime_card(card, card_provider_lookup[card]), unordered_graphics_cards)
    ))

    should_prime = any(can_prime_lookup.values())
    log.info(f"We can prime a graphics card: {should_prime}")

    if len(graphics_cards) == 1:
        log.info("There is only one graphics card installed, pick the 0th one")
        target_card = graphics_cards[0]

    else:
        vendor_set = list(set(map(lambda c: c.vendor, graphics_cards)))
        homogenous_system = len(vendor_set) == 1

        # Prepend a list of cards we can prime so they have a higher priority
        card_iter = chain(filter(lambda card: can_prime_lookup[card], graphics_cards), iter(graphics_cards))

        if homogenous_system:
            log.info("The system is homogenous in vendors just pick the first card we can prime")
            target_card = next(card_iter)

        else:
            log.info("Pick the first vulkan card")  # Which we can prime
            vulkan_card = next(filter(lambda card: card.can_do_vulkan, card_iter))
            target_card = vulkan_card or graphics_cards[0]

    use_mesa_gl_override = False

    if target_card.can_do_vulkan:
        log.info("Target card can do Vulkan, prefer vulkan")
        preferred_roblox_renderer = RobloxRenderer.Vulkan

    else:
        try:
            provider = card_provider_lookup.get(target_card, None)
            if should_prime and provider:
                glx_info = GLXInfo(env=get_prime_env(target_card, provider))

            else:
                glx_info = GLXInfo()

            # Some GPUs are so old that they do not even support a version of OpenGL high enough
            # for Roblox. In this case some mesa trickery is required.

            # Special nVidia case
            if target_card.vendor is GPUVendor.NVIDIA and glx_info.version == (4, 60):
                log.info("Card is an ancient nVidia one, use mesa gl override")
                use_mesa_gl_override = True

            elif glx_info.version <= (4, 4):
                log.info("Card is ancient, use mesa gl override")
                use_mesa_gl_override = True

            log.info("Prefer OpenGL renderer")
            preferred_roblox_renderer = RobloxRenderer.OpenGL

        except CalledProcessError as e:
            log.error(e)
            log.info("Cannot get GL info, prefer D3D11 instead")
            # As a last resort, use D3D11 if GL info is not available
            preferred_roblox_renderer = RobloxRenderer.DX11

    print(target_card)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    compute_parameters()
