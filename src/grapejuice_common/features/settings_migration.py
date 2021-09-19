import logging
import shutil
from typing import Dict

from grapejuice_common import variables
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
    original_prefix_path = variables.local_share_grapejuice() / "wineprefix"
    new_prefix_path = variables.wineprefixes_directory() / settings[k_wineprefixes][0]["name_on_disk"]

    # Try to not destroy any prefixes
    if original_prefix_path.exists() and not new_prefix_path.exists():
        new_prefix_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(original_prefix_path, new_prefix_path)


@register_migration(2, 1)
def downgrade_wineprefix(settings: Dict):
    original_prefix_path = variables.local_share_grapejuice() / "wineprefix"
    new_prefix_path = variables.wineprefixes_directory() / settings[k_wineprefixes][0]["name_on_disk"]

    # Try to not destroy any prefixes
    if original_prefix_path.exists():
        n = 1
        while original_prefix_path.exists():
            original_prefix_path = variables.local_share_grapejuice() / f"wineprefix ({n})"
            n += 1

    original_prefix_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(new_prefix_path, original_prefix_path)
