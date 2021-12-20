import json
import logging
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from grapejuice_common.errors import NoWineError

HERE = Path(__file__).resolve().parent
INSTANCE_ID = str(uuid.uuid4())

LOG = logging.getLogger(__name__)


def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p)

    return p


def roblox_app_experience_url():
    return "roblox-player:+launchmode:app+robloxLocale:en_us+gameLocale:en_us+LaunchExp:InApp"


def roblox_return_to_studio():
    return "https://www.roblox.com/login/return-to-studio"


def git_repository():
    return "https://gitlab.com/brinkervii/grapejuice"


def documentation_link():
    return "https://brinkervii.gitlab.io/grapejuice/docs/"


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


@dataclass
class FpsUnlockerRelease:
    id: int
    tag: str
    download_url: str = "https://github.com/axstin/rbxfpsunlocker/files/5203791/rbxfpsunlocker-x86.zip"
    did_get_from_github_releases: bool = False


def current_rbxfpsunlocker_release() -> FpsUnlockerRelease:
    try:
        import requests

        github_latest_release = requests.get("https://api.github.com/repos/axstin/rbxfpsunlocker/releases/latest")
        github_latest_release.raise_for_status()

        github_latest_release = github_latest_release.json()

        url_ptn = re.compile(r"(https://github.com/axstin.rbxfpsunlocker/files/\d+/[\w-]+?\.zip)")
        found_urls = url_ptn.findall(github_latest_release["body"])

        if len(found_urls) <= 0:
            for asset in github_latest_release["assets"]:
                asset_name = asset["name"].lower()

                if asset_name in ("rbxfpsunlocker-x64.zip", "rbxfpsunlocker-x86.zip"):
                    found_urls.append(asset["browser_download_url"])

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

        return FpsUnlockerRelease(
            github_latest_release.get("id", -1),
            github_latest_release.get("tag_name", "unknown_tag"),
            prioritized[0]["url"],
            did_get_from_github_releases=True
        )

    except Exception as e:
        LOG.error(str(e))

        return FpsUnlockerRelease(-1, "unknown_tag")


def text_encoding() -> str:
    return "UTF-8"
