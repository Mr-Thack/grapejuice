import atexit
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Union, List

from grapejuice_common import variables
from grapejuice_common.logs.log_util import log_function
from grapejuice_common.util.string_util import non_empty_string
from grapejuice_common.wine.wineprefix_configuration import WineprefixConfiguration
from grapejuice_common.wine.wineprefix_paths import WineprefixPaths

LOG = logging.getLogger(__name__)


class ProcessWrapper:
    on_exit: callable = None

    def __init__(self, proc: subprocess.Popen, on_exit: callable = None):
        self.proc = proc
        self.on_exit = on_exit

    @property
    def exited(self):
        proc = self.proc

        if proc.returncode is None:
            proc.poll()

        return proc.returncode is not None

    def kill(self):
        if not self.exited:
            os.kill(self.proc.pid, signal.SIGINT)

    def __del__(self):
        del self.proc


open_fds = []

processes: List[ProcessWrapper] = []
is_polling = False


@log_function
def _poll_processes() -> bool:
    """
    Makes sure zombie launchers are taken care of
    :return: Whether or not processes remain
    """
    global is_polling
    exited = []

    for proc in processes:
        if proc.exited:
            exited.append(proc)

            if proc.proc.returncode != 0:
                LOG.error(f"Process returned with non-zero exit code {proc.proc.returncode}")

    for proc in exited:
        processes.remove(proc)

        if callable(proc.on_exit):
            proc.on_exit()

        del proc

    processes_left = len(processes) > 0
    if not processes_left:
        is_polling = False
        LOG.info("No processes left to poll, exiting thread")

    return processes_left


def poll_processes():
    if is_polling:
        return

    LOG.info("Starting polling thread")

    from gi.repository import GObject
    GObject.timeout_add(100, _poll_processes)


def close_fds(*_, **__):
    LOG.info("Closing fds")

    for fd in open_fds:
        fd.close()

    open_fds.clear()


@log_function
def run_exe_no_daemon(
    command: List[str],
    exe_name: str,
    run_async: bool,
    post_run_function: callable = None
) -> Union[ProcessWrapper, None]:
    LOG.info("Running in no_daemon_mode")

    log_dir = Path(variables.logging_directory())
    os.makedirs(log_dir, exist_ok=True)

    LOG.info("Opening log fds")

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    stdout_path = log_dir / f"{ts}_{exe_name}_stdout.log"
    stderr_path = log_dir / f"{ts}_{exe_name}_stderr.log"

    stdout_fd = stdout_path.open("wb+")
    stderr_fd = stderr_path.open("wb+")

    open_fds.extend((stdout_fd, stderr_fd))

    if run_async:
        LOG.info("Running process asynchronously")

        wrapper = ProcessWrapper(
            subprocess.Popen(
                command,
                stdout=stdout_fd,
                stderr=stderr_fd
            ),
            on_exit=post_run_function
        )

        processes.append(wrapper)
        poll_processes()

        return wrapper

    else:
        LOG.info("Running process synchronously")

        subprocess.call(
            command,
            stdout=stdout_fd,
            stderr=stderr_fd
        )

        if callable(post_run_function):
            post_run_function()

        return None


@log_function
def run_exe_in_daemon(command: List[str], post_run_function: callable = None) -> ProcessWrapper:
    LOG.info("Running process for daemon mode")

    p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=sys.stdout, stderr=sys.stderr)
    wrapper = ProcessWrapper(p, on_exit=post_run_function)

    processes.append(wrapper)
    poll_processes()

    return wrapper


DLL_OVERRIDE_SEP = ";"


def default_dll_overrides() -> List[str]:
    return [
        "dxdiagn=",  # Disable DX9 warning
        "winemenubuilder.exe="  # Prevent Roblox from making shortcuts
    ]


