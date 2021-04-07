import os
import re
import time
from pathlib import Path
from typing import Union

import grapejuice_common.variables as variables
import grapejuice_common.winectrl as winectrl
from grapejuice_common.logs.log_util import log_function
from grapejuice_common.util import download_file

DOWNLOAD_URL = "https://www.roblox.com/download/client"


def set_graphics_mode(mode: int):
    settings_path = variables.wine_roblox_global_settings_13()
    if not os.path.exists(settings_path):
        return False

    ptn = r'token name=\"GraphicsMode\">(\d+)</token'
    gl = 'token name="GraphicsMode">' + str(mode) + '</token'

    output_lines = []
    with open(settings_path, "r") as fp:
        for line in fp.readlines():
            if "GraphicsMode" in line:
                line = re.sub(ptn, gl, line)

            output_lines.append(line)

    with open(settings_path, "w") as fp:
        fp.writelines(output_lines)


def set_graphics_mode_opengl():
    set_graphics_mode(4)


def get_installer():
    install_path = variables.installer_path()

    if os.path.exists(install_path):
        os.remove(install_path)

    download_file(DOWNLOAD_URL, install_path)


def run_installer():
    winectrl.create_prefix()
    get_installer()
    winectrl.run_exe_nowait(variables.installer_path())


@log_function
def locate_in_versions(exe_name) -> Union[str, None]:
    search_roots = [
        variables.wine_roblox_prog(),
        variables.wine_roblox_local_settings()
    ]

    for root in search_roots:
        versions = Path(root, "Versions")

        if os.path.exists(root) and versions.exists() and versions.is_dir():
            executable_path = versions / exe_name

            if executable_path.exists() and executable_path.is_file():
                return str(executable_path)

            for version in Path(versions).glob("*"):
                if version.is_dir():
                    executable_path = version / exe_name

                    if executable_path.exists() and executable_path.is_file():
                        return str(executable_path)

    return None


@log_function
def locate_roblox_exe(exe_name):
    versioned = locate_in_versions(exe_name)

    if not versioned:
        location = os.path.join(variables.wine_roblox_prog(), "Versions", exe_name)
        if os.path.exists(location):
            return location

    return versioned


@log_function
def locate_studio_launcher():
    return locate_roblox_exe("RobloxStudioLauncherBeta.exe")


@log_function
def locate_studio_exe():
    return locate_in_versions("RobloxStudioBeta.exe")


@log_function
def locate_player_launcher():
    return locate_in_versions("RobloxPlayerLauncher.exe")


@log_function
def locate_client_app_settings():
    studio_exe = locate_studio_exe()
    if studio_exe is None:
        return None

    return os.path.join(os.path.dirname(studio_exe), "ClientSettings", "ClientAppSettings.json")


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
    if os.path.exists(fast_flag_path):
        os.remove(fast_flag_path)

    process = studio_with_events(startEvent="FFlagExtract", showEvent="NoSplashScreen")

    while True:
        if os.path.exists(fast_flag_path):
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
