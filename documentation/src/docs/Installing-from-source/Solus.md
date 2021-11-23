## Preamble

⚠ These instructions have only been tested on Solus 4.1 Budgie!

## Installing Grapejuice dependencies

Grapejuice requires a set of libraries to be installed and to be run. These dependencies can be installed by running the
following command:

```sh
sudo eopkg it -c system.devel
sudo eopkg install wine wine-32bit git python3-devel libcairo-devel
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

Running Grapejuice for the first time requires some additional steps. Please follow
the [guide on running Grapejuice for the first time](../Guides/First-time-setup)
