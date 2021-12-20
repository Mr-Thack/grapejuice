from typing import List

from grapejuice_common.hardware_info.lspci import LSPci, LSPciEntry
from grapejuice_common.hardware_info.xrandr import IXRandR, XRandRProvider


def pci_entry_to_phony_xrandr_entry(index: int, entry: LSPciEntry):
    return XRandRProvider(
        index=index,
        id=index,
        cap=list(),
        crtcs=-1,
        outputs=1,
        associated_providers=-1,
        name=entry.gpu_id_string
    )


class PhonyXRandR(IXRandR):
    _providers: List[XRandRProvider]

    def __init__(self):
        lspci = LSPci()

        self._providers = list(map(lambda t: pci_entry_to_phony_xrandr_entry(*t), enumerate(lspci.graphics_cards)))
        if len(self._providers) > 1:
            self._providers[-1].cap = [
                "Sink Output",
                "Sink Offload",
                "Source Output",
                "Source Offload"
            ]

    @property
    def providers(self) -> List[XRandRProvider]:
        return self._providers
