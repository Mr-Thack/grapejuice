import json
from dataclasses import dataclass, asdict


@dataclass
class UninstallationParameters:
    remove_prefix: bool


def go(parameters: UninstallationParameters):
    assert parameters and isinstance(parameters, UninstallationParameters), "Programmer error: Invalid params argument"

    print("Uninstalling Grapejuice, parameters: ", json.dumps(asdict(parameters), indent=2))
