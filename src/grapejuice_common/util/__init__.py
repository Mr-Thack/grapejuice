import os
from pathlib import Path


def prepare_uri(uri):
    if uri is None:
        return None

    if os.path.exists(uri):
        return uri

    prepared_uri = uri.replace("'", "")
    if prepared_uri:
        return prepared_uri
    else:
        return None


def download_file(url, target_path: Path):
    import requests

    response = requests.get(url)
    response.raise_for_status()

    with open(target_path, "wb+") as fp:
        fp.write(response.content)

    return target_path


def xdg_open(*args):
    # Find a less heinous way of opening a program while deferring ownership
    os.spawnlp(os.P_NOWAIT, "xdg-open", "xdg-open", *list(map(str, args)))


def strip_pii(s: str):
    from grapejuice_common import paths
    import getpass

    s = s.replace(str(paths.home()), "~")

    if getpass.getuser().lower() != "root":
        s = s.replace(getpass.getuser(), "[REDACTED]")

    return s
