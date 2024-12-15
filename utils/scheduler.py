import asyncio
import asyncpg
import schedule
from datetime import datetime
from utils.parser import get_price_and_image_from_ozon

async def get_db_connection():
    return await asyncpg.connect(user='postgres', password='qptz23', database='bot', host='localhost')

async def record_price_change(product_id: int, price: float):
    conn = await get_db_connection()
    timestamp = datetime.now()

    row = await conn.fetchrow("""
        SELECT price
        FROM price_history
        WHERE product_id = $1
        ORDER BY timestamp ASC
        LIMIT 1
    """, product_id)

    if not row:
        product_row = await conn.fetchrow("""
            SELECT price
            FROM products
            WHERE id = $1
        """, product_id)

        if product_row:
            price = product_row['price']

    await conn.execute("""
        INSERT INTO price_history (product_id, price, timestamp) 
        VALUES ($1, $2, $3)
    """, product_id, price, timestamp)
    await conn.close()

async def price_update_task():
    conn = await get_db_connection()
    rows = await conn.fetch("SELECT id, url FROM products")

    for row in rows:
        product_id = row['id']
        url = row['url']
        price, img_url, name = await get_price_and_image_from_ozon(url)

        if price is not None:
            await record_price_change(product_id, price)

    await conn.close()

def scheduler_setup():
    def job():
        asyncio.ensure_future(price_update_task())

    schedule.every(10).minutes.do(job)

    async def scheduler():
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)

    asyncio.create_task(scheduler())
