# Grapejuice

⚠️ You need at least Wine 6.11 for the Roblox game client to work!
Please grab an up to date copy from your repositories. If your repositories don't have Wine 6.11, have a look at
WineHQ's official repositories:
https://wiki.winehq.org/Download

---

These days Roblox works quite well with Wine, though there are some minor issues running it. Grapejuice fills in the
gaps around these issues, so you can experience Roblox to its fullest on your favourite Linux distribution.

The primary gap-filler feature is the fact that Wine by default creates no protocol handlers, which is how Roblox
functions at its core. Without protocol handling, you won't be able to launch Roblox Studio and Experiences from the
website!

## Installing Grapejuice from source

Installing from source differs per distributions, please follow the appropriate installation guide for yours. All the
installation guides can be found in the [Grapejuice Wiki](https://gitlab.com/brinkervii/grapejuice/wikis/home)

## Troubleshooting

Are you experiencing some trouble running Roblox Studio with Grapejuice? Please check out
the [Troubleshooting Guide](https://gitlab.com/brinkervii/grapejuice/wikis/Troubleshooting)

## Features

- Contain and automate a Wine prefix
- Edit Roblox experiences from the website
- Enjoy Roblox experiences by launching them from the website.
- Expose utility functions
- FFlag editor for tweaking Roblox' behaviour

## Roblox and Wine compatibility

What works:

- Roblox Studio
- Team Create
- Play Solo
- Test Server
- Roblox Player, granted you have an up to date version of Wine.

What doesn't work:

- Plugin gui's may cause seizures with some rendering methods. More about this issue is discussed in
  the [Troubleshooting Guide](https://gitlab.com/brinkervii/grapejuice/wikis/Troubleshooting)
