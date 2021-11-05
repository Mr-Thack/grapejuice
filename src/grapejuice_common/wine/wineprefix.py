from grapejuice_common import variables
from grapejuice_common.features.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.wine.wineprefix_core_control import WineprefixCoreControl
from grapejuice_common.wine.wineprefix_paths import WineprefixPaths
from grapejuice_common.wine.wineprefix_roblox import WineprefixRoblox


class Wineprefix:
    def __init__(
        self,
        configuration: WineprefixConfigurationModel
    ):
        base_directory = variables.wineprefixes_directory() / configuration.name_on_disk

        self._paths = WineprefixPaths(base_directory)
        self._configuration = configuration
        self._core_control = WineprefixCoreControl(self._paths, self._configuration)
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
    def configuration(self) -> WineprefixConfigurationModel:
        return self._configuration
