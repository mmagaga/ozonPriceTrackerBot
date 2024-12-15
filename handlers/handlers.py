import os
import asyncpg
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram import Dispatcher
from utils.parser import get_price_and_image_from_ozon
from kb.inline_kbs import ease_link_kb
from utils.price_graph import plot_price_graph

router = Router()

class Form(StatesGroup):
    waiting_for_url = State()

async def get_db_connection():
    return await asyncpg.connect(user='postgres', password='qptz23', database='bot', host='localhost')

def generate_keyboard(rows):
    inline_buttons = []
    for row in rows:
        product_button = InlineKeyboardButton(
            text=f"🔹 {row['name']}",
            callback_data=f"select_product_{row['id']}"
        )
        inline_buttons.append([product_button])
    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)

class LoggingMiddleware(BaseMiddleware):
    async def on_process_message(self, message: Message, data: dict):
        pass

def setup_middleware(dispatcher: Dispatcher):
    dispatcher.add_middleware(LoggingMiddleware())

@router.callback_query(F.data == 'get_price')
async def handle_get_price_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_url)
    await callback_query.message.answer("Пожалуйста, отправьте ссылку на товар Ozon.")
    await callback_query.answer()

@router.message(Form.waiting_for_url)
async def get_product_price(message: Message, state: FSMContext):
    url = message.text.strip()

    if 'ozon.ru' not in url:
        await message.answer("Пожалуйста, отправьте ссылку на товар с сайта Ozon.")
        return

    price, img_url, name = await get_price_and_image_from_ozon(url)

    conn = await asyncpg.connect(user='postgres', password='qptz23', database='bot', host='localhost')
    try:
        await conn.execute("""
            INSERT INTO products (name, price, image_url, url, user_id)
            VALUES ($1, $2, $3, $4, $5)
        """, name, price, img_url, url, message.from_user.id)  # Сохраняем user_id
    except Exception as e:
        pass
    finally:
        await conn.close()

    if img_url != "Изображение не найдено" and img_url != "Изображение не найдено или ссылка ведет на видео":
        await message.answer_photo(img_url, caption=f"Название товара: {name}\nЦена товара: {price}")
    else:
        await message.answer(f"Название товара: {name}\nИзображение не найдено или ссылка ведет на видео. Цена товара: {price}")

    keyboard = ease_link_kb()
    await message.answer("Хотите проверить цену другого товара?", reply_markup=keyboard)

    await state.clear()


@router.callback_query(F.data == 'list_products')
async def handle_list_products(callback_query: CallbackQuery):
    try:
        conn = await asyncpg.connect(user='postgres', password='qptz23', database='bot', host='localhost')

        rows = await conn.fetch(
            "SELECT id, name, price, url FROM products WHERE user_id = $1 ORDER BY created_at DESC",
            callback_query.from_user.id
        )

        if not rows:
            await callback_query.message.answer(
                "Продукты не найдены.",
                reply_markup=ease_link_kb()
            )
        else:
            products_message = "Список продуктов:\n\n"
            keyboard = generate_keyboard(rows)

            for row in rows:
                products_message += f"🔹 <b>{row['name']}</b>\nЦена: {row['price']} ₽\nСсылка: {row['url']}\n\n"

            await callback_query.message.answer(
                products_message,
                parse_mode='HTML',
                reply_markup=keyboard
            )

        await conn.close()

    except Exception as e:
        await callback_query.message.answer(
            "Ошибка при получении списка продуктов.",
            reply_markup=ease_link_kb()
        )

    await callback_query.answer()


@router.callback_query(F.data.startswith('select_product_'))
async def handle_select_product(callback_query: CallbackQuery):
    try:
        product_id = int(callback_query.data.split('_')[-1])
        user_id = callback_query.from_user.id

        conn = await get_db_connection()

        selected_product = await conn.fetchrow(
            "SELECT id, name, price, url FROM products WHERE id = $1 AND user_id = $2",
            product_id, user_id
        )

        if selected_product:
            selected_product_url = selected_product['url']

            price, img_url, name = await get_price_and_image_from_ozon(selected_product_url)

            existing_product_price = selected_product['price']

            try:
                graph_filename = await plot_price_graph(product_id)

                if graph_filename:
                    with open(graph_filename, 'rb') as f:
                        file_bytes = f.read()
                        graph = BufferedInputFile(file_bytes, filename='price_graph.png')
                        await callback_query.message.answer_photo(graph)

                    if os.path.exists(graph_filename):
                        os.remove(graph_filename)
                else:
                    await callback_query.message.answer("Ошибка при построении графика. Данные для графика отсутствуют.")
            except Exception as e:
                await callback_query.message.answer("Ошибка при генерации графика.")

            if price == existing_product_price:
                await callback_query.message.answer("Цена не изменилась.")
                keyboard = ease_link_kb()
                await callback_query.message.answer("Вы можете выбрать другой продукт из списка.", reply_markup=keyboard)
                await callback_query.answer()
                return
            elif price < existing_product_price:
                await callback_query.message.answer(
                    f"Цена уменьшилась. Была: {existing_product_price} ₽, стала: {price} ₽. 📉")
            else:
                await callback_query.message.answer(
                    f"Цена увеличилась. Была: {existing_product_price} ₽, стала: {price} ₽. 💹")

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"Обновить цену на {price} ₽",
                                      callback_data=f'update_price_{product_id}_{price}')],
                [InlineKeyboardButton(text="Отменить", callback_data='cancel_update')]
            ])

            await callback_query.message.answer(
                "Хотите перезаписать цену товара?", reply_markup=keyboard
            )

        else:
            await callback_query.message.answer("Продукт не найден в базе данных или он не принадлежит вам.")

        await conn.close()

    except Exception as e:
        await callback_query.message.answer("Ошибка при проверке продукта.")

    await callback_query.answer()

@router.callback_query(F.data.startswith('update_price_'))
async def handle_update_price(callback_query: CallbackQuery):
    try:
        parts = callback_query.data.split('_')

        if len(parts) < 4:
            await callback_query.message.answer("Неверный формат данных для обновления цены.")
            return

        _, _, product_id, new_price = parts
        product_id = int(product_id)

        try:
            new_price = round(float(new_price), 2)
        except ValueError:
            await callback_query.message.answer("Неверный формат цены.")
            return

        conn = await get_db_connection()

        await conn.execute("""
            UPDATE products
            SET price = $1
            WHERE id = $2
        """, new_price, product_id)

        await callback_query.message.answer(f"Цена для продукта обновлена на {new_price} ₽.")

        keyboard = ease_link_kb()
        await callback_query.message.answer("Вы можете выбрать другой продукт из списка.", reply_markup=keyboard)

        await conn.close()

    except Exception as e:
        await callback_query.message.answer("Ошибка при обновлении цены.")

    await callback_query.answer()

@router.callback_query(F.data == 'cancel_update')
async def cancel_update(callback_query: CallbackQuery):
    keyboard = ease_link_kb()
    await callback_query.message.answer("Цена не была обновлена.", reply_markup=keyboard)
    await callback_query.answer()