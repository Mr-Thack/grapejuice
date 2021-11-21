title: Documentation Home
---
## 👋 Welcome
Welcome to the Grapejuice wiki. This is the repository where all the documentation for the project is kept.

### ⚠ Important notices ⚠
- Make sure to install Wine!
- Grapejuice is a **management application**! Packages will in most cases not automatically install Wine for you, since package management in some distributions can be extremely odd and limit your choices in custom builds.
- You need to have Wine 6.11 or greater installed in order for Roblox Player to work!

Distributions mark a lot of Wine's dependencies as 'optional', in reality most of them aren't. If you're having issues with Roblox not functioning properly, make sure you have all the required 'optional' dependencies installed. Here's an (older but still relevant) blog post discussing the issue: https://www.gloriouseggroll.tv/how-to-get-out-of-wine-dependency-hell/

### 🐞 Known Issues
Roblox Player doesn't work perfectly yet. There are some bugs like the mouse getting stuck. Most known issues are documented on the 'Roblox on Linux' fandom page: https://roblox.fandom.com/wiki/Roblox_on_Linux

## 🚀 Installing Grapejuice

### 📦 Install using a package manager
Packages are available for some distributions. Just make sure to go through the [first time setup guide](https://gitlab.com/brinkervii/grapejuice/-/wikis/Guides/First-time-setup) after you have installed the package.

- Arch Linux: `grapejuice-git` (AUR). Preferably installed through an AUR helper: `yay -S grapejuice-git`, `paru -S grapejuice-git`, etc
- Manjaro Linux: `grapejuice-git`. Preferably installed through `pamac` or an AUR helper.
- [NixOS](https://github.com/NixOS/nixpkgs/pull/127397): `grapejuice`

### 📄 Install from source:
Do you want to install Grapejuice from source? Follow the installation guide that's appropriate for your distribution. Guides are currently written for the following distributions:

- Debian
    - [Debian 10 (buster)](Installing-from-source/Debian-10-and-similar)
    - [Debian 11 (bullseye)](Installing-from-source/Debian-10-and-similar)
- Ubuntu
    - [Ubuntu 21.04 (Hirsute Hippo)](Installing-from-source/Debian-10-and-similar)
    - [Ubuntu 20.04 (Focal Fossa)](Installing-from-source/Debian-10-and-similar)
    - [Ubuntu 19.10 (Eoan Ermine)](Installing-from-source/Debian-10-and-similar)
    - [Ubuntu 18.04 (Bionic Beaver)](Installing-from-source/Ubuntu-18.04-and-similar)
- Zorin OS
    - [Zorin OS 15.2](Installing-from-source/Ubuntu-18.04-and-similar)
    - [Zorin OS 16](Installing-from-source/Debian-10-and-similar)
- Linux Mint
     - [Linux Mint 20 "Ulyana"](Installing-from-source/Debian-10-and-similar)
     - [Linux Mint 19.3 "Tricia"](Installing-from-source/Ubuntu-18.04-and-similar)
     - [LMDE4 (Debbie)](Installing-from-source/Debian-10-and-similar)
- [Arch Linux](Installing-from-source/Arch-Linux-and-similar)
- [Manjaro Linux](Installing-from-source/Arch-Linux-and-similar)
- [Solus](Installing-from-source/Solus)
- [Fedora Workstation](Installing-from-source/Fedora-Workstation)
- [OpenSUSE](Installing-from-source/OpenSUSE)

**Please note that the following distributions are NOT supported:**

- Ubuntu 16.04 and older
- Linux Mint 18.x and older
- Kali Linux
- Parrot
- BlackArch
- Endless OS

## 💥 Troubleshooting
Are you having trouble running Grapejuice? Check out the [Troubleshooting page](Troubleshooting). It offers solutions to common problems with running Roblox Studio using Grapejuice.
