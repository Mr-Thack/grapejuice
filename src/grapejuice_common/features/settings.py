import json
import logging
from pathlib import Path
from typing import Dict

from grapejuice_common import variables

LOG = logging.getLogger(__name__)

k_show_fast_flag_warning = "show_fast_flag_warning"
k_wine_binary = "wine_binary"
k_dll_overrides = "dll_overrides"
k_no_daemon_mode = "no_daemon_mode"
k_release_channel = "release_channel"
k_environment_variables = "env"


def default_settings() -> Dict[str, any]:
    return {
        k_show_fast_flag_warning: True,
        k_wine_binary: "",
        k_dll_overrides: "ucrtbase=n,b;api-ms-win-crt-private-l1-1-0=n,b;dxdiagn=;winemenubuilder.exe=",
        k_no_daemon_mode: True,
        k_release_channel: "master",
        k_environment_variables: dict()
    }


class UserSettings:
    _settings_object: Dict[str, any] = None
    _location: Path = None

    def __init__(self, file_location=variables.grapejuice_user_settings()):
        self._location = file_location
        self.load()

    def get(self, key: str, default_value: any = None):
        if self._settings_object:
            return self._settings_object.get(key, default_value)

        return default_value

    def set(self, key: str, value: any, save: bool = False) -> any:
        self._settings_object[key] = value

        if save:
            self.save()

        return value

    def load(self):
        if self._location.exists():
            LOG.debug(f"Loading settings from '{self._location}'")

            try:
                save_settings = False

                with self._location.open("r") as fp:
                    self._settings_object = json.load(fp)

                    for k, v in default_settings().items():
                        if k not in self._settings_object:
                            self._settings_object[k] = v
                            save_settings = True

                if save_settings:
                    self.save()

            except json.JSONDecodeError as e:
                LOG.error(e)
                self._settings_object = default_settings()
                self.save()

        else:
            LOG.debug("There is no settings file present, going to save one")

            self.save()

    def save(self):
        LOG.debug(f"Saving settings file to '{self._location}'")

        with self._location.open("w+") as fp:
            self._settings_object = {
                **default_settings(),
                **(self._settings_object or {})
            }

            json.dump(self._settings_object, fp, indent=2)


current_settings = UserSettings()
