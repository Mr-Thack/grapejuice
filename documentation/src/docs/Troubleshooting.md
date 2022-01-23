title: Troubleshooting
---
This page describes some of the most common issues with Grapejuice and how to solve them. **Make sure you're using the
latest version of Grapejuice!** Do you have an issue that is not described here? Please let us know!

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

```sh
~/.local/bin/grapejuice gui
```

## Missing shared object libffi.so.[number]

Your system's `libffi` package may have upgraded, and the version of the .so file has increased. Just reinstalling
Grapejuice to fix the issue will not work in this case. Pip caches packages locally so they don't have to be
re-downloaded/rebuilt with new installations of a package, but this causes invalid links to shared objects to be cached
as well.

### Solution

**1.** Remove the pip package cache

```sh
rm -r ~/.cache/pip
```

**2.** Reinstall Grapejuice

```sh
cd $GRAPEJUICE_SOURCES_ROOT
./install.py
```

## Built-in screen recorder doesn't work

You should consider using another screen recorder.

If you need to use the built-in screen recorder, follow the below steps:

1. Open Grapejuice.
2. Select the player's wineprefix.
3. Select "Wine Apps" and open Winetricks.
4. Select the default wineprefix.
5. Click "Install a Windows DLL or component".
6. Install `qasf` and `wmp11`.

## Cursor is not unlocked after locking the cursor

You need a patched version of Wine to solve this. See [this guide](Guides/Installing-Wine).

## Desktop application is being used

This is part of the [app beta](https://devforum.roblox.com/t/925069). If you'd like to opt-out, go to the
Grapejuice UI, go to the player wineprefix, and disable "Desktop App".

## Known issues with no known workarounds

- Window decorations (bar on the top of windows) can disappear after entering and exiting fullscreen.
- Screenshot key in the player doesn't work, but the screenshot button does.
- Non-QWERTY keyboard layouts can cause problems with controls.
- Voice chat doesn't work.
- The warning "Unable to read VR Path Registry" usually appears. However, this doesn't seem to affect anything.

## Automated Troubleshooter

Grapejuice has a distribution
independent [troubleshooter](https://gitlab.com/brinkervii/grapejuice/-/raw/master/troubleshooter.py) that can detect
some issues with your system. You can run it with:

```sh
python3 <(curl -L https://gitlab.com/brinkervii/grapejuice/-/raw/master/troubleshooter.py)
```
