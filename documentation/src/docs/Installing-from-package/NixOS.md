title: Install Grapejuice on NixOS
---
## Installing Wine

It's recommended that you install a patched version of Wine. See [this guide](../Guides/Installing-Wine)
for why and how to get the patched version of Wine.

If you want to use vanilla Wine, run the following command:

```sh
nix-env -iA nixpkgs.wine
```

## Installing Grapejuice

In the terminal, run the following command:

```sh
nix-env -iA nixpkgs.grapejuice
```
