# Telegram_Bot_Support
Бот технической поддержки для игр(сервера в Rust), изменив код можно сделать для чего угодно. Интересная реализация с темами.

В боте реализована система тикетов как в Discord, можно открыть не больше 1, только без чата.
Система логирования закрытия определенного тикета определенным человеком. Добавляеш в список id админов и они через команду /admin_panel могут смотреть.
При запуске бота будет создан файл базы данных.

Для работы бота нужно изменить файл config.py|Добавить бота в групу админов, изменить групу так чтоб можно было создавать темы, выдать боту возможность создавать темы и права админа.
Вся настройка конфиденциальной информации в config.py.

Установка библиотек необходимых для работы бота 
1. aiogram3
2. sqlite3
3. sqlalchemy
4. asyncio


Мой первый +- крупный project
