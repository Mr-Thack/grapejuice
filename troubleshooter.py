#!/usr/bin/env python3

import getpass
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import uuid
from datetime import datetime
from typing import List, Union, Dict

TROUBLESHOOTER_VERSION = 9

TMP = os.path.join(os.path.sep, "tmp")
assert os.path.exists(TMP), "Fatal error: /tmp does not exist"
assert os.path.isdir(TMP), "Fatal error: /tmp is not a directory"

ORIGINAL_CWD = os.getcwd()
CWD = os.path.join(TMP, str(uuid.uuid4()))
WINEPREFIX_PATH = os.path.join(os.environ["HOME"], ".cache", "grapejuice-troubleshooter-wineprefix-{arch}")
USED_PREFIXES = set()

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
    def empty_row(cls):
        cls.add_row("", "", True, [])

    @classmethod
    def to_string(cls):
        with io.TextIOWrapper(io.BytesIO()) as fp:
            print(cls._delimiter.join(cls._header), file=fp)
            for row in cls._rows:
                print(cls._delimiter.join(row), file=fp)

            fp.seek(0)
            s = fp.read()

        return s


VARS = dict()


def report_var(k, v):
    VARS[k] = str(v)
    Log.info(f"Reporting variable:", k, v)
    return v


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
    wine32 = "Install a version of Wine that is capable of 32-bit support"
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

                if os.environ.get("DEBUGGING", "0").strip() == "1":
                    raise e

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
    _arch: str

    def __init__(self, arch: str = "win64", pfx: str = None, destroy_prefix: Union[bool, None] = False):
        self._wine = which("wine")
        self._wine64 = which("wine64")
        self._arch = arch

        if pfx is None:
            pfx = WINEPREFIX_PATH.format(arch=arch)

        if destroy_prefix is None:
            destroy_prefix = not os.path.exists(pfx)

        if destroy_prefix:
            USED_PREFIXES.add(pfx)

        self._set("WINEPREFIX", pfx)
        self._set("WINEARCH", self._arch)

    def _set(self, k, v):
        if k in os.environ:
            self._previous_env[k] = os.environ[k]

        else:
            self._previous_env[k] = False

        Log.info("Setting environment variable", k, v)

        os.environ[k] = v

    def __del__(self):
        for k, v in self._previous_env.items():
            if isinstance(v, str):
                Log.info("Restoring environment variable", k, v)
                os.environ[k] = v

            elif isinstance(v, bool):
                Log.info("Deleting environment variable", k)
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
    report_var("Troubleshooter Version", TROUBLESHOOTER_VERSION)

    return True


@check("Log directory info")
def log_cwd():
    report_var("ORIGINAL_CWD", ORIGINAL_CWD)
    report_var("CWD", CWD)

    assert os.path.isdir(ORIGINAL_CWD), "The original CWD is not a directory!"
    assert os.path.isdir(CWD), "The current working directory is not a directory?!!?!!one"

    return True


@check("Are we running in Python 3?", fixes=["Run the script with Python3"])
def is_python3():
    report_var("Version info", sys.version_info)
    report_var("Version", sys.version)
    report_var("API Version", sys.api_version)

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
        report_var("Kernel", out)
        answer = out.lower().startswith("linux")

        if answer:
            out = subprocess.check_output([UNAME, "-r"]).decode(CHARSET).strip()
            report_var("Kernel version", out)

        return answer

else:
    Log.error("Could not find uname")

OS_RELEASE = os.path.join(os.path.sep, "etc", "os-release")


@check("Do we have the OS release file on the system?", fixes=["Run Grapejuice on an LSB compatible distribution."])
def have_os_release():
    exists = os.path.exists(OS_RELEASE)
    if exists:
        with open(OS_RELEASE, "r") as fp:
            contents = fp.read()
            Log.info("OS Release contents:\n", contents)

            for line in contents.split("\n"):
                if not line:
                    continue

                s = line.split("=")
                k = s[0]
                v = "=".join(s[1:])

                report_var("OS_RELEASE_" + k, v)

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
                arch = match.group(1).strip()
                report_var("CPU Architecture", arch)
                return arch == "x86_64"

        return False

else:
    Log.info("lscpu could not be found, so we cannot check for the CPU architecture")


@check("Do we have a compiler?", fixes=[CommonFixes.follow_guide, "Install a compatible C compiler"])
def have_compiler():
    compilers = c_compilers()
    report_var("C Compilers", os.path.pathsep.join(compilers))
    return len(compilers) > 0


@check("Do we have pip or pip3?", fixes=[CommonFixes.follow_guide, "Install pip for Python 3"])
def have_pip():
    pip = which("pip")
    pip3 = which("pip3")

    report_var("pip", pip)
    report_var("pip3", pip3)

    return (pip or pip3) is not None


@check("Do we have pkg-config?", fixes=[CommonFixes.follow_guide, CommonFixes.c_tools])
def have_pkg_config():
    return report_var("PKG_CONFIG", which("pkg-config")) is not None


