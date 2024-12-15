
import asyncpg
import matplotlib.pyplot as plt
from datetime import datetime


async def get_db_connection():
    return await asyncpg.connect(user='postgres', password='qptz23', database='bot', host='localhost')


async def get_price_data(product_id: int):
    conn = await get_db_connection()
    rows = await conn.fetch("""
        SELECT price, timestamp
        FROM price_history
        WHERE product_id = $1
        ORDER BY timestamp ASC
    """, product_id)
    await conn.close()

    prices = [row['price'] for row in rows]
    timestamps = [row['timestamp'] for row in rows]
    return timestamps, prices


async def get_product_name(product_id: int):
    conn = await get_db_connection()
    row = await conn.fetchrow("""
        SELECT name
        FROM products
        WHERE id = $1
    """, product_id)
    await conn.close()
    return row['name'] if row else None


async def plot_price_graph(product_id: int):
    timestamps, prices = await get_price_data(product_id)

    if not timestamps or not prices:
        return

    product_name = await get_product_name(product_id)
    if not product_name:
        return

    timestamps = [datetime.strptime(str(ts).split('.')[0], "%Y-%m-%d %H:%M:%S") for ts in timestamps]

    plt.figure(figsize=(10, 6))

    for i in range(1, len(prices)):
        color = 'gray'
        if prices[i] > prices[i - 1]:
            color = 'red'
        elif prices[i] < prices[i - 1]:
            color = 'green'

        plt.plot([timestamps[i - 1], timestamps[i]], [prices[i - 1], prices[i]], marker='o', linestyle='-', color=color)

    plt.title(f'График изменения цены товара: {product_name}')
    plt.xlabel('Время')
    plt.ylabel('Цена (руб.)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    graph_filename = f'price_graph_{product_id}.png'
    plt.savefig(graph_filename)
    plt.close()

    return graph_filename
