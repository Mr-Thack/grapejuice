## Preamble

⚠ These instructions have only been tested on Fedora Workstation 32!

---

🖥 If you are using the Wayland display server, you might not get any graphical output from Roblox. In that case you should try running Roblox Studio using an Xorg session.

## Installing Grapejuice dependencies
Grapejuice requires a set of libraries to be installed and to be run. These dependencies can be installed by running the following command:
```shell
sudo dnf install git python3-devel python3-pip cairo-devel gobject-introspection-devel cairo-gobject-devel dbus-glib-devel make wine xdg-utils

```

## Installing Grapejuice
First, you have to aquire a copy of the source code. This is easily done by cloning the git repository.
```sh
git clone https://gitlab.com/brinkervii/grapejuice.git
```

After the git clone command is finished, Grapejuice can be installed.
```sh
cd grapejuice
./install.py
```

## 🚀 Running Grapejuice for the first time
Running Grapejuice for the first time requires some additional steps. Please follow the [guide on running Grapejuice for the first time](../Guides/First-time-setup)
