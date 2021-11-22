import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from grapejuice import background
from grapejuice_common import paths
from grapejuice_common.update_info_providers import UpdateInformationProvider
from grapejuice_common.util import xdg_open
from grapejuice_common.wine.wineprefix import Wineprefix


class RunRobloxStudio(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__("Launching Roblox Studio", **kwargs)

        self._prefix = prefix

    def work(self) -> None:
        from grapejuice_common.ipc.dbus_client import dbus_connection
        dbus_connection().launch_studio(self._prefix.configuration.id)


class ExtractFastFlags(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__("Extracting Fast Flags", **kwargs)

        self._prefix = prefix

    def work(self) -> None:
        from grapejuice_common.ipc.dbus_client import dbus_connection

        should_extract_flags = True

        # Only check fast flags every x minutes, checking more often is overkill
        # This also reduces overall compute time used, yay!

        if paths.fast_flag_cache_location().exists():
            ten_minutes_ago = datetime.now() - timedelta(minutes=10)

            stat = os.stat(paths.fast_flag_cache_location())
            if stat.st_mtime > ten_minutes_ago.timestamp():
                should_extract_flags = False

        if should_extract_flags:
            dbus_connection().extract_fast_flags()

        else:
            time.sleep(1)  # Make it feel like Grapejuice is doing something


class OpenLogsDirectory(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__("Opening logs directory", **kwargs)

    def work(self) -> None:
        path = paths.logging_directory()
        path.mkdir(parents=True, exist_ok=True)

        subprocess.check_call(["xdg-open", str(path)])


class OpenConfigFile(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__("Opening configuration file", **kwargs)

    def work(self) -> None:
        subprocess.check_call(["xdg-open", str(paths.grapejuice_user_settings())])


class PerformUpdate(background.BackgroundTask):
    def __init__(self, update_provider: UpdateInformationProvider, reopen: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._update_provider = update_provider
        self._reopen = reopen

    def work(self) -> None:
        self._update_provider.do_update()

        if self._reopen:
            subprocess.Popen(["bash", "-c", f"{sys.executable} -m grapejuice gui & disown"], preexec_fn=os.setpgrp)

            from gi.repository import Gtk
            Gtk.main_quit()

            sys.exit(0)


class InstallRoblox(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(f"Installing Roblox in {prefix.configuration.display_name}", **kwargs)
        self._prefix = prefix

    def work(self):
        self._prefix.roblox.install_roblox()


class ShowDriveC(background.BackgroundTask):
    _path: Path

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(f"Opening Drive C in {prefix.configuration.display_name}", **kwargs)
        self._path = prefix.paths.drive_c

    def work(self):
        xdg_open(str(self._path))
