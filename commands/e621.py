import requests
import random

login = 'Midnightgamese2'
api_key = 'XqA9YbwCUbxbfMzzRwfbM65y'
user_agent = 'MyDiscordBot/1.0 (by your_username on e621)'

async def execute(message, send_message):
    channel_id = message['channel_id']
    content = message['content'].split()
    
    if len(content) < 2:
        await send_message(channel_id, "Usage: ;e621 tag1 [tag2 tag3 ...] [amount=1]")
        return

    tags = content[1:-1]
    amount = content[-1]
    try:
        amount = int(amount)
    except ValueError:
        tags.append(content[-1])
        amount = 1
    
    tags = " ".join(tags)
    amount = min(max(amount, 1), 10)  # Limit the amount between 1 and 10

    api_url = f"https://e621.net/posts.json"
    headers = {
        "User-Agent": user_agent
    }
    auth = (login, api_key)

    for _ in range(amount):
        random_page = random.randint(1, 1000)  # Randomly pick a page number
        params = {
            "tags": tags,
            "limit": 1,
            "page": random_page
        }
        
        response = requests.get(api_url, headers=headers, auth=auth, params=params)
        if response.status_code != 200:
            continue

        posts = response.json().get('posts', [])
        if not posts:
            continue

        post = random.choice(posts)
        image_url = post['file']['url']
        if image_url:
            await send_message(channel_id, image_url)
