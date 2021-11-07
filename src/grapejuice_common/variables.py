import atexit
import json
import logging
import os
import re
import subprocess
import uuid
from pathlib import Path

from grapejuice_common.util.errors import NoWineError

HERE = Path(__file__).resolve().parent
INSTANCE_ID = str(uuid.uuid4())

LOG = logging.getLogger(__name__)

at_exit_handlers = dict()


def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p)

    return p


def ensure_dir_p(p: Path):
    p.mkdir(parents=True, exist_ok=True)
    return p


def home() -> Path:
    return Path(os.environ["HOME"]).resolve()


def local_share_grapejuice() -> Path:
    return local_share() / "grapejuice"


def wineprefixes_directory() -> Path:
    return local_share_grapejuice() / "prefixes"


def application_manifest() -> Path:
    return local_share_grapejuice() / "package_manifest.json"


def assets_dir() -> Path:
    search_locations = [
        HERE / "assets",
        Path(".").resolve() / "assets"
    ]

    for p in search_locations:
        if p.exists():
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


def config_base_dir() -> Path:
    return ensure_dir_p(xdg_config_home() / "brinkervii")


def grapejuice_config_dir():
    return ensure_dir(os.path.join(config_base_dir(), "grapejuice"))


def grapejuice_user_settings():
    return Path(grapejuice_config_dir(), "user_settings.json")


def xdg_config_home() -> Path:
    if "XDG_CONFIG_HOME" in os.environ:
        config_home = Path(os.environ["XDG_CONFIG_HOME"]).resolve()

        if config_home.exists() and config_home.is_dir():
            return config_home

    return ensure_dir_p(home() / ".config")


def vendor_dir() -> Path:
    return ensure_dir_p(local_share_grapejuice() / "vendor")


def dot_local() -> Path:
    return ensure_dir_p(home() / ".local")


def local_share() -> Path:
    return dot_local() / "share"


def local_var():
    return os.path.join(dot_local(), "var")


def local_log():
    return os.path.join(local_var(), "log")


def logging_directory():
    return os.path.join(local_log(), "grapejuice")


def xdg_documents():
    run = subprocess.run(["xdg-user-dir", "DOCUMENTS"], stdout=subprocess.PIPE, check=False)
    documents_path = Path(run.stdout.decode("utf-8").rstrip())

    if documents_path.exists():
        return documents_path

    return ensure_dir_p(home() / "Documents")


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


def system_wine_binary(arch=""):
    path_search = []

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


def required_wine_version():
    return "wine-6.0"


def required_player_wine_version():
    return "wine-6.11"


def at_exit_handler(*args, **kwargs):
    for v in filter(callable, at_exit_handlers.values()):
        v(*args, **kwargs)


def rbxfpsunlocker_vendor_download_url():
    try:
        import requests

        github_latest_release = requests.get("https://api.github.com/repos/axstin/rbxfpsunlocker/releases/latest")
        github_latest_release.raise_for_status()

        github_latest_release = github_latest_release.json()

        url_ptn = re.compile(r"(https://github.com/axstin.rbxfpsunlocker/files/\d+/[\w-]+?\.zip)")
        found_urls = url_ptn.findall(github_latest_release["body"])

        LOG.info("Found FPS unlocker urls: " + json.dumps(found_urls))

        if len(found_urls) <= 0:
            raise RuntimeError("Did not find any valid fps unlocker urls")

        def prioritize_url(url):
            if "x64" in url:
                priority = 0

            elif "x86" in url:
                priority = 1

            else:
                priority = 99

            return {
                "priority": priority,
                "url": url
            }

        prioritized = list(sorted(map(prioritize_url, found_urls), key=lambda x: x["priority"]))

        return prioritized[0]["url"]

    except Exception as e:
        LOG.error(str(e))
        return "https://github.com/axstin/rbxfpsunlocker/files/5203791/rbxfpsunlocker-x86.zip"


def text_encoding() -> str:
    return "UTF-8"


atexit.register(at_exit_handler)
