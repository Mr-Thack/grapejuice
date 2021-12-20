import atexit
import json
import logging
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Union, List, Dict

from grapejuice_common import variables, paths
from grapejuice_common.errors import HardwareProfilingError
from grapejuice_common.hardware_info.graphics_card import GPUVendor
from grapejuice_common.logs.log_util import log_function
from grapejuice_common.models.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.util.string_util import non_empty_string
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

    from grapejuice_common.logs.log_vacuum import remove_empty_logs
    remove_empty_logs()


@log_function
def run_exe_no_daemon(
    command: List[str],
    exe_name: str,
    run_async: bool,
    post_run_function: callable = None
) -> Union[ProcessWrapper, None]:
    LOG.info("Running in no_daemon_mode")

    log_dir = paths.logging_directory()
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


WINE_PROCESS_PTN = re.compile(r"^\s*([a-f0-9]+)\s+(\d+).*\'([\w.]+)\'")


@dataclass(frozen=True)
class WineProcess:
    pid: str
    threads: int
    image: str


DLL_OVERRIDE_SEP = ";"


def default_dll_overrides() -> List[str]:
    return [
        "dxdiagn=",  # Disable DX9 warning
        "winemenubuilder.exe="  # Prevent Roblox from making shortcuts
    ]


def _legacy_hardware_variables(configuration: WineprefixConfigurationModel):
    d = dict()
    if configuration.use_mesa_gl_override:
        d["MESA_GL_VERSION_OVERRIDE"] = "4.4"

    return d


