import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

from grapejuice_common import variables

LOG = logging.getLogger(__name__)

k_n_player_dialogs_remain = "n_player_dialogs_remain"
k_show_fast_flag_warning = "show_fast_flag_warning"
k_wine_binary = "wine_binary"
k_last_run = "last_run"


def default_settings() -> Dict[str, any]:
    return {
        k_n_player_dialogs_remain: 5,
        k_show_fast_flag_warning: True,
        k_wine_binary: "",
        k_last_run: datetime.utcnow().isoformat()
    }


class UserSettings:
    _settings_object: Dict[str, any] = None
    _location: Path = None

    def __init__(self, file_location=variables.grapejuice_user_settings()):
        self._location = file_location
        self.load()

    def __setattr__(self, key, value):
        if key.startswith("_"):
            super().__setattr__(key, value)

        else:
            self._settings_object[key] = value

    def __getattr__(self, item):
        return self._settings_object.get(item, None)

    def load(self):
        if self._location.exists():
            LOG.debug(f"Loading settings from '{self._location}'")

            try:
                with self._location.open("r") as fp:
                    self._settings_object = {
                        **default_settings(),
                        **json.load(fp)
                    }

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
            json.dump({
                **default_settings(),
                **(self._settings_object or {})
            }, fp, indent=2)


settings = UserSettings()
