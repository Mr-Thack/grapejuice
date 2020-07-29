#!/usr/bin/env python3

import getpass
import io
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
from typing import List

TROUBLESHOOTER_VERSION = 2

TMP = os.path.join(os.path.sep, "tmp")
assert os.path.exists(TMP), "Fatal error: /tmp does not exist"
assert os.path.isdir(TMP), "Fatal error: /tmp is not a directory"

ORIGINAL_CWD = os.getcwd()
CWD = os.path.join(TMP, str(uuid.uuid4()))
WINEPREFIX_PATH = os.path.join(os.environ["HOME"], ".cache", "grapejuice-troubleshooter-wineprefix")

os.makedirs(CWD, exist_ok=True)
os.chdir(CWD)

CHECKLIST = list()
CHARSET = "UTF-8"
USERNAME = getpass.getuser()


def fatal_file():
    fp = open(os.path.join(TMP, "grapejuice-troubleshooter-fatal.log"), "a+")
    print(datetime.now(), file=fp)


class TextIOWrapperWrapper(io.TextIOWrapper):
    def write(self, __s: str) -> int:
        __s = __s.replace(USERNAME, "[REDACTED]")

        try:
            sys.stderr.write(__s)

        except Exception as e:
            with fatal_file() as fp:
                print(e.__class__.__name__, file=fp)
                print(e, file=fp)

        return super().write(__s)


OUTPUT_BUFFER = io.BytesIO()
TEXT_OUTPUT_BUFFER = TextIOWrapperWrapper(OUTPUT_BUFFER)


class Log:
    @staticmethod
    def info(*args, sep=" "):
        print("INFO: " + sep.join(list(map(str, args))), file=TEXT_OUTPUT_BUFFER)

    @staticmethod
    def error(*args, sep=" "):
        print("ERROR: " + sep.join(list(map(str, args))), file=TEXT_OUTPUT_BUFFER)


class CSVReport:
    _delimiter = ";"
    _header = ["Troubleshooting Function", "What are we checking?", "Status", "Fixes"]
    _rows = []

    @classmethod
    def add_row(cls, fun: str, what: str, status: bool, fixes: List[str]):
        if status:
            fixes = None

        cls._rows.append([fun, what, "PASS" if status else "FAIL", " :: ".join(fixes) if fixes else ""])

    @classmethod
    def to_string(cls):
        with io.TextIOWrapper(io.BytesIO()) as fp:
            print(cls._delimiter.join(cls._header), file=fp)
            for row in cls._rows:
                print(cls._delimiter.join(row), file=fp)

            fp.seek(0)
            s = fp.read()

        return s


def which(bin_name: str):
    if os.path.exists(bin_name):
        return os.path.abspath(bin_name)

    assert "PATH" in os.environ, "Your environment does not have $PATH. Your system is broken!"

    for path_dir in os.environ["PATH"].split(os.path.pathsep):
        path_dir: str = path_dir.strip()
        bin_path = os.path.join(path_dir, bin_name)

        if os.path.exists(bin_path) and not os.path.isdir(bin_path):
            return bin_path

    return None


class CommonFixes:
    fresh_wine = "Install a recent version of Wine (4.0 or higher)"
    wine64 = "Install a version of Wine that is capable of 64-bit support"
    c_tools = "Install C development tools for your distribution"
    follow_guide = "Follow the installation guide for your particular distribution." \
                   "https://gitlab.com/brinkervii/grapejuice/-/wikis/home"


def check(friendly_text: str, fixes: List[str] = None):
    def decorator(fn):
        def wrapper(*args, **kwargs) -> bool:
            Log.info("Performing check:", friendly_text)

            try:
                status = fn(*args, **kwargs)

                assert status is None or isinstance(status, bool), \
                    "Developer error: function does not return the right type\n" \
                    f"Expected bool or None, got {type(status)}"

                ok = status if isinstance(status, bool) else False

            except Exception as e:
                Log.error(e.__class__.__name__, e, sep=" ~ ")
                ok = False

            Log.info("OK: " if ok else "NOT_OK: ", friendly_text, fn.__name__, sep=" | ")

            CSVReport.add_row(fn.__name__, friendly_text, ok, fixes)

            return ok

        CHECKLIST.append(wrapper)

        return wrapper

    return decorator