@check("Are the native libraries for cairo installed?",
       fixes=[CommonFixes.follow_guide, "Install the cairo development packages for your distribution"])
def have_cairo_natives():
    return report_var("PKG_CONFIG_CAIRO", pkg_config("cairo")) is not None


@check("Can we update the GTK icon cache?",
       fixes=[CommonFixes.follow_guide, "Install the GTK+ icon utilities for your distribution"])
def can_update_icon_cache():
    return report_var("GTK icon cache command", which("gtk-update-icon-cache")) is not None


@check("Can we update the desktop file database?",
       fixes=[CommonFixes.follow_guide, "Install the freedesktop database utilities for your distribution"])
def can_update_desktop_database():
    return report_var("Update desktop database command", which("update-desktop-database")) is not None


@check("Do we have XDG mime?", fixes=[CommonFixes.follow_guide, "Install the XDG utilities for your distribution"])
def have_xdg_mime():
    return report_var("XDG Mime command", which("xdg-mime")) is not None


@check("Do have have GObject?",
       fixes=[CommonFixes.follow_guide, "Install the GObject development packages for your distribution"])
def have_gobject():
    return report_var("PKG_CONFIG_GOBJECT", pkg_config("gobject-2.0")) is not None


@check("Do we have GObject introspection?",
       fixes=[CommonFixes.follow_guide, "Install the GObject introspection development packages for your distribution"])
def have_gobject_introspection():
    return report_var("PKG_CONFIG_GOBJECT_INTROSPECTION", pkg_config("gobject-introspection-1.0")) is not None


@check("Do we have git?", fixes=[CommonFixes.follow_guide, "Install git"])
def have_git():
    return report_var("git binary path", which("git")) is not None


@check("Do we have wine?", fixes=[CommonFixes.follow_guide, "Install Wine"])
def have_wine():
    return report_var("Wine binary path", which("wine")) is not None


@check("Do we have 64-bit wine?", fixes=[CommonFixes.follow_guide, CommonFixes.wine64])
def have_wine64():
    return report_var("Wine64 binary path", which("wine64")) is not None


@check("Log Wine version")
def print_wine_version():
    version = subprocess.check_output(["wine", "--version"]).decode(CHARSET).strip()
    report_var("WINE_VERSION", version)
    Log.info(version)

    return not not version


HOME = os.environ.get("HOME", None)


@check("Do we have the $HOME environment variable?")
def have_home_variable():
    return HOME is not None


if have_home_variable():
    GRAPEJUICE_WINEPREFIX = os.path.join(HOME, ".local", "share", "grapejuice", "wineprefix")


    @check("Do we have a wineprefix?")
    def have_wineprefix():
        return os.path.exists(GRAPEJUICE_WINEPREFIX)


    @check("Do we have a valid wineprefix?")
    def have_valid_wineprefix():
        if have_wineprefix():
            return os.path.isdir(GRAPEJUICE_WINEPREFIX)

        return False


    if have_wineprefix() and have_valid_wineprefix():
        class RegistryFile:
            _path: str
            _sections: Dict[str, Dict]
            _current_section: Dict[str, str] = None
            _section_header_ptn = re.compile(r"\[(.*)?].*")
            _key_ptn = re.compile(r"\"([\w\d]+)?\"\s*=\s*(.*)")

            def __init__(self, path: str):
                self._path = path
                self._sections = dict()

                if self.exists:
                    self._parse()

            @property
            def exists(self):
                return os.path.exists(self._path)

            @property
            def sections(self) -> List[str]:
                return list(self._sections.keys())

            def get_keys(self, section_key: str) -> Dict[str, str]:
                return self._sections[section_key]

            def _parse(self):
                with open(self._path, "rb") as fp:
                    content = fp.read()
                    text = content[2:].decode("iso8859-1").replace("\0", "")

                for line in text.split("\n"):
                    line = line.strip()

                    if not line:
                        continue

                    if line.startswith("Windows"):
                        continue

                    match = self._section_header_ptn.match(line)
                    if match:
                        self._current_section = self._sections.setdefault(match.group(1), {})
                        continue

                    match = self._key_ptn.match(line)
                    if match and (self._current_section is not None):
                        self._current_section[match.group(1).strip()] = match.group(2).strip()

            def __str__(self):
                return self._path


def run_wine_test_command(prefix: WinePrefix):
    out = prefix.run(["cmd", "/c", "echo Hello from Wine"])
    return prefix, out


@check("Can we make a valid 32-bit wineprefix?", fixes=[CommonFixes.wine32])
def can_make_valid_32_bit_prefix():
    prefix, out = run_wine_test_command(WinePrefix(arch="win32", destroy_prefix=True))
    Log.info(out)
    del prefix

    return True


