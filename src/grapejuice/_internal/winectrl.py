import os
import shutil
import time

import grape_common.variables as variables


def prepare():
    prefix_dir = variables.wineprefix_dir()
    os.environ["WINEPREFIX"] = prefix_dir
    os.environ["WINEARCH"] = "win64"

    if not os.path.exists(prefix_dir):
        os.makedirs(prefix_dir)


def winecfg():
    prepare()
    os.spawnlp(os.P_NOWAIT, variables.wine_binary(), variables.wine_binary(), "winecfg")


def regedit():
    prepare()
    os.spawnlp(os.P_NOWAIT, variables.wine_binary(), variables.wine_binary(), "regedit")


def explorer():
    prepare()
    os.spawnlp(os.P_NOWAIT, variables.wine_binary(), variables.wine_binary(), "explorer")


def load_reg(srcfile):
    prepare()
    target_filename = str(int(time.time())) + ".reg"
    target_path = os.path.join(variables.wine_temp(), target_filename)
    shutil.copyfile(srcfile, target_path)

    winreg = "C:\\windows\\temp\\{}".format(target_filename)
    os.spawnlp(os.P_WAIT, variables.wine_binary(), variables.wine_binary(), "regedit", "/S", winreg)
    os.spawnlp(os.P_WAIT, variables.wine_binary_64(), variables.wine_binary_64(), "regedit", "/S", winreg)

    os.remove(target_path)


def load_regs(s: [str], patches: dict = None):
    prepare()
    target_filename = str(int(time.time())) + ".reg"
    target_path = os.path.join(variables.wine_temp(), target_filename)

    with open(target_path, "w+") as fp:
        if patches is None:
            fp.write("\r\n".join(s))
        else:
            out_lines = []
            for line in s:
                for k, v in patches.items():
                    varkey = "$" + k
                    if varkey in line:
                        line = line.replace(varkey, v)

                out_lines.append(line)

            fp.writelines(out_lines)

    winreg = "C:\\windows\\temp\\{}".format(target_filename)
    os.spawnlp(os.P_WAIT, variables.wine_binary(), variables.wine_binary(), "regedit", "/S", winreg)
    os.spawnlp(os.P_WAIT, variables.wine_binary_64(), variables.wine_binary_64(), "regedit", "/S", winreg)

    os.remove(target_path)


def wine_tricks():
    prepare()
    os.spawnlp(os.P_NOWAIT, "winetricks", "winetricks")


def disable_mime_assoc():
    load_reg(os.path.join(variables.assets_dir(), "disable_mime_assoc.reg"))


def set_roblox_document_path():
    src_path = os.path.join(variables.assets_dir(), "roblox_documents_folder.reg")
    patches = dict()
    patches["DOCUMENTS_DIR"] = "Z:" + variables.xdg_documents().replace("/", "\\\\")

    with open(src_path, "r") as fp:
        load_regs(fp.readlines(), patches)


def load_dll_overrides():
    load_reg(os.path.join(variables.assets_dir(), "dll_overrides.reg"))


def sandbox():
    user_dir = variables.wine_user()
    if os.path.exists(user_dir) and os.path.isdir(user_dir):
        for dir in os.listdir(user_dir):
            p = os.path.join(user_dir, dir)
            if os.path.islink(p):
                os.remove(p)


def configure_prefix():
    disable_mime_assoc()
    sandbox()
    load_dll_overrides()
    set_roblox_document_path()


def create_prefix():
    configure_prefix()


def prefix_exists():
    return os.path.exists(variables.wineprefix_dir())


def run_exe(exe_path, *args):
    prepare()
    if len(args) > 0:
        os.spawnlp(os.P_NOWAIT, variables.wine_binary(), variables.wine_binary(), exe_path, *args)
    else:
        os.spawnlp(os.P_NOWAIT, variables.wine_binary(), variables.wine_binary(), exe_path)
