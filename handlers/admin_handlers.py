from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config.config import ADMIN_LOGIN, ADMIN_PASSWORD
import asyncpg
from kb.kbs import main_keyboard
from kb.inline_kbs import ease_link_kb

router = Router()

class AdminPanelState(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

@router.message(F.text == "Админ Панель")
async def admin_panel(message: Message, state: FSMContext):
    await state.set_state(AdminPanelState.waiting_for_login)
    await message.answer("Введите логин администратора:")

@router.message(AdminPanelState.waiting_for_login)
async def handle_login(message: Message, state: FSMContext):
    login = message.text.strip()
    if login == ADMIN_LOGIN:
        await state.set_state(AdminPanelState.waiting_for_password)
        await message.answer("Введите пароль:")
    else:
        await message.answer("Неверный логин. Попробуйте снова.")
        await message.answer("Введите логин администратора:")

@router.message(AdminPanelState.waiting_for_password)
async def handle_password(message: Message, state: FSMContext):
    password = message.text.strip()
    if password == ADMIN_PASSWORD:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Количество записей в БД")],
                [KeyboardButton(text="Удалить все записи из БД")],
                [KeyboardButton(text="Выход из админ панели")],
            ],
            resize_keyboard=True,
        )
        await message.answer("Успешная аутентификация!", reply_markup=keyboard)
        await state.clear()
    else:
        await message.answer("Неверный пароль. Попробуйте снова.")
        await message.answer("Введите пароль:")

@router.message(F.text == "Количество записей в БД")
async def count_records(message: Message):
    try:
        conn = await asyncpg.connect(user='postgres', password='qptz23', database='bot', host='localhost')
        result = await conn.fetchval("SELECT COUNT(*) FROM products")
        await conn.close()
        await message.answer(f"Количество записей в базе данных: {result}")
    except Exception as e:
        await message.answer("Произошла ошибка при подключении к базе данных.")
        print(f"Error: {e}")

@router.message(F.text == "Удалить все записи из БД")
async def delete_all_records(message: Message):
    try:
        conn = await asyncpg.connect(user='postgres', password='qptz23', database='bot', host='localhost')
        await conn.execute("DELETE FROM products")
        await conn.close()
        await message.answer("Все записи из базы данных были удалены.")
    except Exception as e:
        await message.answer("Произошла ошибка при удалении записей.")
        print(f"Error: {e}")

@router.message(F.text == "Выход из админ панели")
async def exit_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вышли из админ панели.", reply_markup=main_keyboard())
    await message.answer("Продолжаем работу", reply_markup=ease_link_kb())
