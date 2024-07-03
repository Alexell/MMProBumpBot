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

**API_ID** и **API_HASH** вы можете получить после создания приложения на [my.telegram.org/apps](https://my.telegram.org/apps)

## Быстрый старт
### Windows
1. Убедитесь, что у вас установлен **Python 3.10** или более новая версия.
2. Используйте `INSTALL.bat` для установки, затем укажите ваши API_ID и API_HASH в .env
3. Используйте `START.bat` для запуска бота (или в консоли: `python main.py`)

### Linux
1. Клонируйте репозиторий: `git clone https://github.com/Alexell/MMProBumpBot.git && cd MMProBumpBot`
2. Выполните установку: `chmod +x INSTALL.sh START.sh && ./INSTALL.sh`, затем укажите ваши API_ID и API_HASH в .env
3. Используйте `./START.sh` для запуска бота (или в консоли: `python3 main.py`)

## Ручная установка
Вы можете скачать [**Репозиторий**](https://github.com/Alexell/MMProBumpBot) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
~ >>> git clone https://github.com/Alexell/MMProBumpBot.git
~ >>> cd MMProBumpBot

# Linux
~/MMProBumpBot >>> python3 -m venv venv
~/MMProBumpBot >>> source venv/bin/activate
~/MMProBumpBot >>> pip3 install -r requirements.txt
~/MMProBumpBot >>> cp .env-example .env
~/MMProBumpBot >>> nano .env # укажите ваши API_ID и API_HASH, остальное можно оставить по умолчанию
~/MMProBumpBot >>> python3 main.py

# Windows (сначала установите Python 3.10 или более новую версию)
~/MMProBumpBot >>> python -m venv venv
~/MMProBumpBot >>> venv\Scripts\activate
~/MMProBumpBot >>> pip install -r requirements.txt
~/MMProBumpBot >>> copy .env-example .env
~/MMProBumpBot >>> # укажите ваши API_ID и API_HASH, остальное можно оставить по умолчанию
~/MMProBumpBot >>> python main.py
```

Также для быстрого запуска вы можете использовать аргументы:
```shell
~/MMProBumpBot >>> python3 main.py --action (1/2)
# или
~/MMProBumpBot >>> python3 main.py -a (1/2)

# 1 - создать сессию
# 2 - запустить бот
```

## Запуск  бота в фоновом режиме (Linux)
```shell
cd MMProBumpBot

# с логированием
setsid venv/bin/python3 main.py --action 2 >> app.log 2>&1 &

# без логирования
setsid venv/bin/python3 main.py --action 2 > /dev/null 2>&1 &

# Теперь вы можете закрыть консоль и бот продолжит свою работу.
```

### Найти процесс бота
```shell
ps aux | grep "python3 main.py" | grep -v grep
```