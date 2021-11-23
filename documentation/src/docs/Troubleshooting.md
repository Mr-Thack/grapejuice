This page describes some of the most common issues with Grapejuice and how to solve them. Do you have an issue that is
not described here? Please let us know!

[TOC]

## Nothing is rendering in DirectX 11 mode!

Due to a regression in Wine 6.1, shaders in the DirectX 11 graphics mode do not compile correctly. The end result of
this is that nothing will be rendered in the 3D viewport, and may cause some graphical artifacting to appear.

### Solution

Downgrade Wine to version 6.0 until the issue has been resolved by the Wine development team. You should refer to the
documentation of your Linux distribution to see how you should do this.

## Roblox Studio crashes when attempting to log in / error displaying captcha

This is an issue with Roblox Studio that cropped up late August of 2018. Roblox added a funcaptcha feature to the login
screen. This however, uses the Wine web browser, which is one of the most unstable components of Wine. So whenever you
attempt to log in through studio now, it crashes

### Solution

You can authenticate Roblox Studio by editing any game on the Roblox website whilst being logged in. After this has been
done, Studio will be authenticated and ready for use. Don't know which game to edit or you don't have any games on
Roblox? Try editing the Roblox crossroads game, click the three dots in the top right of the page and select edit.

Link to
crossroads: [https://www.roblox.com/games/1818/Classic-Crossroads](https://www.roblox.com/games/1818/Classic-Crossroads)

## Roblox Studio could not authenticate user

When attempting to log in, Roblox Studio may report the error  "Could not authenticate user. Request timed out".

### Solution

This is due to a [regression in Wine 5.0-rc2](https://bugs.winehq.org/show_bug.cgi?id=48357). If you have a version of
wine that is in the range of `wine-5.0-rc2` through `wine-5.0-rc4`, you should downgrade your Wine installation
to `wine-5.0-rc1` or lower.

## Lighting has strange shadows

Roblox Studio prefers to use DirectX rendering methods to render to the screen in its default configuration. Certain
combinations of DirectX versions and graphics cards may produce artefacts.

### Solution

Click the GraphicsMode OpenGL button in Grapejuice, it is listed under the Maintenance tab.

**Warning**: Using the OpenGL graphics mode makes every plugin gui in studio flicker, rendering them unusable. This
includes some of the newer settings dialogs.

## Grapejuice does not launch

This is a problem that can have many causes. The first step to fixing an issue that presents itself this way is by
running Grapejuice in a terminal session.

If you've installed Grapejuice from the source repository using the `install.py` script. You can run Grapejuice by
executing

```sh
~/.local/bin/grapejuice gui
```

## Missing shared object libffi.so.6

Your system's `libffi` package may have upgraded, and the version of the .so file has increased. Just reinstalling
Grapejuice to fix the issue will not work in this case. Pip caches packages locally so they don't have to be
re-downloaded/rebuilt with new installations of a package, but this causes invalid links to shared objects to be cached
as well

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

## Automated Troubleshooter

Grapejuice has a distribution independent troubleshooter that can detect some issues with your system. You can run it
through various means:

**1.** Run it directly using curl

```sh
python3 <(curl -L https://gitlab.com/brinkervii/grapejuice/-/raw/master/troubleshooter.py)
```

**2.** Run it directly using wget

```sh
pushd /tmp; python3 <(wget https://gitlab.com/brinkervii/grapejuice/-/raw/master/troubleshooter.py -O-); popd
```

**3.** Clone the repository and run it

```sh
GRAPEJUICE=$HOME/Downloads/grapejuice
git clone https://gitlab.com/brinkervii/grapejuice "$GRAPEJUICE"
python3 "$GRAPEJUICE/troubleshooter.py"
```
