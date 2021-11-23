## Preamble
❓ If you didn't click on the guide for Ubuntu 18.04, but ended up on this page regardless, please do not panic! Ubuntu 18.04 is a distribution that is similar enough to other distributions in the Linux landscape. This guide is applicable to the following distributions:
- Ubuntu 18.04 (Bionic Beaver)
- Zorin OS 15.2 (Follow Ubuntu 18.04 instructions)
- Linux Mint 19.3 (Tricia, Follow Ubuntu 18.04 instructions)

---

💻 All commands in this guide should be run in a terminal emulator using a regular user account that has access to `su` or `sudo`. If you are running a fully fledged desktop environment, you can find a  terminal emulator in your applications menu.

---

⭐ Some commands do not produce any output. This usually means that the command ran successfully, so don't worry!

## Enabling 32-bit support
Even though Roblox Studio runs in 64-bit mode, 32-bit libraries are still required for some parts of the program. This is due to backwards compatibility in the Windows operating system. Run the following command in a terminal:
```sh
sudo dpkg --add-architecture i386
```

## Add the Wine HQ repository
Ubuntu 18.04 and similar distributions require additional repositories to run newer versions of Wine. This is a two-step process.

**01:** Add the WineHQ repository key
```
wget -nc https://dl.winehq.org/wine-builds/winehq.key -O /tmp/winehq.key
sudo apt-key add /tmp/winehq.key
```

**02:** Install the WineHQ repository. The command differs slighly per distribution variant, so please pick the correct one for you distribution.

| Distribution                 | Command                                                                             |
|------------------------------|-------------------------------------------------------------------------------------|
| Ubuntu 18.04                 | sudo apt-add-repository 'deb https://dl.winehq.org/wine-builds/ubuntu/ bionic main' |
| Linux Mint 19.x              | sudo apt-add-repository 'deb https://dl.winehq.org/wine-builds/ubuntu/ bionic main' |

---

❓ Are you not sure which distribution you are on? Run the following command to see the details about your specific distribution:
```sh
cat /etc/os-release
```


## Install FAudio
Wine 5.0 and newer require the FAudio audio libraries. However, these are not supplied by the Ubuntu repositories, so we will have to install these manually.

**01:** Download the FAudio packages to a temporary location
```sh
wget https://download.opensuse.org/repositories/Emulators:/Wine:/Debian/xUbuntu_18.04/i386/libfaudio0_19.07-0~bionic_i386.deb -O /tmp/faudio_i386.deb
wget https://download.opensuse.org/repositories/Emulators:/Wine:/Debian/xUbuntu_18.04/amd64/libfaudio0_19.07-0~bionic_amd64.deb -O /tmp/faudio_amd64.deb
```

**02:** Install the FAudio packages that you just downloaded
```sh
sudo apt install -y /tmp/faudio_i386.deb
sudo apt install -y /tmp/faudio_amd64.deb
```

## Add the 'deadsnakes' repository
Grapejuice requires at least Python3.7. During the dependency installation we are going to do this. However, we need a repository that provides Python3.7 since Ubuntu 18.04 and similar distributions only provide up to Python3.6. Run the following commands and press the enter key when prompted.
```sh
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
```


## Synchronizing the package repositories
We have to make sure that all repositories and locally installed packages are up to date. Run the following two commands in a terminal:
```sh
sudo apt update
sudo apt upgrade -y
```

## Installing Grapejuice dependencies
Grapejuice requires a set of libraries to be installed and to be run. These dependencies can be installed by running the following command:
```sh
sudo apt install -y wine-stable git pkg-config python3.7 python3.7-dev python3-pip libcairo2-dev libgirepository1.0-dev libgtk-3-0 libgtk-3-bin gir1.2-gtk-3.0
```

## Installing Grapejuice
First, you have to aquire a copy of the source code. This is easily done by cloning the git repository.
```sh
git clone https://gitlab.com/brinkervii/grapejuice.git
```

After the git clone command is finished, Grapejuice can be installed.
```sh
cd grapejuice
python3.7 ./install.py
```

## 🚀 Running Grapejuice for the first time
Running Grapejuice for the first time requires some additional steps. Please follow the [guide on running Grapejuice for the first time](../Guides/First-time-setup)
