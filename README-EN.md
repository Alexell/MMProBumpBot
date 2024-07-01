# Bot for [MMPro Bump](https://alexell.ru/cc/mmpro)

![img1](.github/images/demo.png)

> 🇷🇺 README на русском доступен [здесь](README.md)

## Functionality
| Feature                                                        | Supported  |
|----------------------------------------------------------------|:----------:|
| Multithreading                                                 |     ✅     |
| Binding a proxy to a session                                   |     ✅     |
| Auto-claim daily grant                                         |     ✅     |
| Automatic farming                                              |     ✅     |
| Automatic taps that account for enabled boosts                 |     ✅     |
| Support tdata and pyrogram .session                            |     ✅     |

## [Options](https://github.com/Alexell/MMProBumpBot/blob/main/.env-example)
| Option                  | Description                                                                   |
|-------------------------|----------------------------------------------------------------------------|
| **API_ID / API_HASH**   | Platform data from which to launch a Telegram session (stock - Android)    |
| **USE_PROXY_FROM_FILE** | Whether to use proxy from the `bot/config/proxies.txt` file (True / False) |

## Installation
**Use Python 3.10!**

You can download [**Repository**](https://github.com/Alexell/MMProBumpBot) by cloning it to your system and installing the necessary dependencies:
```shell
~ >>> git clone https://github.com/Alexell/MMProBumpBot.git
~ >>> cd MMProBumpBot

# Linux
~/MMProBumpBot >>> python3 -m venv venv
~/MMProBumpBot >>> source venv/bin/activate
~/MMProBumpBot >>> pip3 install -r requirements.txt
~/MMProBumpBot >>> cp .env-example .env
~/MMProBumpBot >>> nano .env # specify your API_ID and API_HASH, the rest is taken by default
~/MMProBumpBot >>> python3 main.py

# Windows
~/MMProBumpBot >>> python -m venv venv
~/MMProBumpBot >>> venv\Scripts\activate
~/MMProBumpBot >>> pip install -r requirements.txt
~/MMProBumpBot >>> copy .env-example .env
~/MMProBumpBot >>> # specify your API_ID and API_HASH, the rest is taken by default
~/MMProBumpBot >>> python main.py
```

Also for quick launch you can use arguments, for example:
```shell
~/MMProBumpBot >>> python3 main.py --action (1/2)
# Or
~/MMProBumpBot >>> python3 main.py -a (1/2)

# 1 - Create session
# 2 - Run bot
```