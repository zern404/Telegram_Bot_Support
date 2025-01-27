from aiogram.types import KeyboardButton as kbb, InlineKeyboardButton as inkb, InlineKeyboardMarkup, ReplyKeyboardMarkup


main = ReplyKeyboardMarkup(keyboard=[
    [kbb(text='⬇️Обжаловать бан⬇️'), kbb(text='Связь с администрацией')],
])

admin_menu = ReplyKeyboardMarkup(keyboard=[
    [kbb(text='Посмотреть логи за 7д')],
    [kbb(text='Очистить логи за 7д')],
    [kbb(text='Выйти в главное меню')]
])

main.resize_keyboard=True
admin_menu.resize_keyboard=True

add_comment_and_chat = InlineKeyboardMarkup(inline_keyboard=[
    [inkb(text='Добавить комментарий и закрыть тикет', callback_data='add_comment')]
])