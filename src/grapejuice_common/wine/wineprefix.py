from pathlib import Path

from grapejuice_common.wine.wineprefix_core_control import WineprefixCoreControl
from grapejuice_common.wine.wineprefix_paths import WineprefixPaths
from grapejuice_common.wine.wineprefix_roblox import WineprefixRoblox


class Wineprefix:
    _base_directory: Path
    _paths: WineprefixPaths
    _core_control: WineprefixCoreControl
    _roblox: WineprefixRoblox

    def __init__(self, base_directory: Path):
        self._base_directory = base_directory
        self._paths = WineprefixPaths(base_directory)
        self._core_control = WineprefixCoreControl(self._paths)
        self._roblox = WineprefixRoblox(self._paths, self._core_control)

    @property
    def paths(self) -> WineprefixPaths:
        return self._paths

    @property
    def core_control(self) -> WineprefixCoreControl:
        return self._core_control

    @property
    def roblox(self) -> WineprefixRoblox:
        return self._roblox
