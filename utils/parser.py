import aiohttp
from bs4 import BeautifulSoup
import re

VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp')


def is_valid_image_url(url: str) -> bool:
    return url.lower().endswith(VALID_IMAGE_EXTENSIONS)


def clean_price(price_str: str) -> float:
    cleaned_price = re.sub(r'[^\d,]', '', price_str)
    cleaned_price = cleaned_price.replace(' ', '')
    cleaned_price = cleaned_price.replace('₽', '')
    cleaned_price = cleaned_price.replace(',', '.')

    try:
        return float(cleaned_price)
    except ValueError:
        return None


async def get_price_and_image_from_ozon(product_url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(product_url) as response:
            if response.status != 200:
                return "Error: Unable to fetch page", "Error: Unable to fetch image", None

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            name_tag = soup.find('h1', {'class': 'wl7_27 tsHeadline550Medium'})
            if name_tag:
                name = name_tag.text.strip()
            else:
                name = "Product name not found"

            price_tag = soup.find('span', {'class': 'v6l_27 lv5_27'})
            if price_tag:
                price_str = price_tag.text.strip().replace('\u202F', ' ')
                price = clean_price(price_str)
            else:
                price = None

            img_tag = soup.find('img', {'class': 'vj7_27 v7j_27 b933-a'})
            if img_tag:
                img_url = img_tag.get('src')
                if img_url and not is_valid_image_url(img_url):
                    img_url = "Image not found"
            else:
                img_url = "Image not found"

            return price, img_url, name
