from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Приступить")],
            [KeyboardButton(text="Инструкция по использованию бота")],
            [KeyboardButton(text="Информация")],
            [KeyboardButton(text="Админ Панель")],
            [KeyboardButton(text="О разработчике")],

        ],
        resize_keyboard=True,
    )
