from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from kb.kbs import main_keyboard
from kb.inline_kbs import ease_link_kb

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    keyboard = main_keyboard()
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard)

@router.message(F.text == "Приступить")
async def handle_start_action(message: Message):
    await message.answer("Выберите действие:", reply_markup=ease_link_kb())

@router.message(F.text == "Инструкция по использованию бота")
async def handle_guide(message: Message):
    guide_text = (
        "Чтобы добавить товар для отслеживания:\n\n"
        "1. Нажмите кнопку 'Получить цену' и отправьте ссылку на товар с сайта Ozon.\n"
        "2. Бот извлечет данные о товаре, включая цену, изображение и название, и сохранит их в базе данных.\n"
        "3. Вы получите сообщение с информацией о товаре и ссылку для проверки цены.\n"
        "4. Вы можете просматривать список всех добавленных товаров через команду 'Список товаров'.\n"
        "5. Выберите товар, чтобы узнать, изменилась ли цена, и, при необходимости, обновить цену.\n\n"
        "Если вам нужно изменить цену, бот предложит вам обновить данные в базе."
    )
    await message.answer(guide_text, reply_markup=main_keyboard())

@router.message(F.text == "Информация")
async def send_info(message: Message):
    info_message = (
        "Этот бот использует следующие пакеты:\n\n"
        "1. aiogram — для работы с Telegram API.\n"
        "2. asyncpg — для работы с PostgreSQL.\n"
        "3. asyncio — для асинхронного выполнения задач.\n"
        "4. BeautifulSoup — для парсинга HTML-контента.\n"
        "5. aiohttp — для асинхронных HTTP-запросов и обработки вебхуков.\n\n"
        "Эти библиотеки помогают эффективно работать с Telegram-ботом, обрабатывать запросы и взаимодействовать с базой данных."
    )
    await message.answer(info_message, reply_markup=main_keyboard())

@router.message(F.text == "О разработчике")
async def about_developer(message: Message):
    developer_info = (
        "Студент 2 курса Магага\n"
        "Основные навыки: Python, работа с библиотеками aiogram"
    )
    await message.answer(developer_info)
