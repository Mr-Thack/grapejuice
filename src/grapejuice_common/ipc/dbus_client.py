connection = None


def dbus_connection():
    global connection

    if connection is None:
        from grapejuice_common.features.settings import settings

        if settings.no_daemon_mode:
            from grapejuice_common.ipc.no_daemon_connection import NoDaemonModeConnection
            connection = NoDaemonModeConnection()

        else:
            from grapejuice_common.ipc.dbus_connection import DBusConnection
            connection = DBusConnection()

    return connection
