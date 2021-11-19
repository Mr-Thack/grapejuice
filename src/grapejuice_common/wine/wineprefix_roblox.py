import logging
import os
import shutil
import time
from pathlib import Path
from typing import Union

from grapejuice_common import paths
from grapejuice_common.errors import RobloxExecutableNotFound
from grapejuice_common.util import download_file
from grapejuice_common.wine.registry_file import RegistryFile
from grapejuice_common.wine.wineprefix_core_control import WineprefixCoreControl, ProcessWrapper
from grapejuice_common.wine.wineprefix_paths import WineprefixPaths

LOG = logging.getLogger(__name__)

ROBLOX_DOWNLOAD_URL = "https://www.roblox.com/download/client"


def _app_settings_path(executable_path: Path) -> Path:
    client_app_settings = executable_path.parent / "ClientSettings" / "ClientAppSettings.json"

    return client_app_settings


class WineprefixRoblox:
    _prefix_paths: WineprefixPaths
    _core_control: WineprefixCoreControl

    def __init__(self, prefix_paths: WineprefixPaths, core_control: WineprefixCoreControl):
        self._prefix_paths = prefix_paths
        self._core_control = core_control

    def download_installer(self):
        path = self._prefix_paths.installer_download_location

        if path.exists():
            LOG.debug(f"Removing old installer at {path}")
            os.remove(path)

        download_file(ROBLOX_DOWNLOAD_URL, path)

        return path

    def install_roblox(self, post_install_function: callable = None):
        self._core_control.create_prefix()

        self._core_control.run_exe(
            self.download_installer(),
            post_run_function=post_install_function
        )

    def is_logged_into_studio(self) -> bool:
        with RegistryFile(self._prefix_paths.user_reg) as registry_file:
            registry_file.load()

            roblox_com = registry_file.find_key(r"Software\\Roblox\\RobloxStudioBrowser\\roblox.com")
            return (roblox_com is not None) and (roblox_com.get_attribute(".ROBLOSECURITY") is not None)

    def locate_roblox_executable_in_versions(self, executable_name: str) -> Union[Path, None]:
        search_locations = [
            self._prefix_paths.roblox_appdata,
            self._prefix_paths.roblox_program_files
        ]

        for location in search_locations:
            versions_directory = location / "Versions"

            if location.exists() and versions_directory.exists() and versions_directory.is_dir():
                executable_path = versions_directory / executable_name

                if executable_path.exists() and executable_path.is_file():
                    return executable_path

                for version in filter(Path.is_dir, versions_directory.glob("*")):
                    executable_path = version / executable_name

                    if executable_path.exists() and executable_path.is_file():
                        return executable_path

        return None

    def locate_roblox_executable(self, executable_name: str) -> Union[Path, None]:
        versioned_executable_path = self.locate_roblox_executable_in_versions(executable_name)

        if versioned_executable_path is not None:
            return versioned_executable_path

        executable_path = self._prefix_paths.roblox_program_files / "Versions" / executable_name
        if executable_path.exists():
            return executable_path

        LOG.warning(f"Failed to locate Roblox executable: {executable_name}")

        raise RobloxExecutableNotFound(executable_name)

    @property
    def roblox_studio_launcher_path(self) -> Union[Path, None]:
        return self.locate_roblox_executable("RobloxStudioLauncherBeta.exe")

    @property
    def roblox_studio_executable_path(self) -> Union[Path, None]:
        return self.locate_roblox_executable("RobloxStudioBeta.exe")

    @property
    def roblox_player_launcher_path(self) -> Union[Path, None]:
        return self.locate_roblox_executable("RobloxPlayerLauncher.exe")

    @property
    def fast_flag_dump_path(self) -> Path:
        return self._prefix_paths.roblox_appdata / "ClientSettings" / "StudioAppSettings.json"

    @property
    def roblox_studio_app_settings_path(self) -> Union[Path, None]:
        return _app_settings_path(self.roblox_studio_executable_path)

    @property
    def roblox_player_app_settings_path(self) -> Union[Path, None]:
        return _app_settings_path(self.roblox_player_launcher_path)

    @property
    def is_installed(self) -> bool:
        try:
            self.locate_roblox_executable("RobloxPlayerLauncher.exe")
            return True

        except RobloxExecutableNotFound:
            return False

    def run_roblox_studio(self, uri=""):
        launcher_path = self.roblox_studio_launcher_path

        if launcher_path is None:
            raise RuntimeError("Could not locate Roblox Studio launcher")

        run_args = [launcher_path]

        if uri:
            run_args.append(uri)

        self._core_control.run_exe(*run_args)

    def run_roblox_player(self, uri):
        player_launcher_path = self.roblox_player_launcher_path

        if player_launcher_path is None:
            raise RuntimeError("Could not locate the Roblox Player launcher")

        # TODO: Reimplement FPS unlocker launch

        self._core_control.run_exe(player_launcher_path, uri)

    def run_roblox_studio_with_events(self, run_async: bool = True, **events) -> ProcessWrapper:
        roblox_studio_path = self.roblox_studio_executable_path

        if roblox_studio_path is None:
            raise RuntimeError("Could not locate Roblox Studio")

        run_args = [roblox_studio_path]

        for k, v in events.items():
            run_args.append("-" + k)
            run_args.append(v)

        return self._core_control.run_exe(*run_args, run_async=run_async)

    def extract_fast_flags(self):
        fast_flag_path = self.fast_flag_dump_path

        if fast_flag_path.exists():
            os.remove(fast_flag_path)

        studio_process = self.run_roblox_studio_with_events(startEvent="FFlagExtract", showEvent="NoSplashScreen")

        def fast_flags_present():
            if fast_flag_path.exists():
                stat = os.stat(fast_flag_path)

                if stat.st_size > 0:
                    return True

            return False

        while not fast_flags_present():
            time.sleep(0.1)

        shutil.copy(fast_flag_path, paths.fast_flag_cache_location())

        if studio_process:
            studio_process.kill()
            time.sleep(1)  # Give Roblox a chance
            self._core_control.kill_wine_server()
