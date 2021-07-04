import atexit
import logging
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from string import Template
from subprocess import DEVNULL
from typing import List, Union

from grapejuice_common import variables
from grapejuice_common.logs.log_util import log_on_call, log_function

LOG = logging.getLogger(__name__)

space_version_ptn = re.compile(r"wine-(.+?)\s+")
non_space_version_ptn = re.compile(r"wine-(.+)")
space = " "

open_fds = []


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


processes: List[ProcessWrapper] = []
is_polling = False


@log_on_call("Preparing for Wine")
def prepare():
    from grapejuice_common.features.settings import current_settings
    from grapejuice_common.features import settings

    prefix_dir = variables.wineprefix_dir()

    user_env = current_settings.get(settings.k_environment_variables, {})
    apply_env = {
        "WINEDLLOVERRIDES": current_settings.get(settings.k_dll_overrides),
        **user_env,
        "WINEPREFIX": prefix_dir,
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

    if not os.path.exists(prefix_dir):
        os.makedirs(prefix_dir)


@log_on_call("Running Wine configuration")
def winecfg():
    prepare()
    run_exe("winecfg", run_async=True)


@log_on_call("Running registry editor")
def regedit():
    prepare()
    run_exe("regedit", run_async=True)


@log_on_call("Running Windows Explorer")
def explorer():
    prepare()
    run_exe("explorer", run_async=True)


def load_registry_file(srcfile, prepare_wine: bool = True):
    LOG.info(f"Loading registry file {srcfile} into the wineprefix")

    if prepare_wine:
        prepare()

    target_filename = str(int(time.time())) + ".reg"
    target_path = os.path.join(variables.wine_temp(), target_filename)
    shutil.copyfile(srcfile, target_path)

    winreg = "C:\\windows\\temp\\{}".format(target_filename)
    run_exe("regedit", "/S", winreg, run_async=False, use_wine64=False)
    run_exe("regedit", "/S", winreg, run_async=False, use_wine64=True)

    os.remove(target_path)


def load_patched_registry_files(source: Path, patches: dict = None):
    prepare()

    target_filename = str(int(time.time())) + ".reg"
    target_path = Path(variables.wine_temp()) / target_filename

    with source.open("r") as fp:
        template = Template(fp.read())

    with target_path.open("w+") as fp:
        fp.write(template.safe_substitute(patches))

    winreg = "C:\\windows\\temp\\{}".format(str(target_filename))
    run_exe("regedit", "/S", winreg, run_async=False, use_wine64=False)
    run_exe("regedit", "/S", winreg, run_async=False, use_wine64=True)

    os.remove(target_path)


@log_on_call("Running Winetricks")
def wine_tricks():
    prepare()

    processes.append(ProcessWrapper(
        subprocess.Popen(["winetricks"])
    ))

    poll_processes()


@log_on_call("Disabling MIME associations in wineprefix")
def disable_mime_assoc():
    load_registry_file(os.path.join(variables.assets_dir(), "disable_mime_assoc.reg"))


def set_roblox_document_path():
    src_path = Path(variables.assets_dir()) / "roblox_documents_folder.reg"
    patches = dict()

    documents_dir = "Z:" + variables.xdg_documents().replace("/", "\\\\")
    patches["DOCUMENTS_DIR"] = documents_dir
    LOG.info(f"Setting the roblox documents directory to '{documents_dir}'")

    load_patched_registry_files(src_path, patches)


@log_on_call("Sandboxing user directories in the wineprefix")
def sandbox():
    user_dir = variables.wine_user()

    if os.path.exists(user_dir) and os.path.isdir(user_dir):
        for file in os.listdir(user_dir):
            p = os.path.join(user_dir, file)

            if os.path.islink(p):
                LOG.info(f"Sandboxing {file}")
                os.remove(p)
                os.makedirs(p, exist_ok=True)


@log_on_call("Configuring the wineprefix")
def configure_prefix():
    disable_mime_assoc()
    sandbox()
    set_roblox_document_path()


@log_on_call("Creating the wineprefix")
def create_prefix():
    configure_prefix()


@log_function
def prefix_exists():
    return os.path.exists(variables.wineprefix_dir())


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

    p = subprocess.Popen(command, stdin=DEVNULL, stdout=sys.stdout, stderr=sys.stderr)
    wrapper = ProcessWrapper(p, on_exit=post_run_function)

    processes.append(wrapper)
    poll_processes()

    return wrapper


@log_function
def run_exe(
    exe_path: Union[Path, str],
    *args,
    run_async=False,
    use_wine64=False,
    post_run_function: callable = None
) -> Union[ProcessWrapper, None]:
    from grapejuice_common.features.settings import current_settings
    from grapejuice_common.features import settings

    prepare()
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
    global is_polling

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


atexit.register(close_fds)
