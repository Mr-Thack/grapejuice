import getpass
from pathlib import Path


class WineprefixPaths:
    _base_directory: Path

    def __init__(self, base_directory: Path):
        self._base_directory = base_directory

    @property
    def drive_c(self) -> Path:
        return self._base_directory / "drive_c"

    @property
    def user_reg(self) -> Path:
        return self._base_directory / "user.reg"

    @property
    def roblox_program_files(self) -> Path:
        return self.drive_c / "Program Files (x86)" / "Roblox"

    @property
    def local_appdata(self):
        return self.user_directory / "Local" / "AppData"

    @property
    def temp_directory(self):
        return self.drive_c / "windows" / "temp"

    @property
    def user_directory(self):
        return self.drive_c / "users" / getpass.getuser()

    @property
    def roblox_appdata(self):
        possible_locations = [
            self.user_directory / "AppData" / "Local" / "Roblox",
            self.user_directory / "Local Settings" / "Application Data" / "Roblox"
        ]

        for location in possible_locations:
            if location.exists():
                return location

        return possible_locations[0]

    @property
    def roblox_studio_app_settings(self):
        return self.roblox_appdata / "ClientSettings" / "StudioAppSettings.json"

    @property
    def installer_download_location(self):
        # Do not call it RobloxPlayerLauncherBeta because it will try to import itself
        return self.temp_directory / "Roblox_Installer.exe"


class Wineprefix:
    _base_directory: Path
    _paths: WineprefixPaths

    def __init__(self, base_directory: Path):
        self._base_directory = base_directory
        self._paths = WineprefixPaths(base_directory)

    @property
    def paths(self):
        return self._paths