class WineprefixCoreControl:
    _prefix_paths: WineprefixPaths
    _configuration: WineprefixConfigurationModel

    def __init__(self, prefix_paths: WineprefixPaths, configuration: WineprefixConfigurationModel):
        self._prefix_paths = prefix_paths
        self._configuration = configuration

    def wine_binary(self, arch="") -> str:
        LOG.info(f"Resolving wine binary for prefix {self._prefix_paths.base_directory}")

        wine_home_string = self._configuration.wine_home.strip()
        LOG.info(f"Wine home string: {wine_home_string}")

        if wine_home_string.startswith(f"~{os.path.sep}"):
            wine_home = Path(wine_home_string).expanduser()

        else:
            wine_home = Path(wine_home_string)

        LOG.info(f"Wine home is {wine_home}")

        # TODO: Replace assert statements with 'proper' errors

        assert wine_home.is_absolute(), f"Wine home '{wine_home}' is not an absolute path"
        assert wine_home.exists() and wine_home.is_dir(), f"Invalid wine_home: {wine_home}"

        if wine_home:
            wine_binary = wine_home / "bin" / f"wine{arch}"
            LOG.info(f"Resolved wine binary path: {wine_binary}")

            assert wine_binary.exists() and wine_binary.is_file(), f"Invalid wine binary: {wine_binary}"

            return str(wine_binary)

        else:
            return variables.system_wine_binary(arch)

    def wine_server(self) -> str:
        path = Path(self.wine_binary()).parent / "wineserver"
        assert path.exists(), f"Could not find wineserver at: {path}"

        return str(path)

    def wine_dbg(self) -> str:
        path = Path(self.wine_binary()).parent / "winedbg"
        assert path.exists(), f"Could not find winedbg at: {path}"

        return str(path)

    def _dri_prime_variables(self) -> Dict[str, str]:
        from grapejuice_common.features.settings import current_settings

        try:
            profile = current_settings.hardware_profile

        except HardwareProfilingError as e:
            LOG.error("Could not get hardware profile")
            LOG.error(e)

            return dict()

        prime_env = dict()

        if self._configuration.prime_offload_sink >= 0:
            sink = str(self._configuration.prime_offload_sink)

            prime_env = {"DRI_PRIME": sink}

            if profile.gpu_vendor is GPUVendor.NVIDIA:
                prime_env = {
                    **prime_env,
                    "__NV_PRIME_RENDER_OFFLOAD": sink,
                    "__VK_LAYER_NV_optimus": "NVIDIA_only",
                    "__GLX_VENDOR_LIBRARY_NAME": "nvidia"
                }

        LOG.info(f"PRIME environment variables: {json.dumps(prime_env)}")

        return prime_env

    def prepare_for_launch(self, accelerate_graphics: bool = False):
        user_env = self._configuration.env
        dll_overrides = list(filter(non_empty_string, self._configuration.dll_overrides.split(DLL_OVERRIDE_SEP)))
        dll_overrides.extend(default_dll_overrides())

        apply_env = {
            "WINEDLLOVERRIDES": DLL_OVERRIDE_SEP.join(dll_overrides),
            **user_env,
            "WINEPREFIX": str(self._prefix_paths.base_directory),
            "WINEARCH": "win64",
            **(self._dri_prime_variables() if accelerate_graphics else dict()),
            **_legacy_hardware_variables(self._configuration)
        }

        # Variables in os.environ take priority
        for k, v in user_env.items():
            apply_env[k] = os.environ.get(k, v)

        # Wine generates giant logs for some people
        # Setting WINEDEBUG to -all *should* fix it
        if "WINEDEBUG" not in apply_env:
            winedebug_string = "-all"

            if self._configuration.enable_winedebug:
                winedebug_string = ""

                configuration_winedebug_string = self._configuration.winedebug_string.strip()
                if configuration_winedebug_string:
                    winedebug_string = configuration_winedebug_string

            apply_env["WINEDEBUG"] = winedebug_string

        LOG.info("Applying environment: " + json.dumps(apply_env))

        # Apply env
        for k, v in apply_env.items():
            os.environ[k] = v

        if not os.path.exists(self._prefix_paths.base_directory):
            self._prefix_paths.base_directory.mkdir(parents=True)

    def load_registry_file(
        self,
        registry_file: Path,
        prepare_wine: bool = True
    ):
        LOG.info(f"Loading registry file {registry_file} into the wineprefix")

        if prepare_wine:
            self.prepare_for_launch()

        target_filename = str(int(time.time())) + ".reg"
        target_path = self._prefix_paths.temp_directory / target_filename
        target_path.parent.mkdir(parents=True, exist_ok=True)

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
        target_path = self._prefix_paths.temp_directory / target_filename

        with registry_file.open("r") as fp:
            template = Template(fp.read())

        with target_path.open("w+") as fp:
            fp.write(template.safe_substitute(patches))

        winreg = f"C:\\windows\\temp\\{target_filename}"
        self.run_exe("regedit", "/S", winreg, run_async=False, use_wine64=False)
        self.run_exe("regedit", "/S", winreg, run_async=False, use_wine64=True)

        os.remove(target_path)

    def disable_mime_associations(self):
        self.load_registry_file(paths.assets_directory() / "disable_mime_assoc.reg")

    def sandbox(self):
        user_dir = self._prefix_paths.user_directory

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
        accelerate_graphics: bool = False,
        post_run_function: callable = None
    ) -> Union[ProcessWrapper, None]:
        from grapejuice_common.features.settings import current_settings
        from grapejuice_common.features import settings

        self.prepare_for_launch(accelerate_graphics=accelerate_graphics)
        LOG.info("Prepared environment for wine")

        if isinstance(exe_path, Path):
            exe_path_string = str(exe_path.resolve())
            exe_name = exe_path.name

        elif isinstance(exe_path, str):
            exe_path_string = exe_path
            exe_name = exe_path.split(os.path.sep)[-1]

        else:
            raise ValueError(f"Invalid value type for exe_path: {type(exe_path)}")

        LOG.info(f"Resolved exe path to {exe_path_string}")

        wine_binary = self.wine_binary("64" if use_wine64 else "")
        command = [wine_binary, exe_path_string, *args]

        if current_settings.get(settings.k_no_daemon_mode):
            return run_exe_no_daemon(command, exe_name, run_async, post_run_function=post_run_function)

        else:
            return run_exe_in_daemon(command, post_run_function=post_run_function)

    def run_linux_command(self, command: str):
        self.prepare_for_launch()

        # TODO: Make commands use wine defined in prefix configuration
        run_exe_no_daemon([command], command, run_async=False)

    def kill_wine_server(self):
        self.prepare_for_launch()

        subprocess.check_call([self.wine_server(), "-k"])

    @property
    def process_list(self) -> List[WineProcess]:
        self.prepare_for_launch()

        the_list = []

        output = subprocess.check_output([self.wine_dbg(), "--command", "info proc"])
        output = output.decode("UTF-8")

        for line in output.split("\n"):
            match = WINE_PROCESS_PTN.search(line.strip())

            if match:
                the_list.append(WineProcess(
                    match.group(1),
                    int(match.group(2)),
                    match.group(3)
                ))

        return the_list


atexit.register(close_fds)