class WinePrefix:
    _previous_env = dict()
    _wine: str
    _wine64: str

    def __init__(self):
        self._wine = which("wine")
        self._wine64 = which("wine64")

        self._set("WINEPREFIX", WINEPREFIX_PATH)
        self._set("WINEARCH", "win64")

    def _set(self, k, v):
        if k in os.environ:
            self._previous_env[k] = os.environ[k]

        else:
            self._previous_env[k] = False

        Log.info("Setting environment variable", k, v)

        os.environ[k] = v

    def __del__(self):
        for k, v in self._previous_env.items():
            Log.info("Restoring environment variable", k, v)

            if isinstance(v, str):
                os.environ[k] = v

            elif isinstance(v, bool):
                os.environ.pop(k)

            else:
                raise RuntimeError(f"Invalid environment variable type: {type(v)}")

    def run(self, cmd: List[str]) -> str:
        cmd = [self._wine, *cmd]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        try:
            while proc.returncode is None:
                proc.poll()
                time.sleep(0.1)

        except subprocess.CalledProcessError:
            pass

        output = proc.stdout.read().decode(CHARSET) if proc.stdout else "-- NO STDOUT --"
        err = proc.stderr.read().decode(CHARSET) if proc.stderr else "-- NO STDERR --"

        Log.info("Wine logs: ", err, "\n\n")

        return output


def c_compilers():
    compilers = ["gcc", "clang"]
    if "CC" in os.environ:
        compilers.append(os.environ["CC"])

    compilers = list(filter(lambda cc: not not cc, map(which, compilers)))
    return compilers


def pkg_config(pkg: str, cflags: bool = True, libs: bool = True):
    cmd = ["pkg-config", pkg]

    if cflags:
        cmd.append("--cflags")

    if libs:
        cmd.append("--libs")

    output = subprocess.check_output(cmd)
    output = output.decode(CHARSET).strip()

    Log.info(cmd, output, sep=" -> ")

    return output


@check("Log troubleshooter version")
def log_troubleshooter_version():
    Log.info(TROUBLESHOOTER_VERSION)

    return True


@check("Log directory info")
def log_cwd():
    Log.info("ORIGINAL_CWD", ORIGINAL_CWD)
    Log.info("CWD", CWD)

    assert os.path.isdir(ORIGINAL_CWD), "The original CWD is not a directory!"
    assert os.path.isdir(CWD), "The current working directory is not a directory?!!?!!one"

    return True


@check("Are we running in Python 3?", fixes=["Run the script with Python3"])
def is_python3():
    Log.info("Version info =", sys.version_info)
    Log.info("Version =", sys.version)
    Log.info("API Version =", sys.api_version)

    return sys.version_info.major == 3


@check("Are we running in at least python 3.7?", fixes=["Install a version of Python that is at least 3.7"])
def have_python37():
    return sys.version_info.major == 3 and sys.version_info.minor >= 7


UNAME = which("uname")
if UNAME is not None:
    Log.info("Found uname:", UNAME)


    @check("Are we on linux?", fixes=["Use the OS Grapejuice was meant for"])
    def on_linux():
        out = subprocess.check_output([UNAME]).decode(CHARSET).strip()
        Log.info(out)
        answer = out.lower().startswith("linux")

        if answer:
            out = subprocess.check_output([UNAME, "-r"]).decode(CHARSET).strip()
            Log.info("Kernel version:", out)

        return answer

else:
    Log.error("Could not find uname")

OS_RELEASE = os.path.join(os.path.sep, "etc", "os-release")


@check("Do we have the OS release file on the system?", fixes=["Run Grapejuice on an LSB compatible distribution."])
def have_os_release():
    exists = os.path.exists(OS_RELEASE)
    if exists:
        with open(OS_RELEASE, "r") as fp:
            Log.info("OS Release contents:\n", fp.read())

    return exists


LSCPU = which("lscpu")

if LSCPU is not None:
    Log.info("Found lscpu:", LSCPU)


    @check("Do we have a compatible CPU?")
    def have_compatible_cpu():
        ptn = re.compile(r"Architecture:\s*(.*)")
        out = subprocess.check_output([LSCPU]).decode(CHARSET).strip()

        Log.info("CPU Info:\n", out)

        for line in out.split("\n"):
            match = ptn.search(line)
            if match:
                return match.group(1).strip() == "x86_64"

        return False

else:
    Log.info("lscpu could not be found, so we cannot check for the CPU architecture")


@check("Do we have a compiler?", fixes=[CommonFixes.follow_guide, "Install a compatible C compiler"])
def have_compiler():
    return len(c_compilers()) > 0


@check("Do we have pip or pip3?", fixes=[CommonFixes.follow_guide, "Install pip for Python 3"])
def have_pip():
    pip = which("pip")
    pip3 = which("pip3")

    Log.info("pip:", pip)
    Log.info("pip3:", pip3)

    return (pip or pip3) is not None


