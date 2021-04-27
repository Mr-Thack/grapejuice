import json
import os
from pathlib import Path
from typing import Dict

from grapejuice_common import variables


def prefix_flags_path() -> Path:
    return Path(variables.wineprefix_dir()) / "grapejuice_flags.json"


class Flags:
    dll_overrides_applied = "dll_overrides_applied"


class PrefixFlags:
    _data: Dict

    def __init__(self):
        self.load()

    def load(self):
        path = prefix_flags_path()

        if path.exists():
            with path.open("r") as fp:
                self._data = json.load(fp)

        else:
            self._data = dict()

    def save(self):
        path = prefix_flags_path()
        os.makedirs(path.parent, exist_ok=True)

        with path.open("w+") as fp:
            json.dump(self._data, fp)

    @property
    def dll_overrides_applied(self):
        return self._data.get(Flags.dll_overrides_applied, False)

    @dll_overrides_applied.setter
    def dll_overrides_applied(self, v: bool):
        self._data[Flags.dll_overrides_applied] = v
        self.save()
