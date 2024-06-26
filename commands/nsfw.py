import requests
import random
import asyncio

API_KEY = 'cFbTPIV15F-RbG6A4UoxiEP0dHWDBhP-tIbpTmjOt8'
BASE_URL = 'https://api.night-api.com/images/nsfw/'
CATEGORIES = [
    "anal", "ass", "boobs", "gonewild", "hanal", "hass", "hboobs", 
    "hentai", "hkitsune", "hmidriff", "hneko", "hthigh", "neko", 
    "paizuri", "pgif", "pussy", "tentacle", "thigh", "yaoi"
]

async def execute(message, send_message):
    channel_id = message['channel_id']
    content = message['content'].split()
    
    if len(content) < 2:
        await send_message(channel_id, "Usage: ;nsfw category [amount=1]")
        return

    category = content[1].lower()
    try:
        amount = int(content[2]) if len(content) > 2 else 1
    except ValueError:
        await send_message(channel_id, "Amount must be a number.")
        return

    amount = min(max(amount, 1), 10)  # Limit the amount between 1 and 10

    headers = {
        "authorization": API_KEY
    }

    for _ in range(amount):
        if category == 'random':
            category_to_use = random.choice(CATEGORIES)
        else:
            category_to_use = category

        response = requests.get(f"{BASE_URL}{category_to_use}", headers=headers)
        
        if response.status_code != 200:
            await send_message(channel_id, f"Failed to fetch images. Status code: {response.status_code}")
            return

        data = response.json()
        if data['status'] == 200 and 'url' in data['content']:
            image_url = data['content']['url']
            await send_message(channel_id, image_url)
        else:
            await send_message(channel_id, "Failed to fetch images.")
