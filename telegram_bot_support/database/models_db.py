import sqlite3 as sq
import datetime

from mailbox import Message
from typing import List, Tuple
from aiogram import Bot

from handlers.admin_handler import create_new_topic_unban, create_new_topic_feedback
from config import TOKEN, chat_id, admins

bot = Bot(TOKEN)
chat_id = chat_id
admins = admins

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

db = sq.connect('tickets.db')
cur = db.cursor()

async def db_run():
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Tickets_ban(id INTEGER, steam_id text, problem text, admin_ban_id text, ticket_id INTEGER PRIMARY KEY AUTOINCREMENT, status text)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Tickets_feedback(id INTEGER, steam_id text, nickname text, problem text, ticket_id INTEGER PRIMARY KEY AUTOINCREMENT, status text)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Logs(id INTEGER, admin_name text, action text, comment text, timestamp text)")
    cur.execute("CREATE TABLE IF NOT EXISTS Topics(ticket_id INTEGER, message_thread_id INTEGER)")

    db.commit()

async def save_topic_to_db(ticket_id: int, message_thread_id: int):
    '''Сохраняем id топика и tg_id пользователя(чтоб в будущем получать ticket_id по id топика)'''

    cur.execute(
        "INSERT INTO Topics (ticket_id, message_thread_id) VALUES (?, ?)",
        (ticket_id, message_thread_id)
    )
    db.commit()

async def delete_ticket_by_id(ticket_id: int):
    try:
        cur.execute("DELETE FROM Topics WHERE ticket_id = ?", (ticket_id,))
        db.commit()

    except Exception as e:
        await bot.send_message(chat_id, f"Ошибка при удалении топика {e}")




async def get_message_thread_id(ticket_id: int) -> int:
    cur.execute("SELECT message_thread_id FROM Topics WHERE ticket_id = ?", (ticket_id,))
    result = cur.fetchone()
    return result[0] if result else None

async def get_user_tg_id_by_ticket(ticket_id: int) -> int:
    cur.execute("SELECT id FROM Tickets_ban WHERE ticket_id = ?", (ticket_id,))
    result = cur.fetchone()
    if result:
        return result[0]

    cur.execute("SELECT id FROM Tickets_feedback WHERE ticket_id = ?", (ticket_id,))
    result_2 = cur.fetchone()
    
    if result_2:
        return result_2[0]

    return None

async def get_ticket_id_by_thread_id(thread_id: int) -> int:
    cur.execute("SELECT ticket_id FROM Topics WHERE message_thread_id = ?", (thread_id,))
    result = cur.fetchone()
    return result[0]



async def update_ticket_status(ticket_id: int):
    cur.execute(
        "UPDATE Tickets_feedback SET status = ? WHERE ticket_id = ?",
        ("Close", ticket_id)
    )
    cur.execute(
        "UPDATE Tickets_ban SET status = ? WHERE ticket_id = ?",
        ("Close", ticket_id)
    )
    db.commit()

async def check_ticket_ban(tg_id: int) -> bool:
    cur.execute("SELECT * FROM Tickets_ban WHERE id = ? AND status = 'Open'", (tg_id,))
    result = cur.fetchone()
    return result is not None

async def check_ticket_feedback(tg_id: int) -> bool:
    cur.execute("SELECT * FROM Tickets_feedback WHERE id = ? AND status = 'Open'", (tg_id,))
    result = cur.fetchone()
    return result is not None




async def add_unban_tckt(tg_id: int, steam_id: str, problem: str, admin_ban_id: str, status: str):
    '''Добавления тикета в бд'''

    cur.execute("""INSERT INTO Tickets_ban (id, steam_id, problem, admin_ban_id, status) VALUES (?, ?, ?, ?, ?)""",
                (tg_id, steam_id, problem, admin_ban_id, status))
    db.commit()

    cur.execute("SELECT ticket_id, steam_id, problem, admin_ban_id, status FROM Tickets_ban WHERE id = ?", (tg_id,))
    ticket = cur.fetchone()
    try:
        if ticket:
            await create_new_topic_unban(
                ticket_id=ticket[0],
                steam_id=ticket[1],
                problem=ticket[2],
                admin_ban_id=ticket[3],
                status=ticket[4]
            )
    except Exception as e:
        await bot.send_message(chat_id, f"unban {e}")

async def add_feedback_tckt(tg_id: int, steam_id: str, problem: str, nickname: str, status: str):
    '''Добавления тикета в бд'''

    cur.execute("""INSERT INTO Tickets_feedback (id, steam_id, nickname, problem, status) VALUES (?, ?, ?, ?, ?)""",
                (tg_id, steam_id, nickname, problem, status))
    db.commit()

    cur.execute("SELECT ticket_id, steam_id, nickname, problem, status FROM Tickets_feedback WHERE id = ?", (tg_id,))
    ticket = cur.fetchone()
    try:
        if ticket:
            await create_new_topic_feedback(
                ticket_id=ticket[0],
                steam_id=ticket[1],
                nickname=ticket[2],
                problem=ticket[3],
                status=ticket[4]
            )
    except Exception as e:
        await bot.send_message(chat_id, f"feedback {e}")





async def add_log(tg_id: int, admin_name: str, action: str, comment: str):
    try:
        cur.execute("INSERT INTO Logs (id, admin_name, action, comment, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (tg_id, admin_name, action, comment, timestamp)
                    )
        db.commit()

    except Exception as e:
        await bot.send_message(chat_id, f"логи {e}")

async def get_logs_for_last_week(message: Message):
    '''Получаем все действия модераторов за последнюю неделю(для админов)'''

    try:
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
        one_week_ago = now - datetime.timedelta(days=7)
        formatted_date = one_week_ago.strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            SELECT id, admin_name, action, comment, timestamp 
            FROM Logs 
            WHERE timestamp >= ? 
            ORDER BY timestamp DESC
        """, (formatted_date,))

        logs = cur.fetchall()

        if logs:
            message_a = "Логи за последнюю неделю:\n"
            for log in logs:
                message_a += (
                    f"📝 ID: {log[0]}\n"
                    f"👨‍💻 Модератор: {log[1]}\n"
                    f"📋 Действие: {log[2]}\n"
                    f"💬 Комментарий: {log[3]}\n"
                    f"🕒 Время: {log[4]}\n\n"
                )

            for chunk in [message_a[i:i + 4096] for i in range(0, len(message_a), 4096)]:
                await bot.send_message(message.from_user.id, chunk)
        else:
            await bot.send_message(message.from_user.id, "Логи за последнюю неделю отсутствуют.")
    except Exception as e:
        await bot.send_message(message.from_user.id, f"Ошибка при получении логов: {e}")

async def clear_logs_for_last_week(message: Message):
    '''Удаления логов'''
    try:
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
        one_week_ago = now - datetime.timedelta(days=7)
        formatted_date = one_week_ago.strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("DELETE FROM Logs WHERE timestamp >= ?", (formatted_date,))
        db.commit()

        await bot.send_message(message.from_user.id, "Логи были успешно удалены.")
    except Exception as e:
        await bot.send_message(message.from_user.id, f"Ошибка при очистке логов: {e}")