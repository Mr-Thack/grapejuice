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
