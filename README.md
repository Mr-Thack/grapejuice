# Grapejuice

⚠️ You need a Wine patch in order for the Roblox game client to function!

https://source.winehq.org/patches/data/207646

---

These days Roblox works quite well with Wine, though there are some minor issues running it. Grapejuice fills in the
gaps around these issues, so you can experience Roblox to its fullest on your favourite Linux distribution.

The primary gap-filler feature is the fact that Wine by default creates no protocol handlers, which is how Roblox
functions at its core. Without protocol handling, you won't be able to launch Roblox Studio and Experiences from
the website!

## Installing Grapejuice from source

Installing from source differs per distributions, please follow the appropriate installation guide for yours. All the
installation guides can be found in the [Grapejuice Wiki](https://gitlab.com/brinkervii/grapejuice/wikis/home)

## Note for upgrading from 1.x to 2.x

The builtin Grapejuice updater behaves a bit wonkily upgrading from 1.x to 2.x. Upgrading *does* work. However, the
upgrade button might not indicate such until you relaunch Grapejuice manually.

## Troubleshooting

Are you experiencing some trouble running Roblox Studio with Grapejuice? Please check out
the [Troubleshooting Guide](https://gitlab.com/brinkervii/grapejuice/wikis/Troubleshooting)

## Features

- Contain and automate a Wine prefix
- Expose utility functions
- Edit Roblox games from the website

## Roblox and Wine compatibility

What works:

- Roblox Studio
- Team Create
- Play Solo
- Test Server

What doesn't work:

- The Roblox game client
- Plugin gui's may cause seizures with some rendering methods. More about this issue is discussed in
  the [Troubleshooting Guide](https://gitlab.com/brinkervii/grapejuice/wikis/Troubleshooting)
