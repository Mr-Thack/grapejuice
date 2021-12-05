from typing import List

from grapejuice_common.wine.wineprefix_hints import WineprefixHint


class NoWineError(RuntimeError):
    def __init__(self):
        super().__init__("A valid wine binary could not be found")


class RobloxDownloadError(RuntimeError):
    def __init__(self):
        super().__init__("Roblox installer couldn't be downloaded")


class RobloxExecutableNotFound(RuntimeError):
    def __init__(self, executable_name: str):
        super().__init__(f"Roblox executable '{executable_name}' could not be found!")


class NoWineprefixConfiguration(RuntimeError):
    def __init__(self):
        super().__init__("Configuration for a Wineprefix instance cannot be None")


class WineprefixNotFoundUsingHints(RuntimeError):
    def __init__(self, hints: List[WineprefixHint]):
        hints_as_string = "\n".join(list(map(lambda hint: hint.value, hints)))
        msg = f"A wineprefix could not be found using hints. The following hints were used:\n\n{hints_as_string}"

        super().__init__(msg)


class HardwareProfilingError(RuntimeError):
    pass
