import re

from time import thread_time
from xml.dom.expatbuilder import theDOMImplementation
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from keyboards import keyboard_1 as kb
from database import models_db as db
from config import TOKEN, chat_id
from sqlalchemy.dialects.mysql import match
from sqlalchemy.util import await_only

router_callbacks = Router()

bot = Bot(TOKEN)
chat_id = chat_id

class Chat(StatesGroup):
    chat_info = State()

class Comments(StatesGroup):
    comment = State()

@router_callbacks.callback_query(F.data == 'add_comment')
async def add_comment(callback: CallbackQuery, state: FSMContext):
    '''Функция для записи коментария от админа в теме(топике)'''

    match = re.search(r'#(\d+)', callback.message.text)
    ticket_id = int(match.group(1))
    user_tg_id = await db.get_user_tg_id_by_ticket(ticket_id)

    await state.update_data(ticket_id=ticket_id, user_tg_id=user_tg_id)
    await callback.answer('')

    data = await state.get_data()
    ticket_id = data.get('ticket_id')
    user_tg_id = data.get('user_tg_id')

    await db.update_ticket_status(ticket_id)#Смена статуса тикета на Close

    await state.set_state(Comments.comment)
    await callback.message.answer('Введите текст комментария')


@router_callbacks.message(Comments.comment)
async def close(message: Message, state: FSMContext):

    await state.update_data(comment=message.text)

    data = await state.get_data()

    ticket_id = data.get('ticket_id')
    user_tg_id = data.get('user_tg_id')
    comment = data.get('comment')
    admin_name = message.from_user.full_name
    user = await bot.get_chat(user_tg_id)

    try:
        '''Логи об активности администрации'''
        await db.add_log(
            tg_id=message.from_user.id,
            admin_name=admin_name,
            action=f"Ваш тикет закрыт #{ticket_id}",
            comment=comment
        )

        '''Отправка сообщения пользователю что тикет закрыт'''

        await bot.send_message(
            chat_id=user_tg_id,
            text=f"❗️@{user.username}, ваш тикет #{ticket_id} был закрыт модератором.❗️\nКомментарий: {comment}"
        )

        '''Удаления темы(топика) у админов и закрытия тикета)'''

        try:
            await bot.close_forum_topic(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id
            )

            await bot.delete_forum_topic(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id
            )

            await db.delete_ticket_by_id(ticket_id)#удаления топика из базы данных по тг id
            await state.clear()

        except Exception as forum_error:
            await state.clear()
            await message.answer(f"Ошибка при закрытии тикета: {forum_error}")

    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")