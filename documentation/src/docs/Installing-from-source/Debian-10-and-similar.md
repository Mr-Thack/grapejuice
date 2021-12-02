title: Install Grapejuice on Debian 10 and similar
---
## Preamble

❓ If you didn't click on the guide for Debian, but ended up on this page regardless, please do not panic! Debian is a
distribution that is the base for many other distributions in the Linux landscape. This guide is applicable to the
following distributions:

- Debian 10 (buster)
- Debian 11 (bullseye)
- Ubuntu 21.04 (Hirsute Hippo)
- Ubuntu 20.04 (Focal Fossa)
- Ubuntu 19.10 (Eoan Ermine)
- LMDE 4 (Debbie)
- Linux Mint 20 (Ulyana)
- Zorin OS 16

---

❗ This guide assumes that you've properly set up `sudo` on your Debian system and that dbus is properly configured. If
you are using a display manager like `lightdm` or are using a desktop environment provided by the distributor, dbus
should be in place properly.

Don't know what any of that means? If you've installed Ubuntu, Linux Mint, or selected a desktop environment in the
Debian installer, don't worry about this.

---

💻 All commands in this guide should be run in a terminal emulator using a regular user account that has access to `su`
or `sudo`. If you are running a fully fledged desktop environment, you can find a terminal emulator in your applications
menu.

## Installing Wine

It's recommended that you install a patched version of Wine. See [this guide](../Guides/Installing-Wine)
for why and how to get the patched version of Wine.

If you want to use vanilla Wine, use the [official WineHQ repositories](https://wiki.winehq.org/Download)
and install either `winehq-devel` or `winehq-staging`.

Note for users of distributions that are Ubuntu derivatives: You need to select an Ubuntu repository that aligns with
your specific derivative. The Ubuntu codename for your specific distribution can be found in the file `/etc/os-release`
as the value `UBUNTU_CODENAME`

## Synchronise the package repositories

We have to make sure that all repositories and locally installed packages are up to date. Run the following two commands
in a terminal:

```sh
sudo apt update
sudo apt upgrade -y
```

## Installing Grapejuice dependencies

Grapejuice requires a set of libraries to be installed and to be run. These dependencies can be installed by running the
following command:

```sh
sudo apt install -y git python3-pip python3-setuptools python3-wheel python3-dev pkg-config libcairo2-dev gtk-update-icon-cache desktop-file-utils xdg-utils libgirepository1.0-dev gir1.2-gtk-3.0 gnutls-bin:i386
```

## Install Grapejuice

First, you have to acquire a copy of the source code. This is easily done by cloning the git repository.

```sh
git clone https://gitlab.com/brinkervii/grapejuice.git /tmp/grapejuice
```

After the git clone command is finished, Grapejuice can be installed.

```sh
cd /tmp/grapejuice
python3 ./install.py
```
