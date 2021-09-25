from pathlib import Path
from typing import Union

from grapejuice_common.wine.wineprefix_configuration import WineprefixConfiguration, WineprefixConfigurationObject
from grapejuice_common.wine.wineprefix_core_control import WineprefixCoreControl
from grapejuice_common.wine.wineprefix_paths import WineprefixPaths
from grapejuice_common.wine.wineprefix_roblox import WineprefixRoblox


class Wineprefix:
    def __init__(
        self,
        base_directory: Path,
        configuration_object: Union[WineprefixConfigurationObject, None] = None
    ):
        self._paths = WineprefixPaths(base_directory)
        self._configuration = WineprefixConfiguration(configuration_object or dict())
        self._core_control = WineprefixCoreControl(self._paths, self.configuration)
        self._roblox = WineprefixRoblox(self.paths, self._core_control)

    @property
    def paths(self) -> WineprefixPaths:
        return self._paths

    @property
    def core_control(self) -> WineprefixCoreControl:
        return self._core_control

    @property
    def roblox(self) -> WineprefixRoblox:
        return self._roblox

    @property
    def configuration(self) -> WineprefixConfiguration:
        return self._configuration