@check("Do we have pkg-config?", fixes=[CommonFixes.follow_guide, CommonFixes.c_tools])
def have_pkg_config():
    return which("pkg-config") is not None


@check("Are the native libraries for cairo installed?",
       fixes=[CommonFixes.follow_guide, "Install the cairo development packages for your distribution"])
def have_cairo_natives():
    return pkg_config("cairo") is not None


@check("Are the native libraries dbus installed?",
       fixes=[CommonFixes.follow_guide, "Install the dbus development packages for your distribution"])
def have_dbus_natives():
    return pkg_config("dbus-1") is not None


@check("Can we update the GTK icon cache?",
       fixes=[CommonFixes.follow_guide, "Install the GTK+ icon utilities for your distribution"])
def can_update_icon_cache():
    return which("gtk-update-icon-cache") is not None


@check("Can we update the desktop file database?",
       fixes=[CommonFixes.follow_guide, "Install the freedesktop database utilities for your distribution"])
def can_update_desktop_database():
    return which("update-desktop-database") is not None


@check("Do we have XDG mime?", fixes=[CommonFixes.follow_guide, "Install the XDG utilities for your distribution"])
def have_xdg_mime():
    return which("xdg-mime") is not None


@check("Do have have GObject?",
       fixes=[CommonFixes.follow_guide, "Install the GObject development packages for your distribution"])
def have_gobject():
    return pkg_config("gobject-2.0") is not None


@check("Do we have GObject introspection?",
       fixes=[CommonFixes.follow_guide, "Install the GObject introspection development packages for your distribution"])
def have_gobject_introspection():
    return pkg_config("gobject-introspection-1.0") is not None


@check("Do we have GTK3?",
       fixes=[CommonFixes.follow_guide, "Install the GTK+3 development packages for your distribution"])
def have_gtk_3():
    return pkg_config("gtk+-3.0") is not None


@check("Do we have git?", fixes=[CommonFixes.follow_guide, "Install git"])
def have_git():
    return which("git") is not None


@check("Do we have wine?", fixes=[CommonFixes.follow_guide, "Install Wine"])
def have_wine():
    return which("wine") is not None


@check("Do we have 64-bit wine?", fixes=[CommonFixes.follow_guide, CommonFixes.wine64])
def have_wine64():
    return which("wine64") is not None


@check("Log Wine version")
def print_wine_version():
    Log.info(subprocess.check_output(["wine", "--version"]).decode(CHARSET).strip())
    return True


@check("Can we make a valid wineprefix?", fixes=[CommonFixes.wine64])
def can_make_valid_prefix():
    prefix = WinePrefix()
    out = prefix.run(["winecfg", "/?"])
    Log.info(out)
    del prefix

    error_ptn = re.compile(r".*?:\s*WINEARCH set to win64 but .*?is a 32-bit installation.*")
    assert error_ptn, "Couldn't compile the pattern that checks for a 64-bit error"

    match = error_ptn.search(out)
    if match is None:
        return True

    return False


@check("Does Wine support Windows 10?", fixes=[CommonFixes.fresh_wine])
def wine_supports_windows_10():
    prefix = WinePrefix()
    try:
        out = prefix.run(["winecfg", "/v", "win10"])
        Log.info(out)

    except Exception as e:
        Log.error(e)

    del prefix

    return True


@check("Can we access the Grapejuice package?", fixes=[CommonFixes.follow_guide])
def have_grapejuice_package():
    try:
        from grapejuice import __version__
        Log.info("Grapejuice version:", __version__)

        return True

    except ImportError as e:
        Log.error(e)
        return False


def main():
    n_passed = sum(map(lambda f: f(), CHECKLIST))
    Log.info(f"{n_passed}/{len(CHECKLIST)} passed")

    TEXT_OUTPUT_BUFFER.seek(0)
    report = TEXT_OUTPUT_BUFFER.read()

    with open("/tmp/grapejuice-report.csv", "w+") as fp:
        print(CSVReport.to_string(), file=fp)
        print("", file=fp)
        print("""
##################
### LOG OUTPUT ###
##################
        """, file=fp)
        print(report, file=fp)

    if os.path.exists(WINEPREFIX_PATH) and os.path.isdir(WINEPREFIX_PATH):
        Log.info("Removing wineprefix", WINEPREFIX_PATH)
        shutil.rmtree(WINEPREFIX_PATH)

    if os.path.exists(CWD):
        Log.info("Removing", CWD)

        os.chdir(ORIGINAL_CWD)
        shutil.rmtree(CWD)

    sys.exit(0 if n_passed == len(CHECKLIST) else 1)


main()
