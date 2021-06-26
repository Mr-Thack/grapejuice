from grapejuice_common.features import settings

connection = None


def dbus_connection():
    global connection

    if connection is None:
        from grapejuice_common.features.settings import current_settings

        if current_settings.get(settings.k_no_daemon_mode, True):
            from grapejuice_common.ipc.no_daemon_connection import NoDaemonModeConnection
            connection = NoDaemonModeConnection()

        else:
            from grapejuice_common.ipc.dbus_connection import DBusConnection
            connection = DBusConnection()

    return connection
