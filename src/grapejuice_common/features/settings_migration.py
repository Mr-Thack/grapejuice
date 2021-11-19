import logging
import os
import shutil
from dataclasses import asdict
from typing import Dict

from grapejuice_common import paths
from grapejuice_common.features.settings import k_wineprefixes

migration_index = dict()


def register_migration(version_from: int, version_to: int):
    def decorator(migration_function):
        migration_index[(version_from, version_to)] = migration_function

        return migration_function

    return decorator


# Keep migrations between 0 and 1 even though they don't do anything
# Having these run is an indicator that the feature is working

@register_migration(0, 1)
def migration_one(_settings: Dict):
    log = logging.getLogger(migration_one.__name__)
    log.info("Migration one application")


@register_migration(1, 0)
def undo_migration_one(_settings: Dict):
    log = logging.getLogger(undo_migration_one.__name__)
    log.info("Migration one undo")


@register_migration(1, 2)
def upgrade_wineprefix(settings: Dict):
    from grapejuice_common.wine.wine_functions import create_player_prefix_model, create_studio_prefix_model

    prefixes = settings.get(k_wineprefixes, [])

    if len(prefixes) > 0:
        return

    new_player_prefix = create_player_prefix_model(settings)
    new_studio_prefix = create_studio_prefix_model(settings)
    prefixes.extend(list(map(asdict, [new_player_prefix, new_studio_prefix])))

    settings[k_wineprefixes] = prefixes

    settings_to_delete = ("env", "dll_overrides", "wine_binary", "wine_home", "enabled_tweaks")

    for k in settings_to_delete:
        try:
            settings.pop(k)

        except KeyError:
            pass

    from grapejuice_common.features.wineprefix_migration import do_wineprefix_migration

    do_wineprefix_migration(
        legacy_wineprefix_path=paths.local_share_grapejuice() / "wineprefix",
        new_name_on_disk=new_player_prefix.name_on_disk
    )


@register_migration(2, 1)
def downgrade_wineprefix(settings: Dict):
    if len(settings[k_wineprefixes]) <= 0:
        return

    settings["env"] = settings[k_wineprefixes][0].get("env", dict())

    original_prefix_path = paths.local_share_grapejuice() / "wineprefix"
    new_prefix_path = paths.wineprefixes_directory() / settings[k_wineprefixes][0]["name_on_disk"]

    # Try to not destroy any prefixes
    if original_prefix_path.exists():
        if original_prefix_path.is_symlink():
            os.remove(original_prefix_path)

        else:
            n = 1
            while original_prefix_path.exists():
                original_prefix_path = paths.local_share_grapejuice() / f"wineprefix ({n})"
                n += 1

    original_prefix_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(new_prefix_path, original_prefix_path)
