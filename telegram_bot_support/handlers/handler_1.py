from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import keyboard_1 as kb
from database import models_db as db

router = Router()

class Ban(StatesGroup):
    steam_id_b = State()
    problem_b = State()
    admin_id_b = State()

class Feedback(StatesGroup):
    steam_id_f = State()
    problem_f = State()
    nickname_f = State()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Здраствуйте, это бот тех поддержки', reply_markup=kb.main)



@router.message(F.text == '⬇️Обжаловать бан⬇️')
async def ticket_unban(message: Message, state: FSMContext):
    if not await db.check_ticket_ban(message.from_user.id):#Проверка не открыт ли уже тикет у пользователя
        await state.set_state(Ban.steam_id_b)
        await message.answer('⬇️Введите ваш steam id⬇️')
    else:
        await message.answer('Вы уже открыли тикет')


@router.message(Ban.steam_id_b)
async def unban_process_1(message: Message, state: FSMContext):
    await state.update_data(steam_id_b=message.text)
    await state.set_state(Ban.admin_id_b)

    await message.answer('⬇️Введите steam id или ник админа который вас забанил.⬇️')


@router.message(Ban.admin_id_b)
async def unban_process_2(message: Message, state: FSMContext):
    await state.update_data(admin_id_b=message.text)
    await state.set_state(Ban.problem_b)

    await message.answer('Опишите что случилось.')


@router.message(Ban.problem_b)
async def unban_process_3(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    await state.update_data(problem_b=message.text)

    data = await state.get_data()
    steam_id_b = data.get('steam_id_b')
    problem_b = data.get('problem_b')
    admin_id_b = data.get('admin_id_b')

    try:
        await db.add_unban_tckt(tg_id, steam_id_b, problem_b, admin_id_b, 'Open')#Запись тикета в бд
        await message.answer('✅Вы успешно заполнили тикет✅\nожидайте, скоро вам ответит модератор')
        await state.clear()

    except Exception as e:
        await message.answer(e)


@router.message(F.text == 'Связь с администрацией')
async def ticket_feedback(message: Message, state: FSMContext):
    if not await db.check_ticket_feedback(message.from_user.id):#Проверка не открыт ли уже тикет у пользователя
        await state.set_state(Feedback.steam_id_f)
        await message.answer('Введите ваш steam id')
    else:
        await message.answer('Вы уже открыли тикет')


@router.message(Feedback.steam_id_f)
async def feedback_process_1(message: Message, state: FSMContext):
    await state.update_data(steam_id_f=message.text)
    await state.set_state(Feedback.nickname_f)

    await message.answer('Теперь введите ваш никнейм')


@router.message(Feedback.nickname_f)
async def feedback_process_2(message: Message, state: FSMContext):
    await state.update_data(nickname_f=message.text)
    await state.set_state(Feedback.problem_f)

    await message.answer('Опишите что случилось.')


@router.message(Feedback.problem_f)
async def feedback_process_3(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    await state.update_data(problem_f=message.text)

    data = await state.get_data()
    steam_id_f = data.get('steam_id_f')
    problem_f = data.get('problem_f')
    nickname_f = data.get('nickname_f')

    try:
        await db.add_feedback_tckt(tg_id, steam_id_f, nickname_f, problem_f, 'Open')#Запись тикета в бд

        await message.answer('✅Вы успешно заполнили тикет✅\nожидайте, скоро вам ответит модератор')

        await state.clear()

    except Exception as e:
        await message.answer(e)