import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from grapejuice_common import variables


@dataclass
class LSPciEntry:
    pci_id: str
    attributes: Dict[str, str] = field(default_factory=dict)

    @property
    def is_graphics_card(self) -> bool:
        return "vga compatible controller" in self.attributes

    @property
    def kernel_driver(self) -> Optional[str]:
        v = self.attributes.get("kernel driver in use", None)

        if v is not None:
            v = v.strip()

        return v

    @property
    def kernel_modules(self) -> List[str]:
        return list(
            filter(
                lambda s: not not s,
                map(
                    str.strip,
                    re.split(r"[,\s]+", self.attributes.get("kernel modules", ""))
                )
            )
        )


class LSPci:
    _entries: List[LSPciEntry]

    def __init__(self):
        self._entries = []

        lc_all = os.environ.get("LC_ALL", "")
        lang = os.environ.get("LANG")
        os.environ["LC_ALL"] = "C"
        os.environ.pop("LANG")

        try:
            content = subprocess.check_output(["lspci", "-vvv"]).decode(variables.text_encoding())
            self._parse(content)

        except Exception as e:
            if lc_all:
                os.environ["LC_ALL"] = lc_all

            if lang:
                os.environ["LANG"] = lang

            raise e

    def _parse(self, content: str):
        work: Optional[LSPciEntry] = None

        whitespace_ptn = re.compile(r"^\s+\w+")
        pci_id_ptn = re.compile(r"([\d:\.]+)\s+(.*)\s*")

        def explode_line(line_to_be_exploded: str):
            s = line_to_be_exploded.split(":")
            key = s[0]
            value = ":".join(s[1:])

            return key.strip().lower(), value.strip()

        for line in content.split("\n"):
            if not line.strip():
                if work is not None:
                    self._entries.append(work)

                work = None

                continue

            match = whitespace_ptn.search(line)
            starts_with_whitespace = match is not None

            if starts_with_whitespace:
                k, v = explode_line(line.strip())

            else:
                match = pci_id_ptn.search(line)
                assert match is not None, "Invalid line"

                work = LSPciEntry(match.group(1))

                k, v = explode_line(match.group(2))

            assert work is not None, "Invalid state"
            work.attributes[k] = v

        if work is not None:
            self._entries.append(work)

    @property
    def graphics_cards(self) -> List[LSPciEntry]:
        return list(filter(lambda x: x.is_graphics_card, self._entries))
