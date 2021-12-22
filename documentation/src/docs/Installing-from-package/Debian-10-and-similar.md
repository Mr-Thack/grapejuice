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

## Synchronise the package repositories

We have to make sure that all repositories and locally installed packages are up to date. Run the following two commands
in a terminal:

```sh
sudo apt update
sudo apt upgrade -y
```

## Installing required utilities

The `wget` and `gpg` utilities are required for the following steps. Run the following command in a terminal:

```sh
sudo apt install -y wget gpg
```

## Downloading Grapejuice's keyring

In order to ensure that the Grapejuice package hasn't been tampered with, you need Grapejuice's keyring.
To download the keyring, run the following commands in a terminal:

```sh
wget -O- https://gitlab.com/brinkervii/grapejuice/-/raw/master/ci_scripts/signing_keys/public_key.gpg | gpg --dearmor > /tmp/grapejuice-archive-keyring.gpg
sudo cp /tmp/grapejuice-archive-keyring.gpg /usr/share/keyrings/
rm /tmp/grapejuice-archive-keyring.gpg
```

## Adding the Grapejuice repository

The Grapejuice repository needs to be added to your system to get the Grapejuice package.
Run the following command in a terminal:

```sh
sudo tee /etc/apt/sources.list.d/grapejuice.list <<< 'deb [signed-by=/usr/share/keyrings/grapejuice-archive-keyring.gpg] https://brinkervii.gitlab.io/grapejuice/repositories/debian/ universal main' > /dev/null
```


## Installing Grapejuice

Since a new repository was added, you need to update package information on your system so apt can find Grapejuice.
Run the following commands in a terminal:

```sh
sudo apt update
sudo apt install -y grapejuice
```

## Installing a patched Wine build

It's recommended that you install a patched version of Wine. See [this guide](../Guides/Installing-Wine)
for more information.
