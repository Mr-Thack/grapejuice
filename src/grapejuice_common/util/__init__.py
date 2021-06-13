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
