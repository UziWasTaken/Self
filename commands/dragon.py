import asyncio

async def execute(event_data, send_message):
    channel_id = event_data['channel_id']
    
    message_1 = "I, who am about to awaken,"
    message_2 = "Am the Heavenly Dragon who has taken the principles of supremacy from God."
    message_3 = "I envy the 'infinite' and I pursue the dream..."
    link_message = "https://media1.tenor.com/m/nMZrznqFD28AAAAC/issei-aura.gif"

    await send_message(channel_id, message_1)
    await asyncio.sleep(3)
    await send_message(channel_id, message_2)
    await asyncio.sleep(3)
    await send_message(channel_id, message_3)
    await asyncio.sleep(3)
    await send_message(channel_id, link_message)
