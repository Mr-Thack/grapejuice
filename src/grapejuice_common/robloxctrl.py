import os
import time
from pathlib import Path
from typing import Union, List

import grapejuice_common.variables as variables
import grapejuice_common.winectrl as winectrl
from grapejuice_common.logs.log_util import log_function
from grapejuice_common.util import download_file

DOWNLOAD_URL = "https://www.roblox.com/download/client"


def get_installer():
    install_path = variables.installer_path()

    if os.path.exists(install_path):
        os.remove(install_path)

    download_file(DOWNLOAD_URL, install_path)


def run_installer():
    winectrl.create_prefix()
    get_installer()

    p = variables.installer_path()
    winectrl.run_exe_nowait(p)


@log_function
def locate_in_versions(exe_name) -> Union[Path, None]:
    search_roots: List[Path] = [
        variables.wine_roblox_prog(),
        variables.wine_roblox_local_settings(),
        variables.wine_roblox_appdata_local()
    ]

    for root in search_roots:
        versions = root / "Versions"

        if root.exists() and versions.exists() and versions.is_dir():
            executable_path = versions / exe_name

            if executable_path.exists() and executable_path.is_file():
                return executable_path

            for version in Path(versions).glob("*"):
                if version.is_dir():
                    executable_path = version / exe_name

                    if executable_path.exists() and executable_path.is_file():
                        return executable_path

    return None


@log_function
def locate_roblox_exe(exe_name) -> Path:
    versioned = locate_in_versions(exe_name)

    if not versioned:
        location = variables.wine_roblox_prog() / "Versions" / exe_name

        if location.exists():
            return location

    return versioned


@log_function
def locate_studio_launcher() -> Path:
    return locate_roblox_exe("RobloxStudioLauncherBeta.exe")


@log_function
def locate_studio_exe() -> Path:
    return locate_in_versions("RobloxStudioBeta.exe")


@log_function
def locate_player_launcher() -> Path:
    return locate_in_versions("RobloxPlayerLauncher.exe")


@log_function
def locate_studio_client_app_settings():
    studio_exe = locate_studio_exe()

    if studio_exe is None:
        return None

    return studio_exe.parent / "ClientSettings" / "ClientAppSettings.json"


def run_studio(uri="", ide=False):
    launcher = locate_studio_launcher()

    if launcher is None:
        return False

    if ide:
        winectrl.run_exe_nowait(launcher, "-ide", uri)

    else:
        if uri:
            winectrl.run_exe_nowait(launcher, uri)

        else:
            winectrl.run_exe_nowait(launcher, "-ide")

    return True


def studio_with_events(**events):
    studio_exe = locate_studio_exe()
    if studio_exe is None:
        return False

    args = [studio_exe]

    for k, v in events.items():
        args.append("-" + k)
        args.append(v)

    return winectrl.run_exe_nowait(*args)


def fast_flag_extract():
    fast_flag_path = variables.wine_roblox_studio_app_settings()

    if fast_flag_path.exists():
        os.remove(fast_flag_path)

    process = studio_with_events(startEvent="FFlagExtract", showEvent="NoSplashScreen")

    while True:
        if fast_flag_path.exists():
            stat = os.stat(fast_flag_path)

            if stat.st_size > 0:
                break

        time.sleep(0.5)

    process.kill()


def run_player(uri):
    player = locate_player_launcher()

    if player is None:
        return False

    winectrl.run_exe_nowait(player, uri)

    return True
