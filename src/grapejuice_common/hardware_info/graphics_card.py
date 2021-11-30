import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict

from grapejuice_common.hardware_info.lspci import LSPciEntry


# nVidia Vulkan reference: https://developer.nvidia.com/vulkan-driver
# AMD Vulkan reference: https://www.amd.com/en/technologies/vulkan


class GPUVendor(Enum):
    INTEL = 0
    AMD = 1
    NVIDIA = 2
    UNKNOWN = 999


GPU_VENDOR_PRIORITY = {
    GPUVendor.NVIDIA: 0,
    GPUVendor.AMD: 1,
    GPUVendor.INTEL: 2,

    GPUVendor.UNKNOWN: 999
}

DRIVER_TO_VENDOR_MAPPING = {
    "i915": GPUVendor.INTEL,
    "amdgpu": GPUVendor.AMD,
    "r600": GPUVendor.AMD,
    "nvidia": GPUVendor.NVIDIA,
    "nouveau": GPUVendor.NVIDIA
}

special_nvidia_vulkan_cards = [
    "GeForce MX250", "GeForce MX230", "Quadro T2000", "Quadro T1000", "Quadro GV100", "Quadro GP100",
    "Quadro P6000", "Quadro P5200", "Quadro P5000", "Quadro P4200", "Quadro P4000", "Quadro P3200",
    "Quadro P3000", "Quadro P2200", "Quadro P2000", "Quadro P1000", "Quadro P620", "Quadro P600",
    "Quadro P520", "Quadro P500", "Quadro P400", "Quadro M6000", "Quadro M6000", "Quadro M5500",
    "Quadro M5000", "Quadro M5000M", "Quadro M4000", "Quadro M4000M", "Quadro M3000M", "Quadro M2200",
    "Quadro M2000", "GeForce GTX 860M", "GeForce GTX 850M", "GeForce 845M", "GeForce 840M", "GeForce 830M",
    "GeForce GTX 750 Ti", "GeForce GTX 750", "GeForce GTX 745", "GeForce MX130", "Quadro M2000M",
    "Quadro M1000M", "Quadro M600M", "Quadro M500M", "Quadro M1200", "Quadro M620", "Quadro M520",
    "Quadro K2200M", "Quadro K620M"
]


@dataclass()
class GraphicsCard:
    lspci_entry: LSPciEntry
    _can_do_vulkan_value: Optional[bool] = None

    @property
    def vendor(self) -> GPUVendor:
        driver = self.lspci_entry.kernel_driver
        if driver in DRIVER_TO_VENDOR_MAPPING:
            return DRIVER_TO_VENDOR_MAPPING[driver]

        return GPUVendor.UNKNOWN

    @property
    def pci_id(self) -> str:
        return self.lspci_entry.pci_id

    # pylint: disable=R1702,R0911,R0912
    @property
    def can_do_vulkan(self):
        if self._can_do_vulkan_value is not None:
            return self._can_do_vulkan_value

        id_string = self.lspci_entry.gpu_id_string
        id_string_l = id_string.lower()

        def resolve(x):
            self._can_do_vulkan_value = x
            return x

        if self.vendor is GPUVendor.NVIDIA:
            # Any RTX card can do Vulkan
            if "RTX" in id_string:
                return resolve(True)

            # Any GTX card in the 900+ series can do vulkan
            match = re.search(r"GeForce\s+GTX\s+(\d+)", id_string)
            if match:
                series = int(match.group(1))
                if series > 900:
                    return resolve(True)

            # Any card that got some TLC from nVidia
            return resolve(
                any(
                    map(
                        lambda x: x in id_string_l,
                        map(
                            str.lower,
                            special_nvidia_vulkan_cards
                        )
                    )
                )
            )

        elif self.vendor is GPUVendor.AMD:
            if "RX" in id_string:
                match = re.search(r"\[Radeon RX\s+(.+)]", id_string)
                if match:
                    for product in list(filter(None, map(str.strip, match.group(1).split("/")))):
                        match = re.search(r"^(\d+)", product)
                        if match:
                            v = int(match.group(1))

                            if v >= 5700:
                                return resolve(True)

                            if 400 < v < 600:
                                return resolve(True)

            # R7 and R9 series graphics
            if ("r7" in id_string_l) or ("r9" in id_string_l):
                return resolve(True)

            # R5 series graphics (but only 240 and up)
            match = re.search(r"r5\s+(\d+)", id_string_l)
            if match:
                if int(match.group(1)) >= 240:
                    return resolve(True)

            # HD 8000 and up
            match = re.search(r"hd (\d+)", id_string_l)
            if match:
                if int(match.group(1)) >= 8570:
                    return resolve(True)

            # HD7000 and lower technically do support Vulkan, but the version is not high
            # enough for Roblox.

            return resolve(False)

        elif self.vendor is GPUVendor.INTEL:
            # Assume any 'gaming' laptop has a new enough intel GPU
            # Other code should ignore the vulkan value if another GPU vendor card is present
            return resolve(True)

        return resolve(False)

    def as_serializable_dict(self) -> Dict[str, any]:
        return {
            "pci_id": self.pci_id,
            "vendor": self.vendor.value,
            "can_do_vulkan": self.can_do_vulkan,
            **self.lspci_entry.attributes
        }

    def __str__(self):
        return f"<{type(self).__name__}> " + json.dumps(self.as_serializable_dict(), indent=2)

    def __hash__(self):
        return hash(self.lspci_entry)
