import os
import subprocess
import sys

from grapejuice import background
from grapejuice_common import winectrl, variables
from grapejuice_common.update_info_providers import UpdateInformationProvider


def install_roblox():
    from grapejuice_common.ipc.dbus_client import dbus_connection
    dbus_connection().install_roblox()


class DisableMimeAssociations(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__("Disabling Wine associations", **kwargs)

    def work(self) -> None:
        winectrl.disable_mime_assoc()


class InstallRoblox(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__("Installing Roblox", **kwargs)

    def work(self) -> None:
        install_roblox()


class SandboxWine(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__("Sandboxing the Wine prefix", **kwargs)

    def work(self) -> None:
        winectrl.sandbox()


class RunRobloxStudio(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__("Launching Roblox Studio", **kwargs)

    def work(self) -> None:
        from grapejuice_common.ipc.dbus_client import dbus_connection
        dbus_connection().launch_studio()


class ExtractFastFlags(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__("Extracting Fast Flags", **kwargs)

    def work(self) -> None:
        from grapejuice_common.ipc.dbus_client import dbus_connection
        dbus_connection().extract_fast_flags()


class OpenLogsDirectory(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__("Opening logs directory", **kwargs)

    def work(self) -> None:
        path = variables.logging_directory()
        os.makedirs(path, exist_ok=True)

        subprocess.check_call(["xdg-open", path])


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
