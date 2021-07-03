import atexit
import getpass
import logging
import os
import subprocess
import uuid
from pathlib import Path

from grapejuice_common.util.errors import NoWineError

HERE = os.path.abspath(os.path.dirname(__file__))
INSTANCE_ID = str(uuid.uuid4())

LOG = logging.getLogger(__name__)

at_exit_handlers = dict()


def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p)

    return p


def home():
    return str(Path(os.environ["HOME"]).resolve())


def system_application_dir():
    p = os.path.dirname(src_dir())

    assert os.path.exists(p)

    return p


def user_application_dir():
    return os.path.join(local_share(), "grapejuice")


def application_manifest():
    return os.path.join(user_application_dir(), "package_manifest.json")


def assets_dir():
    search_locations = [
        os.path.join(HERE, "assets"),
        os.path.join(os.getcwd(), "assets"),
        os.path.join(system_application_dir(), "assets")
    ]

    for p in search_locations:
        if os.path.exists(p):
            return p

    raise RuntimeError("Could not find assets directory")


def desktop_assets_dir():
    return os.path.join(assets_dir(), "desktop")


def mime_xml_assets_dir():
    return os.path.join(assets_dir(), "mime_xml")


def icons_assets_dir():
    return os.path.join(assets_dir(), "icons")


def grapejuice_icon():
    return os.path.join(icons_assets_dir(), "hicolor", "scalable", "apps", "grapejuice.svg")


def src_dir():
    return os.path.abspath(os.path.dirname(HERE))


def glade_dir():
    return os.path.join(assets_dir(), "glade")


def grapejuice_glade():
    return os.path.join(glade_dir(), "grapejuice.glade")


def about_glade():
    return os.path.join(glade_dir(), "about.glade")


def fast_flag_editor_glade():
    return os.path.join(glade_dir(), "fast_flag_editor.glade")


def grapejuice_components_glade():
    return os.path.join(glade_dir(), "grapejuice_components.glade")


def fast_flag_warning_glade():
    return os.path.join(glade_dir(), "fast_flag_warning.glade")


def config_base_dir():
    return ensure_dir(os.path.join(xdg_config_home(), "brinkervii"))


def grapejuice_config_dir():
    return ensure_dir(os.path.join(config_base_dir(), "grapejuice"))


def grapejuice_user_settings():
    return Path(grapejuice_config_dir(), "user_settings.json")


def wineprefix_dir():
    return os.path.join(user_application_dir(), "wineprefix")


def wine_drive_c():
    return os.path.join(wineprefix_dir(), "drive_c")


def wine_user_reg():
    return os.path.join(wineprefix_dir(), "user.reg")


def wine_roblox_prog() -> Path:
    return Path(wine_drive_c(), "Program Files (x86)", "Roblox")


def wine_roblox_local_settings() -> Path:
    return Path(wine_drive_c(), "users", getpass.getuser(), "Local Settings", "Application Data", "Roblox")


def wine_temp():
    return ensure_dir(os.path.join(wine_drive_c(), "windows", "temp"))


def wine_user():
    return os.path.join(wine_drive_c(), "users", os.environ["USER"])


def wine_roblox_appdata():
    p = os.path.join(wine_user(), "Local Settings", "Application Data", "Roblox")
    if os.path.exists(p):
        return p

    p = os.path.join(wine_user(), "AppData", "Local", "Roblox")
    return p


def wine_roblox_appdata_local() -> Path:
    return Path(wine_user(), "AppData", "Local", "Roblox")


def wine_roblox_global_settings_13():
    return os.path.join(wine_roblox_appdata(), "GlobalSettings_13.xml")


def wine_roblox_studio_app_settings():
    return Path(wine_roblox_appdata(), "ClientSettings", "StudioAppSettings.json")


def installer_path():
    return Path(wine_temp(), "Roblox_Installer.exe")


def xdg_config_home():
    if "XDG_CONFIG_HOME" in os.environ:
        config_home = os.environ["XDG_CONFIG_HOME"]
        if config_home and os.path.exists(config_home) and os.path.isdir(config_home):
            return config_home

    config_home = os.path.join(home(), ".config")
    if not os.path.exists(config_home):
        os.makedirs(config_home)

    return config_home


def dot_local():
    path = os.path.join(home(), ".local")
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def local_share():
    return os.path.join(dot_local(), "share")


def local_var():
    return os.path.join(dot_local(), "var")


def local_log():
    return os.path.join(local_var(), "log")


def logging_directory():
    return os.path.join(local_log(), "grapejuice")


def xdg_documents():
    run = subprocess.run(["xdg-user-dir", "DOCUMENTS"], stdout=subprocess.PIPE, check=False)
    documents_path = run.stdout.decode("utf-8").rstrip()

    if os.path.exists(documents_path):
        return documents_path

    documents_path = os.path.join(home(), "Documents")
    return ensure_dir(documents_path)


def roblox_app_experience_url():
    return "roblox-player:+launchmode:app+robloxLocale:en_us+gameLocale:en_us+LaunchExp:InApp"


def roblox_return_to_studio():
    return "https://www.roblox.com/login/return-to-studio"


def git_repository():
    return "https://gitlab.com/brinkervii/grapejuice"


def git_wiki():
    return f"{git_repository()}/-/wikis/home"


def git_grapejuice_init():
    from grapejuice_common.features.settings import current_settings
    from grapejuice_common.features import settings

    release_channel = current_settings.get(settings.k_release_channel)
    return f"{git_repository()}/-/raw/{release_channel}/src/grapejuice/__init__.py"


def git_source_tarball():
    from grapejuice_common.features.settings import current_settings
    from grapejuice_common.features import settings

    release_channel = current_settings.get(settings.k_release_channel)
    return f"{git_repository()}/-/archive/{release_channel}/grapejuice-{release_channel}.tar.gz"


def tmp_path():
    path = Path(os.path.sep, "tmp", f"grapejuice-{INSTANCE_ID}").resolve()
    path_string = str(path)

    if "clean_tmp_path" not in at_exit_handlers:
        def on_exit(*_, **__):
            import shutil
            shutil.rmtree(path, ignore_errors=True)

        at_exit_handlers["clean_tmp_path"] = on_exit

    return ensure_dir(path_string)


def wine_binary(arch=""):
    from grapejuice_common.features.settings import current_settings
    from grapejuice_common.features import settings

    custom_wine_binary = (current_settings.get(settings.k_wine_binary) or "").strip()
    if custom_wine_binary and not os.path.exists(custom_wine_binary):
        LOG.error(f"!! Custom wine binary set to {custom_wine_binary}, but it does not exist !!")

    path_search = [custom_wine_binary] if custom_wine_binary else []

    if "PATH" in os.environ:
        for spec in os.environ["PATH"].split(":"):
            path_search.append(os.path.join(spec, "wine" + arch))

    static_search = [
        "/opt/wine-stable/bin/wine" + arch,
        "/opt/wine-staging/bin/wine" + arch
    ]

    for p in path_search + static_search:
        if p and os.path.exists(p):
            LOG.debug(f"Using wine binary at: {p}")
            return p

    raise NoWineError()


def wine_binary_64():
    return wine_binary("64")


def required_wine_version():
    return "wine-4.0"


def at_exit_handler(*args, **kwargs):
    for v in filter(callable, at_exit_handlers.values()):
        v(*args, **kwargs)


atexit.register(at_exit_handler)