class WineprefixCoreControl:
    _paths: WineprefixPaths
    _configuration: WineprefixConfiguration

    def __init__(self, paths: WineprefixPaths, configuration: WineprefixConfiguration):
        self._paths = paths
        self._configuration = configuration

    def prepare_for_launch(self):
        pco = self._configuration.program_configuration_object

        user_env = pco.get("env", dict())
        dll_overrides = list(filter(non_empty_string, pco.get("dll_overrides", "").split(DLL_OVERRIDE_SEP)))
        dll_overrides.extend(default_dll_overrides())

        apply_env = {
            "WINEDLLOVERRIDES": DLL_OVERRIDE_SEP.join(dll_overrides),
            **user_env,
            "WINEPREFIX": str(self._paths.base_directory),
            "WINEARCH": "win64"
        }

        # Variables in os.environ take priority
        for k, v in user_env.items():
            apply_env[k] = os.environ.get(k, v)

        # Wine generates giant logs for some people
        # Setting WINEDEBUG to -all *should* fix it
        if "WINEDEBUG" not in apply_env:
            apply_env["WINEDEBUG"] = "-all"

        # Apply env
        for k, v in apply_env.items():
            os.environ[k] = v

        if not os.path.exists(self._paths.base_directory):
            self._paths.base_directory.mkdir(parents=True)

    def load_registry_file(
        self,
        registry_file: Path,
        prepare_wine: bool = True
    ):
        LOG.info(f"Loading registry file {registry_file} into the wineprefix")

        if prepare_wine:
            self.prepare_for_launch()

        target_filename = str(int(time.time())) + ".reg"
        target_path = self._paths.temp_directory / target_filename
        shutil.copyfile(registry_file, target_path)

        winreg = f"C:\\windows\\temp\\{target_filename}"
        self.run_exe("regedit", "/S", winreg, run_async=False, use_wine64=False)
        self.run_exe("regedit", "/S", winreg, run_async=False, use_wine64=True)

        os.remove(target_path)

    def load_patched_registry_files(
        self,
        registry_file: Path,
        patches: dict = None
    ):
        self.prepare_for_launch()

        target_filename = str(int(time.time())) + ".reg"
        target_path = self._paths.temp_directory / target_filename

        with registry_file.open("r") as fp:
            template = Template(fp.read())

        with target_path.open("w+") as fp:
            fp.write(template.safe_substitute(patches))

        winreg = f"C:\\windows\\temp\\{target_filename}"
        self.run_exe("regedit", "/S", winreg, run_async=False, use_wine64=False)
        self.run_exe("regedit", "/S", winreg, run_async=False, use_wine64=True)

        os.remove(target_path)

    def disable_mime_associations(self):
        self.load_registry_file(variables.assets_dir() / "disable_mime_assoc.reg")

    def sandbox(self):
        user_dir = self._paths.user_directory

        if user_dir.exists() and user_dir.is_dir():
            for file in user_dir.glob("*"):
                if file.is_symlink():
                    LOG.info(f"Sandboxing {file}")
                    os.remove(file)
                    os.makedirs(file, exist_ok=True)

    def configure_prefix(self):
        self.disable_mime_associations()
        self.sandbox()

        # TODO: Set Roblox document path? Is this still required?

    def create_prefix(self):
        self.configure_prefix()

    def run_exe(
        self,
        exe_path: Union[Path, str],
        *args,
        run_async=False,
        use_wine64=False,
        post_run_function: callable = None
    ) -> Union[ProcessWrapper, None]:
        from grapejuice_common.features.settings import current_settings
        from grapejuice_common.features import settings

        self.prepare_for_launch()
        LOG.info("Prepared Wine.")

        if isinstance(exe_path, Path):
            exe_path_string = str(exe_path.resolve())
            exe_name = exe_path.name

        elif isinstance(exe_path, str):
            exe_path_string = exe_path
            exe_name = exe_path.split(os.path.sep)[-1]

        else:
            raise ValueError(f"Invalid value type for exe_path: {type(exe_path)}")

        LOG.info(f"Resolved exe path to {exe_path_string}")

        wine_binary = variables.wine_binary_64() if use_wine64 else variables.wine_binary()
        command = [wine_binary, exe_path_string, *args]

        if current_settings.get(settings.k_no_daemon_mode):
            return run_exe_no_daemon(command, exe_name, run_async, post_run_function=post_run_function)

        else:
            return run_exe_in_daemon(command, post_run_function=post_run_function)


atexit.register(close_fds)