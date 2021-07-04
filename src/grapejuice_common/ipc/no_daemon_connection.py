import logging

from grapejuice_common.ipc.i_dbus_connection import IDBusConnection

LOG = logging.getLogger(__name__)


class NoDaemonModeConnection(IDBusConnection):
    @property
    def connected(self):
        return True

    def launch_studio(self):
        from grapejuice_common import robloxctrl

        robloxctrl.run_studio()

    def play_game(self, uri):
        from grapejuice_common import robloxctrl

        def do_run():
            robloxctrl.run_player(uri)

        if robloxctrl.locate_player_launcher():
            do_run()

        else:
            robloxctrl.run_installer(post_install_function=do_run)

    def edit_local_game(self, place_path):
        from grapejuice_common import robloxctrl

        robloxctrl.run_studio(place_path, True)

    def edit_cloud_game(self, uri):
        from grapejuice_common import robloxctrl

        robloxctrl.run_studio(uri)

    def install_roblox(self):
        from grapejuice_common import robloxctrl

        robloxctrl.run_installer()

    def version(self):
        from grapejuiced import __version__

        return __version__

    def extract_fast_flags(self):
        from grapejuice_common import robloxctrl

        robloxctrl.fast_flag_extract()
