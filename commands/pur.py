import requests
import asyncio
import re

BASE_URL = 'https://purrbot.site/api/img/sfw'
CATEGORIES = {
    "angry": "gif",
    "background": "img",
    "bite": "gif",
    "blush": "gif",
    "comfy": "gif",
    "cry": "gif",
    "cuddle": "gif",
    "dance": "gif",
    "eevee": "gif",
    "fluff": "gif",
    "holo": "img",
    "hug": "gif",
    "icon": "img",
    "kiss": "gif",
    "kitsune": "img",
    "lay": "gif",
    "lick": "gif",
    "neko": "gif",
    "okami": "img",
    "pat": "gif",
    "poke": "gif",
    "pout": "gif",
    "senko": "img",
    "shiro": "img",
    "slap": "gif",
    "smile": "gif",
    "tail": "gif",
    "tickle": "gif"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json",
    "Connection": "keep-alive",
    "DNT": "1",
    "Referer": "https://purrbot.site"
}

async def execute(message, send_message):
    channel_id = message['channel_id']
    content = message['content'].split()

    if len(content) < 2:
        await send_message(channel_id, "Usage: ;pur category or ;pur category @user")
        return

    category = content[1].lower()
    if category not in CATEGORIES:
        await send_message(channel_id, f"Invalid category. Available categories are: {', '.join(CATEGORIES.keys())}")
        return

    mention_match = re.search(r'@(\w+)', message['content'])
    if mention_match:
        mentioned_user = mention_match.group(0)
        sender = message['author']['username']
        await fetch_and_send_image(channel_id, category, mentioned_user, sender, send_message)
    else:
        await fetch_and_send_image(channel_id, category, None, None, send_message)

async def fetch_and_send_image(channel_id, category, mentioned_user, sender, send_message):
    url = f"{BASE_URL}/{category}/{CATEGORIES[category]}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 403:
        await send_message(channel_id, f"Access forbidden to the path {url}")
        return
    elif response.status_code == 404:
        await send_message(channel_id, f"Path does not contain images {url}")
        return
    elif response.status_code != 200:
        await send_message(channel_id, f"Failed to fetch images. Status code: {response.status_code}\nURL: {url}\nRaw response: {response.text}")
        return

    content_type = response.headers.get('Content-Type')
    if 'application/json' in content_type:
        try:
            data = response.json()
        except ValueError:
            await send_message(channel_id, f"Failed to fetch images. Invalid JSON response from API at {url}\nRaw response: {response.text}")
            return

        if not data.get('error') and 'link' in data:
            image_url = data['link']
            if mentioned_user and sender:
                action_text = category.replace("_", " ")
                message = f"@{sender} (this user is me) is {action_text} {mentioned_user}"
                await send_message(channel_id, f"{message}\n{image_url}")
            else:
                await send_message(channel_id, image_url)
        else:
            await send_message(channel_id, f"Failed to fetch images. API response: {data}")
    else:
        await send_message(channel_id, f"Failed to fetch images. Unexpected content type: {content_type}\nRaw response: {response.text}")
