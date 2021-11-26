title: Troubleshooting
---
This page describes some of the most common issues with Grapejuice and how to solve them. **Make sure you're using the
latest version of Grapejuice and Wine 6.11 or above, or Wine Staging 6.16 or above!** Do you have an issue that is not
described here? Please let us know!

**Table of Contents**

[TOC]

---

## An error occurred trying to launch the experience. Please try again later.

If you're using Firefox, go to about:config and set `network.http.referer.XOriginPolicy`
and `network.http.sendRefererHeader` to `1`.

## The server name or address could not be resolved

Start the `nscd` service from `glibc`.

## Grapejuice does not launch

This is a problem that can have many causes. The first step to fixing an issue that presents itself this way is by
running Grapejuice in a terminal session.

If you've installed Grapejuice from the source repository using the `install.py` script. You can run Grapejuice by
executing

```
~/.local/bin/grapejuice gui
```

## Missing shared object libffi.so.[number]

Your system's `libffi` package may have upgraded, and the version of the .so file has increased. Just reinstalling
Grapejuice to fix the issue will not work in this case. Pip caches packages locally so they don't have to be
re-downloaded/rebuilt with new installations of a package, but this causes invalid links to shared objects to be cached
as well.

### Solution

**1.** Remove the pip package cache

```
rm -r ~/.cache/pip
```

**2.** Reinstall Grapejuice

```
cd $GRAPEJUICE_SOURCES_ROOT
./install.py
```

## Black box follows the cursor in Studio

This is caused by [a regression in Wine](https://source.winehq.org/git/wine.git/commit/db2b266). The only known
workaround is to revert this commit and compile Wine yourself.

## Built-in screen recorder doesn't work

You should consider using another screen recorder.

If you need to use the built-in screen recorder, follow the below steps:

1. Open Grapejuice and open Winetricks
2. Select the default wineprefix
3. Click "Install a Windows DLL or component"
4. Install `qasf` and `wmp11`.

## Cursor is not unlocked after locking the cursor

You need a patched version of Wine to solve this. See [this guide](Guides/Installing-Wine).

## Player freezes when visiting an experience

This is caused by [a regression in Wine](https://source.winehq.org/git/wine.git/commit/7ef35b3).

To work around this, open Grapejuice's FFlag editor and disable the FFlag `DFFlagClientVisualEffectRemote`.

## Failed to deploy

This error occurs when launching Studio from the website before Studio is installed.

To get around this, open Studio through Grapejuice and **do not** log in if Grapejuice asks you to.

After Studio is installed, you should be able to launch Studio from the website.

## Grapejuice's FFlag editor doesn't open

This is because Grapejuice attempts to launch `RobloxStudioBeta.exe` rather than `RobloxStudioLauncherBeta.exe` to get
the default FFlags. However, `RobloxStudioBeta.exe` doesn't exist if Studio is not installed.

As a workaround, open Studio first to install it. After Studio is installed, you should be able to use the FFlag editor
normally.

## Bad performance/input lag

### Choosing the renderer

Check if your GPU supports Vulkan. [This unofficial website](https://vulkan.gpuinfo.org/listdevices.php) can help you
check for Vulkan support on your GPU. If Vulkan is supported, using Vulkan is recommended, and you should ensure
appropriate Vulkan 64-bit and 32-bit drivers are installed.

Are you using Arch Linux? Please refer to the instructions on the Arch
Wiki: [https://wiki.archlinux.org/title/Vulkan#Installation](https://wiki.archlinux.org/title/Vulkan#Installation)

If you want to enable Vulkan support on Debian based distributions you need one or more of the packages listed in the
table below. Depending on which GPU you have. Keep in mind though, that the base vulkan packages are always required! To
install the drivers for you GPU, just copy the terminal command from the table and paste it into your terminal.

| Package Type                    | Terminal Command                                                |
|---------------------------------|-----------------------------------------------------------------|
| Base vulkan packages (required) | `sudo apt install libvulkan1 libvulkan1:i386`                   |
| MESA (amdgpu/intel)             | `sudo apt install mesa-vulkan-drivers mesa-vulkan-drivers:i386` |
| NVidia                          | `sudo apt install nvidia-driver nvidia-driver:i386`             |

If Vulkan is not supported, OpenGL is recommended.

### Changing the renderer

Keep in mind that the speed of each renderer varies by hardware.

:warning: Make sure only one renderer is enabled.

1. Open the Grapejuice FFlag editor through the Grapejuice UI.
2. The FFlag to change to use each graphics API is listed below.
3. Save the FFlags.

| Graphics API | FFlag                            |
|--------------|----------------------------------|
| Vulkan       | `FFlagDebugGraphicsPreferVulkan` |
| Direct3D     | `FFlagDebugGraphicsPreferD3D11`  |
| OpenGL       | `FFlagDebugGraphicsPreferOpenGL` |

## Known issues with no known workarounds

- Window decorations (bar on the top of windows) can disappear after entering and exiting fullscreen.
- Screenshot key in the player doesn't work, but the screenshot button does.
- Player process occasionally stays after closing the window.
- Non-QWERTY keyboard layouts can cause problems with controls.
- Voice chat doesn't work.
- The warning "Unable to read VR Path Registry" usually appears. However, this doesn't seem to affect anything.

## Automated Troubleshooter

Grapejuice has a distribution
independent [troubleshooter](https://gitlab.com/brinkervii/grapejuice/-/raw/master/troubleshooter.py) that can detect
some issues with your system. You can run it with:

```
python3 <(curl -L https://gitlab.com/brinkervii/grapejuice/-/raw/master/troubleshooter.py)
```
