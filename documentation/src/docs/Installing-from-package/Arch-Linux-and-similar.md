title: Install Grapejuice on Arch Linux and similar distributions
---
## Preamble

:question: If you didn't click on the guide for Arch Linux, but ended up on this page regardless, please do not panic!
Arch Linux is a distribution that is the base for other distributions in the Linux landscape. This guide is applicable
to the following distributions:

- Arch Linux
- Manjaro Linux

---

:computer: Grapejuice assumes your desktop is configured properly. Even though Arch Linux to some, is all about
minimalism, it is recommended that you run your desktop session using a display manager.

---

## Installing Grapejuice

1. Enable the [multilib repository](https://wiki.archlinux.org/title/Official_repositories#multilib).
2. Get an [AUR helper](https://wiki.archlinux.org/title/AUR_helpers) or
[learn how to install packages from the AUR manually](https://wiki.archlinux.org/title/Arch_User_Repository).
3. Install the `base-devel` package group with `sudo pacman -S base-devel`.
4. Install [grapejuice-git](https://aur.archlinux.org/packages/grapejuice-git/) through an AUR helper or manually.

## Installing dependencies for audio

Install `lib32-libpulse` with `sudo pacman -S lib32-libpulse`.

In addition, if you're using Pipewire (check if the `pipewire` process is running), you need to install
`pipewire-pulse` with `sudo pacman -S pipewire-pulse`.

## Installing a patched Wine build

It's recommended that you install a patched version of Wine. See [this guide](../Guides/Installing-Wine)
for more information.
