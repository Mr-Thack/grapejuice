import argparse
import logging
import sys
from typing import Callable

from grapejuice_common.logs.log_vacuum import vacuum_logs


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

    parser_list_processes = subparsers.add_parser("top")
    parser_list_processes.add_argument("hint", type=str)
    parser_list_processes.set_defaults(func=func_list_processes)

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
