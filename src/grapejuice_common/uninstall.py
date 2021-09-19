import json
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

from grapejuice_common import variables

LOG = logging.getLogger(__name__)


@dataclass
class UninstallationParameters:
    remove_prefix: bool
    for_reals: bool = False


def go(parameters: UninstallationParameters):
    assert parameters and isinstance(parameters, UninstallationParameters), "Programmer error: Invalid params argument"

    LOG.info("Uninstalling Grapejuice, parameters: " + json.dumps(asdict(parameters), indent=2))

    LOG.info(
        subprocess.check_output([
            sys.executable, "-m", "grapejuiced",
            "kill"
        ]).decode("UTF-8")
    )

    with variables.application_manifest().open("r", encoding=variables.text_encoding()) as fp:
        manifest = json.load(fp)

    for file in manifest["files"]:
        file_path = Path(file)

        if file_path.is_absolute():
            o_file = file
            file_path = variables.home() / file
            LOG.info(f"Mended file path: {o_file} -> {file_path}")

        if file_path.exists() and file_path.is_file():
            LOG.info(f"Removing file from manifest: {file_path}")

            if parameters.for_reals:
                os.remove(file_path)

    if parameters.remove_prefix:
        LOG.info(f"Removing full user application directory: {variables.local_share_grapejuice()}")

        if parameters.for_reals:
            shutil.rmtree(variables.local_share_grapejuice(), ignore_errors=True)

    else:
        LOG.info(f"Removing manifest: {variables.application_manifest()}")

        if parameters.for_reals:
            os.remove(variables.application_manifest())

    LOG.info(
        subprocess.check_output([
            sys.executable, "-m", "pip",
            "uninstall", "-y", "grapejuice"
        ]).decode("UTF-8")
    )

    sys.exit(0)
