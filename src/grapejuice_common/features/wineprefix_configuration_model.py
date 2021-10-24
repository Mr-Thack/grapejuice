from dataclasses import dataclass, field
from typing import Dict, List

from grapejuice_common.wine.wineprefix_hints import WineprefixHint


@dataclass
class WineprefixConfigurationModel:
    id: str
    priority: int
    name_on_disk: str
    display_name: str
    wine_home: str
    dll_overrides: str
    env: Dict[str, str] = field(default_factory=dict)
    hints: List[str] = field(default_factory=list)

    @property
    def hints_as_enum(self) -> List[WineprefixHint]:
        return list(map(lambda x: WineprefixHint[x], self.hints))


def from_json(json_object: Dict[str, any]):
    return WineprefixConfigurationModel(**json_object)