@check("Can we make a valid 64-bit wineprefix?", fixes=[CommonFixes.wine64])
def can_make_valid_64_bit_prefix():
    prefix, out = run_wine_test_command(WinePrefix(arch="win64", destroy_prefix=True))
    Log.info(out)
    del prefix

    error_ptn = re.compile(r".*?:\s*WINEARCH set to win64 but .*?is a 32-bit installation.*")
    assert error_ptn, "Couldn't compile the pattern that checks for a 64-bit error"

    match = error_ptn.search(out)
    if match is None:
        return True

    return False


@check("Can we access the Grapejuice package?", fixes=[CommonFixes.follow_guide])
def have_grapejuice_package():
    try:
        from grapejuice import __version__
        Log.info("Grapejuice version:", __version__)

        return True

    except ImportError as e:
        Log.error(e)
        return False


HASTEBIN_DOCUMENTS = "https://hastebin.com/documents"
HASTEBIN_FILE = "https://hastebin.com/{file_id}"


def strict_yes_no(msg: str):
    querying = True
    result = False

    while querying:
        response = input(f"{msg} Type yes in capital letters if you do, if not type 'n' or 'no'.\n> ").strip()

        if response == "YES":
            querying = False
            result = True

        elif response.lower() == "n" or response.lower() == "no":
            querying = False
            result = False

        else:
            print("That is an invalid answer, please try again")
            print("")

    return result


def yes_no(msg: str):
    querying = True
    result = False

    def print_invalid():
        print("That is an invalid answer, please try again")
        print("")

    while querying:
        response = input(f"{msg} [y/n]\n> ").strip().lower()

        if response == "y" or response == "n":
            querying = False

            if response == "y":
                result = True

            elif response == "n":
                result = False

            else:
                print_invalid()

        else:
            print_invalid()

    return result


def display_file(path):
    cmds = ["less", "more", "cat"]

    if "EDITOR" in os.environ:
        cmds.insert(0, os.environ["EDITOR"])

    if "PAGER" in os.environ:
        cmds.insert(0, os.environ["PAGER"])

    for cmd in map(which, cmds):
        if cmd:
            subprocess.call([cmd, path])
            print("")
            return


def str_to_hastebin(s: str):
    req = urllib.request.Request(
        HASTEBIN_DOCUMENTS,
        method="POST",
        data=s.encode(CHARSET),
        headers={
            "User-Agent": f"Grapejuice Troubleshooter (CLI; Linux; {TROUBLESHOOTER_VERSION})",
            "Content-Type": "application/json",
            "DNT": 1,
            "Accept": "application/json, text/plain"
        }
    )

    response = urllib.request.urlopen(req)
    response_text: str = response.read().decode(CHARSET)
    response_object = json.loads(response_text)

    return HASTEBIN_FILE.format(file_id=response_object["key"])


def main():
    n_passed = sum(map(lambda f: f(), CHECKLIST))
    Log.info(f"{n_passed}/{len(CHECKLIST)} passed")

    TEXT_OUTPUT_BUFFER.seek(0)
    report = TEXT_OUTPUT_BUFFER.read()

    CSVReport.empty_row()
    CSVReport.empty_row()
    CSVReport.add_row("KEY", "VALUE", True, [])

    for k, v in VARS.items():
        CSVReport.add_row(k, v.replace(USERNAME, "[REDACTED]"), True, [])

    report_path = "/tmp/grapejuice-report.csv"

    report_fp = io.TextIOWrapper(io.BytesIO())

    print(CSVReport.to_string(), file=report_fp)
    print("", file=report_fp)
    print("""
##################
### LOG OUTPUT ###
##################
    """, file=report_fp)
    print(report, file=report_fp)

    report_fp.seek(0)
    with open(report_path, "w+") as fp:
        fp.write(report_fp.read())

    for pfx in USED_PREFIXES:
        if os.path.exists(pfx) and os.path.isdir(pfx):
            Log.info("Removing wineprefix", pfx)
            shutil.rmtree(pfx)

    if os.path.exists(CWD):
        Log.info("Removing", CWD)

        os.chdir(ORIGINAL_CWD)
        shutil.rmtree(CWD)

    for _ in range(30):
        print("")

    return_code = 0 if n_passed == len(CHECKLIST) else 1
    if return_code:
        print("Some checks did not pass, please review the report to see what's not working correctly")
        print("")

    else:
        print("All checks passed!")
        print("")

    print(f"Saved report to: {report_path}")
    print("If you intend on sharing the report, please make sure that it generated correctly.")
    print("")

    if yes_no("Do you want to review the report?"):
        display_file(report_path)

    if strict_yes_no("Do you want to upload your report to Hastebin, so you can share it with people that are helping "
                     "you troubleshoot?"):
        report_fp.seek(0)
        url = str_to_hastebin(report_fp.read())
        print("")
        print("Hastebin url for you to share: " + url)

    if return_code == 0:
        print("")
        print("Everything was A-OK, have a nice day!")

    sys.exit(return_code)


main()
