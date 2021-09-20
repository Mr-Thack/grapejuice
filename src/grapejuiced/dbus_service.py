import dbus.service

from grapejuice_common.ipc.dbus_config import bus_name
from grapejuice_common.ipc.no_daemon_connection import NoDaemonModeConnection
from grapejuiced.__init__ import __version__


class DBusService(dbus.service.Object):
    def __init__(self, bus, path):
        super().__init__(bus, path, dbus.service.BusName(bus_name))
        self.version_string = str(__version__)

        self._dry_connection = NoDaemonModeConnection()

    @dbus.service.method(
        dbus_interface=bus_name,
        in_signature="s",
        out_signature=""
    )
    def EditLocalGame(self, path):
        self._dry_connection.edit_local_game(path)

    @dbus.service.method(
        dbus_interface=bus_name,
        in_signature="s",
        out_signature=""
    )
    def EditCloudGame(self, uri):
        self._dry_connection.edit_cloud_game(uri)

    @dbus.service.method(
        dbus_interface=bus_name,
        in_signature="",
        out_signature=""
    )
    def LaunchStudio(self):
        self._dry_connection.launch_studio()

    @dbus.service.method(
        dbus_interface=bus_name,
        in_signature="s",
        out_signature=""
    )
    def PlayGame(self, uri):
        self._dry_connection.play_game(uri)

    @dbus.service.method(
        dbus_interface=bus_name,
        in_signature="",
        out_signature=""
    )
    def ExtractFastFlags(self):
        self._dry_connection.extract_fast_flags()

    @dbus.service.method(
        dbus_interface=bus_name,
        in_signature="",
        out_signature="s"
    )
    def Version(self):
        return self._dry_connection.version()
