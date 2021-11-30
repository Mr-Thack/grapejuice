import re
import subprocess
from dataclasses import dataclass
from typing import List

# pylint: disable=C0301
XRANDR_LINE_PTN = re.compile(
    r"Provider\s+(\d+):\s+id:\s+([a-f\dx]+)\s+cap:\s+(.+)\s+crtcs:\s+(\d+)\s+outputs:\s+(\d+)\s+associated providers:\s+(\d+)\s+name:(.+)\s+@\s+(.+)"
)


@dataclass(frozen=True)
class XRandRProvider:
    index: int
    id: int
    cap: List[str]
    crtcs: int
    outputs: int
    associated_providers: int
    name: str
    pci_id: str

    @property
    def source_output(self) -> bool:
        return "Source Output" in self.cap

    @property
    def sink_output(self) -> bool:
        return "Sink Output" in self.cap

    @property
    def source_offload(self) -> bool:
        return "Source Offload" in self.cap

    @property
    def sink_offload(self) -> bool:
        return "Sink Offload" in self.cap

    @classmethod
    def from_line(cls, line: str):
        line = line.strip()
        match = XRANDR_LINE_PTN.search(line)

        if match is None:
            raise ValueError("Could not parse this XRandR line")

        return cls(
            index=int(match.group(1)),
            id=int(match.group(2), 0),
            cap=list(filter(None, map(str.strip, match.group(3).split(",")))),
            crtcs=int(match.group(4)),
            outputs=int(match.group(5)),
            associated_providers=int(match.group(6)),
            name=match.group(7),
            pci_id=match.group(8)
        )


class XRandR:
    _providers: List[XRandRProvider]

    def __init__(self):
        output = subprocess.check_output(["xrandr", "--listproviders"]).decode("UTF-8")
        lines = list(filter(None, map(str.strip, output.split("\n"))))

        self._providers = list(map(XRandRProvider.from_line, lines[1:]))

    @property
    def providers(self) -> List[XRandRProvider]:
        return self._providers
