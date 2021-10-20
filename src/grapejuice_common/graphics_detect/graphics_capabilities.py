from enum import Enum
from typing import List

from grapejuice_common.graphics_detect.lspci import LSPci


class GraphicsVendor(Enum):
    INTEL = 0
    AMD = 1
    NVIDIA = 2  # 💢
    UNKNOWN = 999


DRIVER_TO_VENDOR_MAPPING = {
    "i915": GraphicsVendor.INTEL,
    "amdgpu": GraphicsVendor.AMD,
    "r600": GraphicsVendor.AMD,
    "nvidia": GraphicsVendor.NVIDIA,
    "nouveau": GraphicsVendor.NVIDIA
}


class GraphicsCapabilities:
    _pci: LSPci

    def __init__(self, pci: LSPci):
        self._pci = pci

    @property
    def all_kernel_drivers(self) -> List[str]:
        return list(set(map(lambda x: x.kernel_driver, self._pci.graphics_cards)))

    @property
    def hybrid_graphics(self) -> bool:
        drivers = self.all_kernel_drivers

        if len(drivers) < 2:
            return False

        return "i915" in drivers and \
               (
                   ("nvidia" in drivers or "nouveau" in drivers)
                   and
                   ("amdgpu" in drivers or "r600" in drivers)
               )

    @property
    def graphics_vendors(self) -> List[GraphicsVendor]:
        return list(
            set(
                map(
                    lambda x: DRIVER_TO_VENDOR_MAPPING.get(x, GraphicsVendor.UNKNOWN),
                    self.all_kernel_drivers
                )
            )
        )
