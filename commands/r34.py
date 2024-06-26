# commands/r34.py

import requests
import random
import asyncio

async def execute(message, send_message):
    channel_id = message['channel_id']
    content = message['content'].split()
    
    if len(content) < 2:
        await send_message(channel_id, "Usage: ;r34 tag1 [tag2 tag3 ...] [amount=1]")
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

    # Define the endpoint URL and headers
    base_endpoint_url = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&tags={}&json=1&limit={}&pid={}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }

    # Fetch the total number of posts for the given tags
    count_endpoint_url = base_endpoint_url.format(tags, 1, 0)
    response = requests.get(count_endpoint_url, headers=headers)
    
    # Check if the response is valid JSON
    try:
        count_data = response.json()
    except ValueError:
        await send_message(channel_id, "Failed to fetch images. Invalid response from API.")
        return

    if not count_data:
        await send_message(channel_id, "No images found.")
        return

    total_posts = len(count_data)
    if total_posts == 0:
        await send_message(channel_id, "No images found.")
        return

    # Calculate the total number of pages
    posts_per_page = 100
    total_pages = (total_posts // posts_per_page) + 1

    selected_posts = []

    # Try fetching random pages to get unique images until we get the desired amount
    for _ in range(amount * 5):  # Attempt more times than the number of images needed
        random_page = random.randint(1, total_pages)  # Randomly pick a page number
        endpoint_url = base_endpoint_url.format(tags, posts_per_page, random_page)
        
        response = requests.get(endpoint_url, headers=headers)
        if response.status_code != 200:
            continue

        try:
            posts = response.json()
        except ValueError:
            continue

        if not posts:
            continue

        random.shuffle(posts)
        for post in posts:
            if len(selected_posts) < amount:
                selected_posts.append(post)
            else:
                break
        
        if len(selected_posts) >= amount:
            break

    if not selected_posts:
        await send_message(channel_id, "No images found.")
        return

    # Send the selected unique images
    for post in selected_posts:
        image_url = post.get('file_url')
        if image_url:
            await send_message(channel_id, image_url)
