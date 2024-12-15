from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def ease_link_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Получить цену продукта💰", callback_data='get_price')],
        [InlineKeyboardButton(text="Список продуктов📃", callback_data='list_products')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
