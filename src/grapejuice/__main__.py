import argparse
import logging
import sys
from typing import Callable

import grapejuice_common.util
from grapejuice_common.gtk.gtk_util import gtk_boot
from grapejuice_common.logs.log_vacuum import vacuum_logs


def handle_fatal_error(ex: Exception):
    print("Fatal error: " + str(ex))

    def make_exception_window():
        from grapejuice.windows.exception_viewer import ExceptionViewer
        window = ExceptionViewer(exception=ex, is_main=True)

        window.show()

    gtk_boot(make_exception_window)


def main_gui():
    def make_main_window():
        from grapejuice.windows.main_window import MainWindow
        window = MainWindow()
        window.show()

    gtk_boot(make_main_window)


def func_gui(_args):
    main_gui()


def func_player(args):
    def player_main():
        from grapejuice_common.ipc.dbus_client import dbus_connection
        from grapejuice_common.wine.wine_functions import get_player_wineprefix

        prefix = get_player_wineprefix()

        dbus_connection().play_game(
            prefix.configuration.id,
            grapejuice_common.util.prepare_uri(args.uri)
        )

    gtk_boot(player_main, gtk_main=False)

    return 0


def func_app(*_):
    def player_main():
        import grapejuice_common.variables as v
        from grapejuice_common.ipc.dbus_client import dbus_connection
        from grapejuice_common.wine.wine_functions import get_app_wineprefix

        prefix = get_app_wineprefix()

        dbus_connection().play_game(
            prefix.configuration.id,
            grapejuice_common.util.prepare_uri(v.roblox_app_experience_url())
        )

    gtk_boot(player_main, gtk_main=False)

    return 0


def func_studio(args):
    from grapejuice_common.wine.wine_functions import get_studio_wineprefix
    from grapejuice_common.ipc.dbus_client import dbus_connection

    prefix = get_studio_wineprefix()
    uri = grapejuice_common.util.prepare_uri(args.uri)

    if uri:
        is_local = False
        if not uri.startswith("roblox-studio:"):
            uri = "Z:" + uri.replace("/", "\\")
            is_local = True

        if is_local:
            dbus_connection().edit_local_game(prefix.configuration.id, uri)

        else:
            dbus_connection().edit_cloud_game(prefix.configuration.id, uri)

    else:
        dbus_connection().launch_studio(prefix.configuration.id)


def func_first_time_setup(_args):
    from grapejuice_common.features.settings import current_settings
    from grapejuice_common.errors import WineprefixNotFoundUsingHints
    from grapejuice_common.wine.wineprefix import Wineprefix
    from grapejuice_common.recipes.roblox_player_recipe import RobloxPlayerRecipe
    from grapejuice_common.wine.wine_functions import \
        get_player_wineprefix, \
        get_studio_wineprefix, \
        create_player_prefix_model, \
        create_studio_prefix_model

    log = logging.getLogger("first_time_setup")

    log.info("Retrieving settings as dict")
    settings_dict = current_settings.as_dict()

    log.info("Getting player Wineprefix")
    try:
        player_prefix = get_player_wineprefix()

    except WineprefixNotFoundUsingHints:
        log.info("Creating player Wineprefix")

        player_prefix_model = create_player_prefix_model(settings_dict)

        log.info("Saving player wineprefix to settings")
        current_settings.save_prefix_model(player_prefix_model)
        settings_dict = current_settings.as_dict()

        player_prefix = Wineprefix(player_prefix_model)

    log.info("Starting Roblox Player recipe")
    player_recipe = RobloxPlayerRecipe()
    if not player_recipe.exists_in(player_prefix):
        log.info("Roblox is not installed!")
        player_recipe.make_in(player_prefix)

    log.info("Getting studio Wineprefix")
    try:
        studio_prefix = get_studio_wineprefix()

    except WineprefixNotFoundUsingHints:
        log.info("Creating studio wineprefix")
        studio_prefix_model = create_studio_prefix_model(settings_dict)

        log.info("Saving studio Wineprefix to settings")
        current_settings.save_prefix_model(studio_prefix_model)

        studio_prefix = Wineprefix(studio_prefix_model)

    assert studio_prefix, "Studio Wineprefix was not created?!"

    log.info("Completed first time setup!")


def func_uninstall_grapejuice(*_):
    from grapejuice_common import uninstall

    uninstall_grapejuice_response = input(
        "Are you sure you want to uninstall grapejuice? [y/N] "
    ).strip().lower()

    uninstall_grapejuice = (uninstall_grapejuice_response[0] == "y") if uninstall_grapejuice_response else False

    if uninstall_grapejuice:
        delete_prefix_response = input(
            "Remove the Wineprefixes that contain your installations of Roblox? This will cause all "
            "configurations for Roblox to be permanently deleted! [n/Y] "
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


def _main(in_args=None):
    from grapejuice_common.logs import log_config

    log_config.configure_logging("grapejuice")
    log = logging.getLogger(f"{__name__}/main")

    from grapejuice_common.features.settings import current_settings
    from grapejuice_common.update_info_providers import guess_relevant_provider

    update_info_provider = guess_relevant_provider()

    if current_settings:
        current_settings.perform_migrations()
        log.info("Loaded and migrated settings")

    if in_args is None:
        in_args = sys.argv

    if len(in_args) > 1:
        if in_args[1].lower() == "grapejuiced":
            return run_daemon_instead(in_args[2:])

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

    parser_install_roblox = subparsers.add_parser("first-time-setup")
    parser_install_roblox.set_defaults(func=func_first_time_setup)

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


def main(in_args=None):
    try:
        return _main(in_args)

    except Exception as fatal_error:
        handle_fatal_error(fatal_error)
        return -1


if __name__ == "__main__":
    sys.exit(main())
