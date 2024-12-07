# SteamGifts Bot + Enhanced

Original version developed by [stilManiac](https://github.com/stilManiac) can be found [here](https://github.com/stilManiac/steamgifts-bot) - Thanks for the great work!

[![release](https://img.shields.io/github/v/release/ZoltePudeleczko/SteamGifts-Bot-Enhanced)](https://github.com/ZoltePudeleczko/SteamGifts-Bot-Enhanced/releases)
[![build-executables](https://github.com/ZoltePudeleczko/SteamGifts-Bot-Enhanced/actions/workflows/build-executables.yml/badge.svg?branch=master)](https://github.com/ZoltePudeleczko/SteamGifts-Bot-Enhanced/actions/workflows/build-executables.yml)

![SteamGifts Bot](assets/animation.gif)

## About

The bot specially designed for [SteamGifts.com](https://www.steamgifts.com/) giveaway platform. It automatically enters giveaways for you. Undetectable, does not overstrain SteamGifts API and can run 24/7.

### Features

- Automatically enters giveaways
- Configurable
  - wishlist
  - recommended
  - giveaways with a certain number of points
  - giveaways with a certain level
- Undetectable
- Multiplatform
  - macOS 13
  - Linux
  - Windows
- Sleeps to restock the points
- Can run 24/7

## How to run

1. Download the latest version from [`releases` (https://github.com/ZoltePudeleczko/SteamGifts-Bot-Enhanced/releases)](https://github.com/ZoltePudeleczko/SteamGifts-Bot-Enhanced/releases)
2. Sign in on [SteamGifts.com](https://www.steamgifts.com/)
3. Find `PHPSESSID` cookie in your browser
4. Start the bot and follow instructions

### Run from sources

Application requires Python 3.9

Checkout the repository and run the following commands:

```bash
pip install -r requirements.txt
python src/cli.py
```

## What's next?

Please leave your feedback and bugs in [`Issues`](https://github.com/ZoltePudeleczko/SteamGifts-Bot-Enhanced/issues) page.
