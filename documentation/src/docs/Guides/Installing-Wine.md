title: Install Wine
---
## About Wine issues

Using a version of Wine that has not been patched may lead to issues like the in-game cursor getting stuck, the game crashing, or being kicked automatically with an error code.

To fix this, a patched version of Wine is required.

## Installing a patched version of Wine

**Warning:** You should decide if you trust the authors of the below resources before using them.

There are two different options: Installing a prebuilt patched Wine build, or compiling it yourself. **Generally, it is easier to install the prebuilt version.**

### Installing a prebuilt patched Wine build

Run the commands below to automatically download a pre-compiled patched Wine:

```sh
cd /tmp
wget https://pastebin.com/raw/5SeVb005 -O install.py
python3 install.py
```

### Compiling Wine TKG

If you'd like to instead compile Wine, you can use [this guide](Compiling-Wine-TKG).

## Installing vanilla Wine

Vanilla Wine does not currently have the mouse patch, meaning the mouse bug will occur when using vanilla Wine.

If your distribution provides a package for Wine, usually named `wine`, which provides Wine 7.0 or above,
install that from your package manager.

Otherwise, use the [download page for Wine](https://wiki.winehq.org/Download).
