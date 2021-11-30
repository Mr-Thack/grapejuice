import json
import logging
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from grapejuice_common import paths
from grapejuice_common.hardware_info import hardware_profile
from grapejuice_common.hardware_info.hardware_profile import HardwareProfile
from grapejuice_common.models import wineprefix_configuration_model
from grapejuice_common.models.wineprefix_configuration_model import WineprefixConfigurationModel

LOG = logging.getLogger(__name__)

CURRENT_SETTINGS_VERSION = 2

k_version = "__version__"  # Magic variable gets underscores
k_hardware_profile = "__hardware_profile__"

k_show_fast_flag_warning = "show_fast_flag_warning"
k_wine_binary = "wine_binary"
k_dll_overrides = "dll_overrides"
k_no_daemon_mode = "no_daemon_mode"
k_release_channel = "release_channel"
k_disable_updates = "disable_updates"
k_wineprefixes = "wineprefixes"
k_enabled_tweaks = "enabled_tweaks"
k_ignore_wine_version = "ignore_wine_version"
k_unsupported_settings = "unsupported_settings"


def default_settings() -> Dict[str, any]:
    return {
        k_version: 0,
        k_hardware_profile: None,
        k_show_fast_flag_warning: True,
        k_no_daemon_mode: True,
        k_release_channel: "master",
        k_disable_updates: False,
        k_ignore_wine_version: False,
        k_wineprefixes: [],
        k_unsupported_settings: dict()
    }


class UserSettings:
    _settings_object: Dict[str, any] = None
    _location: Path = None

    def __init__(self, file_location=paths.grapejuice_user_settings()):
        self._location = file_location
        self.load()

    def _perform_migrations(self, desired_migration_version: int = CURRENT_SETTINGS_VERSION):
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
    def hardware_profile(self) -> HardwareProfile:
        if self._profile_hardware():
            self.save()

        return HardwareProfile.from_dict(self._settings_object[k_hardware_profile])

    @property
    def raw_wineprefixes_sorted(self) -> List[Dict]:
        return list(sorted(
            self._settings_object.get(k_wineprefixes),
            key=lambda wp: wp.get("priority", 999)
        ))

    @property
    def parsed_wineprefixes_sorted(self) -> List[WineprefixConfigurationModel]:
        return list(map(wineprefix_configuration_model.from_json, self.raw_wineprefixes_sorted))

    def find_wineprefix(self, search_id: str) -> Optional[WineprefixConfigurationModel]:
        for prefix_configuration in self._settings_object.get(k_wineprefixes, []):
            if prefix_configuration["id"] == search_id:
                return WineprefixConfigurationModel(**prefix_configuration)

        return None

    def get(self, key: str, default_value: any = None):
        if self._settings_object:
            return self._settings_object.get(key, default_value)

        return default_value

    def set(self, key: str, value: any, save: bool = False) -> any:
        self._settings_object[key] = value

        if save:
            self.save()

        return value

    def _profile_hardware(self, always_profile: Optional[bool] = False) -> bool:
        saved_profile = None if always_profile else self._settings_object.get(k_hardware_profile, None)

        if saved_profile:
            from grapejuice_common.hardware_info.lspci import LSPci
            hardware_list = LSPci()

            should_profile_hardware = (hardware_list.graphics_id != saved_profile["graphics_id"]) or \
                                      (saved_profile.get("version", -1) != HardwareProfile.version)

        else:
            should_profile_hardware = True

        if should_profile_hardware:
            LOG.info("Going to profile hardware")
            profile = hardware_profile.profile_hardware()
            self._settings_object[k_hardware_profile] = profile.as_dict
            return True

        return False

    def load(self):
        save_settings = False

        if self._location.exists():
            LOG.debug(f"Loading settings from '{self._location}'")

            try:
                with self._location.open("r") as fp:
                    self._settings_object = json.load(fp)

                    # Make sure all the default settings are present
                    # Using a for loop because magic settings shouldn't be touched
                    for k, v in default_settings().items():
                        # Do not touch magic variables here
                        if k.startswith("__") and k.endswith("__"):
                            continue

                        if k not in self._settings_object:
                            self._settings_object[k] = v
                            save_settings = True

            except json.JSONDecodeError as e:
                LOG.error(e)

                self._settings_object = default_settings()
                save_settings = True

        else:
            LOG.info("There is no settings file present, going to save one")
            save_settings = True

        self._perform_migrations()

        save_settings = self._profile_hardware() or save_settings

        if save_settings:
            LOG.info("Saving settings after load, because something was wrong.")
            self.save()

    def save(self):
        LOG.debug(f"Saving settings file to '{self._location}'")

        # Sort wineprefixes before saving so the file order matches the UI
        self._settings_object[k_wineprefixes] = self.raw_wineprefixes_sorted

        # Store in value so its not called twice
        defaults = default_settings()

        # Preserve unsupported settings
        unsupported_setting_keys = set()

        for k, _ in self._settings_object.items():
            if k not in defaults:
                unsupported_setting_keys.add(k)

        for k in unsupported_setting_keys:
            self._settings_object[k_unsupported_settings][k] = self._settings_object.pop(k)

        # Perform actual save
        with self._location.open("w+") as fp:
            self._settings_object = {
                **defaults,
                **(self._settings_object or {})
            }

            json.dump(self._settings_object, fp, indent=2)

    def save_prefix_model(self, model: WineprefixConfigurationModel):
        did_update = False
        model_as_dict = asdict(model)

        # Extract and re-insert wineprefixes list in case it doesn't exist
        prefixes = self._settings_object.get(k_wineprefixes, [])

        if self.find_wineprefix(model.id) is None:
            prefixes.append(model_as_dict)
            did_update = True

        else:
            for prefix_configuration in prefixes:
                if prefix_configuration["id"] == model.id:
                    for k, v in model_as_dict.items():
                        prefix_configuration[k] = v

                    did_update = True

                # Prune products with no fast flags set
                if "fast_flags" in prefix_configuration:
                    for product_name in list(prefix_configuration["fast_flags"].keys()):
                        if len(prefix_configuration["fast_flags"][product_name]) <= 0:
                            prefix_configuration["fast_flags"].pop(product_name)

        self._settings_object[k_wineprefixes] = prefixes

        if did_update:
            self.save()

    def remove_prefix_model(self, model: WineprefixConfigurationModel):
        def keep_model(m: Dict):
            return m["id"] != model.id

        self._settings_object[k_wineprefixes] = list(
            filter(
                keep_model,
                self._settings_object.get(k_wineprefixes, [])
            )
        )

        self.save()

    def as_dict(self) -> Dict:
        return deepcopy(self._settings_object)


current_settings = UserSettings()
