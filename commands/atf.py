import requests
import random

async def execute(message, send_message):
    channel_id = message['channel_id']
    content = message['content'].split()
    
    if len(content) < 2:
        await send_message(channel_id, "Usage: ;atf tag1 [tag2 tag3 ...] [amount=1]")
        return

    tags = content[1:-1]
    amount = content[-1]
    try:
        amount = int(amount)
    except ValueError:
        tags.append(content[-1])
        amount = 1
    
    tags = "+".join(tags)
    amount = min(max(amount, 1), 10)  # Limit the amount between 1 and 10

    base_endpoint_url = "https://booru.allthefallen.moe/posts.json?tags={}&limit={}&page={}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "api-key": "PAAvBsBYKHpXKBEyPBKwre4t"
    }

    for _ in range(amount):
        random_page = random.randint(1, 1000)  # Randomly pick a page number
        endpoint_url = base_endpoint_url.format(tags, 1, random_page)
        
        response = requests.get(endpoint_url, headers=headers)
        if response.status_code != 200:
            continue

        posts = response.json()
        if not posts:
            continue

        post = random.choice(posts)
        image_url = post.get('file_url')
        if image_url:
            await send_message(channel_id, image_url)
