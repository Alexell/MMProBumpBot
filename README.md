# Бот для [MMPro Bump](https://alexell.ru/cc/mmpro)

![img1](.github/images/demo.png)

> 🇺🇸 README in english available [here](README-EN.md)

## Функционал
| Функция                                                        | Поддерживается  |
|----------------------------------------------------------------|:---------------:|
| Многопоточность                                                |        ✅       |
| Привязка прокси к сессии                                       |        ✅       |
| Получение ежедневной награды                                   |        ✅       |
| Автоматический фарминг                                         |        ✅       |
| Автоматические тапы с учетом бустов                            |        ✅       |
| Поддержка tdata и pyrogram .session                            |        ✅       |

## [Настройки](https://github.com/Alexell/MMProBumpBot/blob/main/.env-example)
| Опция                   | Описание                                                                   |
|-------------------------|----------------------------------------------------------------------------|
| **API_ID / API_HASH**   | Данные платформы, с которой запускать сессию Telegram (сток - Android)     |
| **USE_PROXY_FROM_FILE** | Использовать-ли прокси из файла `bot/config/proxies.txt` (True / False)    |

## Установка
**Используйте Python 3.10!**

Вы можете скачать [**Репозиторий**](https://github.com/Alexell/MMProBumpBot) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
~ >>> git clone https://github.com/Alexell/MMProBumpBot.git
~ >>> cd MMProBumpBot

# Linux
~/MMProBumpBot >>> python3 -m venv venv
~/MMProBumpBot >>> source venv/bin/activate
~/MMProBumpBot >>> pip3 install -r requirements.txt
~/MMProBumpBot >>> cp .env-example .env
~/MMProBumpBot >>> nano .env # указываете ваши API_ID и API_HASH, остальное берется по умолчанию
~/MMProBumpBot >>> python3 main.py

# Windows
~/MMProBumpBot >>> python -m venv venv
~/MMProBumpBot >>> venv\Scripts\activate
~/MMProBumpBot >>> pip install -r requirements.txt
~/MMProBumpBot >>> copy .env-example .env
~/MMProBumpBot >>> # указываете ваши API_ID и API_HASH, остальное берется по умолчанию
~/MMProBumpBot >>> python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/MMProBumpBot >>> python3 main.py --action (1/2)
# Or
~/MMProBumpBot >>> python3 main.py -a (1/2)

# 1 - создать сессию
# 2 - запустить бот
```