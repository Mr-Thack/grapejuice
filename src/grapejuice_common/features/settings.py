import json
import logging
import uuid
from pathlib import Path
from typing import Dict, List

from grapejuice_common import variables
from grapejuice_common.features import wineprefix_configuration_model
from grapejuice_common.features.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.wine.wineprefix import Wineprefix
from grapejuice_common.wine.wineprefix_hints import WineprefixHint

LOG = logging.getLogger(__name__)

CURRENT_SETTINGS_VERSION = 2

k_version = "__version__"  # Magic variable gets underscores
k_show_fast_flag_warning = "show_fast_flag_warning"
k_wine_binary = "wine_binary"
k_dll_overrides = "dll_overrides"
k_no_daemon_mode = "no_daemon_mode"
k_release_channel = "release_channel"
k_disable_updates = "disable_updates"
k_wineprefixes = "wineprefixes"
k_enabled_tweaks = "enabled_tweaks"
k_ignore_wine_version = "ignore_wine_version"


def default_settings() -> Dict[str, any]:
    return {
        k_version: CURRENT_SETTINGS_VERSION,
        k_show_fast_flag_warning: True,
        k_wine_binary: "",
        k_no_daemon_mode: True,
        k_release_channel: "master",
        k_disable_updates: False,
        k_ignore_wine_version: False,
        k_wineprefixes: [{
            "id": str(uuid.uuid4()),
            "priority": 0,
            "name_on_disk": "default",
            "wine_home": "",
            k_dll_overrides: "ucrtbase=n,b;api-ms-win-crt-private-l1-1-0=n,b",
            "env": {},
            "hints": [
                WineprefixHint.studio.value,
                WineprefixHint.player.value
            ]
        }]
    }


class UserSettings:
    _settings_object: Dict[str, any] = None
    _location: Path = None

    def __init__(self, file_location=variables.grapejuice_user_settings()):
        self._location = file_location
        self.load()

    def perform_migrations(self, desired_migration_version: int = CURRENT_SETTINGS_VERSION):
        if self.version == desired_migration_version:
            LOG.debug(f"Settings file is up to date at version {self.version}")
            return

        a = self.version
        LOG.info(f"Performing migration from {a} to{CURRENT_SETTINGS_VERSION}")

        direction = 1 if desired_migration_version > a else -1

        for x in range(a + direction, desired_migration_version + direction, direction):
            index = (a, x)
            LOG.info(f"Migration index {index}")
            from grapejuice_common.features.settings_migration import migration_index

            migration_function = migration_index.get(index, None)

            if callable(migration_function):
                LOG.info(f"Applying migration {index}: {migration_function}")
                migration_function(self._settings_object)

                LOG.info(f"Applying and saving new settings version {x}")
                self.set(k_version, x, save=True)

            else:
                LOG.warning(f"Migration {index} is invalid")

            a = x

    @property
    def version(self) -> int:
        return self.get(k_version, 0)

    @property
    def raw_wineprefixes_sorted(self) -> List[Dict]:
        return list(sorted(
            self._settings_object.get(k_wineprefixes),
            key=lambda wp: wp.get("priority", 999)
        ))

    @property
    def parsed_wineprefixes_sorted(self) -> List[WineprefixConfigurationModel]:
        return list(map(wineprefix_configuration_model.from_json, self.raw_wineprefixes_sorted))

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
                        # Do not touch magic variables here
                        if k.startswith("__") and k.endswith("__"):
                            continue

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

        self.perform_migrations()

        self._settings_object[k_wineprefixes] = self.raw_wineprefixes_sorted

    def save(self):
        LOG.debug(f"Saving settings file to '{self._location}'")

        with self._location.open("w+") as fp:
            self._settings_object = {
                **default_settings(),
                **(self._settings_object or {})
            }

            json.dump(self._settings_object, fp, indent=2)

    def save_wineprefix(self, prefix: Wineprefix):
        did_update = False

        for prefix_configuration in self._settings_object.get(k_wineprefixes, []):
            if prefix_configuration.get("id") == prefix.configuration.id:
                for k, v in prefix.configuration.user_configuration_object.items():
                    prefix_configuration[k] = v
                    did_update = True

        if did_update:
            self.save()


current_settings = UserSettings()
