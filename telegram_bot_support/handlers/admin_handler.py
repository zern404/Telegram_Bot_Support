import asyncio
import re

from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram import Bot

from config import TOKEN, chat_id, admins
from keyboards import keyboard_1 as kb
from database import models_db as db

admin_router = Router()
admins = admins
chat_id = chat_id

bot = Bot(TOKEN)

async def who_admin(message: Message) -> bool:
    tg_id = message.from_user.id
    return tg_id in admins

async def create_new_topic_unban(ticket_id: int, steam_id: str, problem: str, admin_ban_id: str, status: str):
    '''Создание темы(топика)'''

    user_tg_id = await db.get_user_tg_id_by_ticket(ticket_id)
    user = await bot.get_chat(user_tg_id)

    try:
        topic_name = f"Обжалования #{ticket_id}"
        topic = await bot.create_forum_topic(chat_id=chat_id, name=topic_name)

        if topic and topic.message_thread_id:
            message_thread_id = topic.message_thread_id
            await bot.send_message(
                chat_id=chat_id,
                message_thread_id=message_thread_id,
                text=(
                    f"📝 Тикет #{ticket_id}\n\n"
                    f"👤 Steam ID: {steam_id}\n"
                    f"❓ Проблема: {problem}\n"
                    f"👮 Забанил админ: {admin_ban_id}\n"
                    f"📂 Статус: {status}\n"
                    f"👤Телеграм игрока: @{user.username}"
                ), reply_markup=kb.add_comment_and_chat
            )
            await db.save_topic_to_db(ticket_id, message_thread_id)

        else:
            await bot.send_message(chat_id, 'Не удалось создать тему')

    except Exception as e:
        print(e)


async def create_new_topic_feedback(ticket_id: int, steam_id: str, nickname: str, problem: str, status: str):
    '''Создание темы(топика)'''

    try:
        topic_name = f"Обратная связь #{ticket_id}"
        topic = await bot.create_forum_topic(chat_id=chat_id, name=topic_name)

        if topic and topic.message_thread_id:
            message_thread_id = topic.message_thread_id
            await bot.send_message(
                chat_id=chat_id,
                message_thread_id=message_thread_id,
                text=(
                    f"📝 Тикет #{ticket_id}\n\n"
                    f"👤 Steam ID: {steam_id}\n"
                    f"🎮 Никнейм: {nickname}\n"
                    f"❓ Проблема: {problem}\n"
                    f"📂 Статус: {status}"
                ),
                reply_markup=kb.add_comment_and_chat
            )
            await db.save_topic_to_db(ticket_id, message_thread_id)

        else:
            await bot.send_message(chat_id, 'Не удалось создать тему')

    except Exception as e:
        print(e)


'''Все что ниже админ меню.'''


@admin_router.message(Command('admin_panel'))
async def admin_panel(message: Message):
    if not await who_admin(message):
        await message.answer("❗️У вас нет прав для выполнения этой операции.❗️")

    else:
        await bot.send_message(message.from_user.id, 'Вы вошли в админ панель', reply_markup=kb.admin_menu)


@admin_router.message(F.text == 'Посмотреть логи за 7д')
async def admin_panel(message: Message):
    if not await who_admin(message):
        await message.answer("❗️У вас нет прав для выполнения этой операции.❗️")

    else:
        await bot.send_message(message.from_user.id, 'Все админы которые закрывали тикеты за 7д')
        await db.get_logs_for_last_week(message)


@admin_router.message(F.text == 'Очистить логи за 7д')
async def admin_panel(message: Message):
    if not await who_admin(message):
        await message.answer("❗️У вас нет прав для выполнения этой операции.❗️")
    else:
        await db.clear_logs_for_last_week(message)


@admin_router.message(F.text == 'Выйти в главное меню')
async def admin_exit(message: Message):
    await message.answer('Вы вышли с админ панели.', reply_markup=kb.main)