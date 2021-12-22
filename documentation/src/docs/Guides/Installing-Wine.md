title: Install Wine
---
## About the mouse bug

When locking the cursor (not allowing the cursor to move) like by adjusting the camera with right click,
the cursor does not get unlocked.

To fix this, a patched version of Wine is required.

## Installing a patched version of Wine

**Warning:** You should decide if you trust the authors of the below resources before using them.

There are two different options: installing Wine with patches compiled for you or compiling Wine yourself.

### Installing a prebuilt patched Wine build

Run [this Python script](https://pastebin.com/raw/5SeVb005) which requires Python 3.8 or above.

To run it, run the following:

```sh
cd /tmp
wget https://pastebin.com/raw/5SeVb005 -O install.py
python3 install.py
```

### Compiling Wine TKG

Use [this guide](Compiling-Wine-TKG).

## Installing vanilla Wine

Vanilla Wine does not currently have the mouse patch, meaning the mouse bug will occur when using vanilla Wine.

You need to install Wine 6.11 or above, or Wine Staging 6.16 or above.

If your distribution provides the `wine` package, install that from your package manager.

Otherwise, use the [download page for Wine](https://wiki.winehq.org/Download).
