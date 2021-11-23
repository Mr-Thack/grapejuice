## Preamble

:question: If you didn't click on the guide for Arch Linux, but ended up on this page regardless, please do not panic! Arch Linux is a distribution that is the base for other distributions in the Linux landscape. This guide is applicable to the following distributions:

- Arch Linux
- Manjaro Linux

---

:computer: Grapejuice assumes your desktop is configured properly. Even though Arch Linux to some, is all about minimalism, it is recommended that you run your desktop session using a display manager.

---

:package: This setup guide assumes you have AUR support enabled on your system, which implies that the `base-devel` package is installed and that your account can use the `sudo` command.

## Enabling 32-bit support

Even though Roblox Studio runs in 64-bit mode, 32-bit libraries are still required for some parts of the program. This is due to backwards compatibility in the Windows operating system.

You enable 32-bit support by editing `/etc/pacman.conf` with your favourite editor, where you uncomment the multilib repository. Note that you have to be root in order to edit the file. The resulting file should contain the following:

```ini
[multilib]
Include = /etc/pacman.d/mirrorlist
```

## Synchronize the package database

Before installing anything, you should always synchronize the package database in order to prevent strange package-not-found errors.

```shell
sudo pacman -Syu
```

## Installing Wine

Installing Wine on Arch Linux is fairly straight forward once the `multilib` repository is enabled:

```shell
sudo pacman -S wine
```

## Install additional wine dependencies

Some additional Wine dependencies are required for Roblox to work properly. These have to be installed explicitly because the Arch package marks these dependencies as optional. You can install them using the following command:

```shell
sudo pacman -S --asdep lib32-gnutls lib32-openssl lib32-pipewire lib32-libpulse lib32-alsa-lib lib32-alsa-plugins
```

## Installing Grapejuice dependencies

Grapejuice requires a set of libraries to be installed and to be run. These dependencies can be installed by running the following command:

```shell
sudo pacman -S git python-pip cairo gtk3 gobject-introspection desktop-file-utils xdg-utils xdg-user-dirs gtk-update-icon-cache shared-mime-info gobject-introspection
```

## Installing Grapejuice

First, you have to acquire a copy of the source code. This is easily done by cloning the git repository.

```shell
git clone https://gitlab.com/brinkervii/grapejuice.git /tmp/grapejuice
```

After the git clone command is finished, Grapejuice can be installed.

```shell
cd /tmp/grapejuice
./install.py
```

## :rocket: Running Grapejuice for the first time

Running Grapejuice for the first time requires some additional steps. Please follow the [guide on running Grapejuice for the first time](../Guides/First-time-setup)

## :star: Bonus Wine Tip :star:

The default installation of Wine on Arch Linux is quite minimal. This might sometimes lead to Wine applications not working due to missing libraries. The killer (but kind of bloated) solution to this is to just install all optional dependencies of Wine. It is everything but pretty, but hey, it works.

```shell
sudo pacman -S expac
sudo pacman -S $(expac '%n %o' | grep ^wine)
```
