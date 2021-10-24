class NoWineError(RuntimeError):
    def __init__(self):
        super().__init__("A valid wine binary could not be found")


class RobloxDownloadError(RuntimeError):
    def __init__(self):
        super().__init__("Roblox installer couldn't be downloaded")
