import argparse
import logging
import random
import sys
from typing import Callable

import grapejuice_common.util
from grapejuice_common.gtk.gtk_stuff import gtk_boot
from grapejuice_common.ipc.dbus_client import dbus_connection
from grapejuice_common.logs import log_config
from grapejuice_common.logs.log_vacuum import vacuum_logs


def main_gui():
    def make_main_window():
        from grapejuice_common.logs import self_test
        self_test.post.run()

        from grapejuice.gui.main_window import MainWindow
        main_window = MainWindow()
        main_window.show()

    gtk_boot(make_main_window)


def func_gui(args):
    main_gui()


def func_player(args):
    def player_main():
        dbus_connection().play_game(grapejuice_common.util.prepare_uri(args.uri))

    gtk_boot(player_main, gtk_main=False)

    return 0


def func_app(*_):
    def player_main():
        import grapejuice_common.variables as v
        dbus_connection().play_game(grapejuice_common.util.prepare_uri(v.roblox_app_experience_url()))

    gtk_boot(player_main, gtk_main=False)

    return 0


def func_studio(args):
    uri = grapejuice_common.util.prepare_uri(args.uri)
    if uri:
        is_local = False
        if not uri.startswith("roblox-studio:"):
            uri = "Z:" + uri.replace("/", "\\")
            is_local = True

        if is_local:
            dbus_connection().edit_local_game(uri)
        else:
            dbus_connection().edit_cloud_game(uri)

    else:
        dbus_connection().launch_studio()


def func_install_roblox(args):
    from grapejuice_common import robloxctrl

    do_install = not (args.only_once and robloxctrl.locate_player_launcher())

    if do_install:
        robloxctrl.run_installer()


def func_uninstall_grapejuice(*_):
    from grapejuice_common import uninstall

    uninstall_grapejuice_response = input(
        "Are you sure you want to uninstall grapejuice? [y/N] "
    ).strip().lower()

    uninstall_grapejuice = (uninstall_grapejuice_response[0] == "y") if uninstall_grapejuice_response else False

    if uninstall_grapejuice:
        delete_prefix_response = input(
            "Remove the Wineprefix that contains your installation of Roblox Studio? This will cause all "
            "configuration of Roblox Studio to be permanently deleted! [n/Y] "
        ).strip().lower()

        delete_prefix = (delete_prefix_response[0] == "y") if delete_prefix_response else False

        params = uninstall.UninstallationParameters(delete_prefix, for_reals=True)
        uninstall.go(params)

        print("Grapejuice has been uninstalled, have a nice day!")

    else:
        print("Uninstallation aborted")


def run_daemon_instead(argv):
    from grapejuiced.__main__ import main as daemon_main
    daemon_main([sys.argv[0], *argv])

    return 0


def main(in_args=None):
    log_config.configure_logging("grapejuice")
    log = logging.getLogger(f"{__name__}/main")

    from grapejuice_common.features.settings import current_settings
    from grapejuice_common.update_info_providers import guess_relevant_provider

    update_info_provider = guess_relevant_provider()

    if current_settings:
        log.info("Loaded settings")

    if in_args is None:
        in_args = sys.argv

    if len(in_args) > 1:
        if in_args[1].lower() == "grapejuiced":
            return run_daemon_instead(in_args[2:])

    if random.randint(0, 10) == 5:
        print("beep beep")

    parser = argparse.ArgumentParser(prog="grapejuice", description="Manage Roblox on Linux")
    subparsers = parser.add_subparsers(title="subcommands", help="sub-command help")

    parser_gui = subparsers.add_parser("gui")
    parser_gui.set_defaults(func=func_gui)

    parser_player = subparsers.add_parser("player")
    parser_player.add_argument("uri", type=str, help="Your Roblox token to join a game")
    parser_player.set_defaults(func=func_player)

    parser_studio = subparsers.add_parser("studio")
    parser_studio.add_argument(
        "uri",
        nargs="?",
        type=str,
        help="The URI or file to open roblox studio with",
        default=None
    )

    parser_studio.set_defaults(func=func_studio)

    parser_install_roblox = subparsers.add_parser("install-roblox")
    parser_install_roblox.add_argument("--only-once", action="store_true")
    parser_install_roblox.set_defaults(func=func_install_roblox)

    if update_info_provider.can_update():
        parser_uninstall_grapejuice = subparsers.add_parser("uninstall")
        parser_uninstall_grapejuice.set_defaults(func=func_uninstall_grapejuice)

    parser_app = subparsers.add_parser("app")
    parser_app.set_defaults(func=func_app)

    args = parser.parse_args(in_args[1:])

    exit_code = 1

    if hasattr(args, "func"):
        f: Callable[[any], int] = getattr(args, "func")
        exit_code = f(args) or 0

    else:
        parser.print_help()

    try:
        log.info("Vacuuming logs")
        vacuum_logs()

    except Exception as e:
        # Vacuuming logs appears to break on some systems
        # So let's just catch any exception
        log.error(str(e))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
