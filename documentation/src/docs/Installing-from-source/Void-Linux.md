title: Install Grapejuice on Void Linux
---
## Installing Grapejuice dependencies

Grapejuice requires a set of libraries to be installed and to be run. These dependencies can be installed by running the
following command:

```sh
sudo xbps-install -S python3 python3-pip python3-wheel python3-setuptools python3-cairo python3-gobject cairo-devel desktop-file-utils xdg-user-dirs gtk-update-icon-cache shared-mime-info pkg-config gobject-introspection
```

## Installing Grapejuice

First, you have to aquire a copy of the source code. This is easily done by cloning the git repository.

```sh
git clone --depth=1 https://gitlab.com/brinkervii/grapejuice.git /tmp/grapejuice
```

After the git clone command is finished, Grapejuice can be installed.

```sh
cd /tmp/grapejuice
./install.py
```

## Installing Graphics dependencies

See [Graphics Drivers](https://docs.voidlinux.org/config/graphical-session/graphics-drivers/index.html)

## Installing Audio dependencies

```sh
sudo xbps-install -S libpulseaudio-32bit
```

## Installing a patched Wine build

It's recommended that you install a patched version of Wine. See [this guide](../Guides/Installing-Wine)
for more information.

Wine will also require dependencies to make Roblox function correctly.

```sh
sudo xbps-install -S freetype-32bit gnutls-32bit libgcc-32bit
```
