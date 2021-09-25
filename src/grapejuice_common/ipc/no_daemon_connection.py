import logging

from grapejuice_common.ipc.i_dbus_connection import IDBusConnection
from grapejuice_common.wine.wine_functions import initialize_roblox_in_default_prefix

LOG = logging.getLogger(__name__)


class NoDaemonModeConnection(IDBusConnection):
    @property
    def connected(self):
        return True

    def launch_studio(self):
        from grapejuice_common.wine.wine_functions import get_studio_wineprefix

        prefix = get_studio_wineprefix()
        prefix.roblox.run_roblox_studio()

    def play_game(self, uri):
        from grapejuice_common.wine.wine_functions import get_player_wineprefix

        prefix = get_player_wineprefix()

        def do_run():
            prefix.roblox.run_roblox_player(uri)

        if prefix.roblox.roblox_player_launcher_path is not None:
            do_run()

        else:
            prefix.roblox.install_roblox(post_install_function=do_run)

    def edit_local_game(self, place_path):
        from grapejuice_common.wine.wine_functions import get_studio_wineprefix

        prefix = get_studio_wineprefix()
        prefix.roblox.run_roblox_studio(
            ide=True,
            uri=place_path
        )

    def edit_cloud_game(self, uri):
        from grapejuice_common.wine.wine_functions import get_studio_wineprefix

        prefix = get_studio_wineprefix()
        prefix.roblox.run_roblox_studio(uri)

    def version(self):
        from grapejuiced import __version__

        return __version__

    def extract_fast_flags(self):
        from grapejuice_common.wine.wine_functions import get_studio_wineprefix

        prefix = get_studio_wineprefix()
        prefix.roblox.extract_fast_flags()

    def install_roblox(self):
        initialize_roblox_in_default_prefix()
