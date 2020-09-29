import json
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict

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

    with open(variables.application_manifest(), "r") as fp:
        manifest = json.load(fp)

    for file in manifest["files"]:
        if not os.path.isabs(file):
            o_file = file
            file = os.path.join(variables.home(), file)
            LOG.info(f"Mended file path: {o_file} -> {file}")

        if os.path.exists(file) and os.path.isfile(file):
            LOG.info(f"Removing file from manifest: {file}")

            if parameters.for_reals:
                os.remove(file)

    if parameters.remove_prefix:
        LOG.info(f"Removing full user application directory: {variables.user_application_dir()}")

        if parameters.for_reals:
            shutil.rmtree(variables.user_application_dir(), ignore_errors=True)

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
