import requests
import json
import asyncio
import websockets
import importlib
import os
import aiohttp
import ctypes

# Set the CMD window title
ctypes.windll.kernel32.SetConsoleTitleW("GrabinDragon")

# Clear the console
os.system('cls')

# Define the ASCII art in red
ascii_art = """
\033[91m
  ▄████  ██▀███   ▄▄▄       ▄▄▄▄    ██▓ ███▄    █ ▓█████▄  ██▀███   ▄▄▄        ▄████  ▒█████   ███▄    █ 
 ██▒ ▀█▒▓██ ▒ ██▒▒████▄    ▓█████▄ ▓██▒ ██ ▀█   █ ▒██▀ ██▌▓██ ▒ ██▒▒████▄     ██▒ ▀█▒▒██▒  ██▒ ██ ▀█   █ 
▒██░▄▄▄░▓██ ░▄█ ▒▒██  ▀█▄  ▒██▒ ▄██▒██▒▓██  ▀█ ██▒░██   █▌▓██ ░▄█ ▒▒██  ▀█▄  ▒██░▄▄▄░▒██░  ██▒▓██  ▀█ ██▒
░▓█  ██▓▒██▀▀█▄  ░██▄▄▄▄██ ▒██░█▀  ░██░▓██▒  ▐▌██▒░▓█▄   ▌▒██▀▀█▄  ░██▄▄▄▄██ ░▓█  ██▓▒██   ██░▓██▒  ▐▌██▒
░▒▓███▀▒░██▓ ▒██▒ ▓█   ▓██▒░▓█  ▀█▓░██░▒██░   ▓██░░▒████▓ ░██▓ ▒██▒ ▓█   ▓██▒░▒▓███▀▒░ ████▓▒░▒██░   ▓██░
 ░▒   ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░▒▓███▀▒░▓  ░ ▒░   ▒ ▒  ▒▒▓  ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░ ░▒   ▒ ░ ▒░▒░▒░ ░ ▒░   ▒ ▒ 
  ░   ░   ░▒ ░ ▒░  ▒   ▒▒ ░▒░▒   ░  ▒ ░░ ░░   ░ ▒░ ░ ▒  ▒   ░▒ ░ ▒░  ▒   ▒▒ ░  ░   ░   ░ ▒ ▒░ ░ ░░   ░ ▒░
░ ░   ░   ░░   ░   ░   ▒    ░    ░  ▒ ░   ░   ░ ░  ░ ░  ░   ░░   ░   ░   ▒   ░ ░   ░ ░ ░ ░ ▒     ░   ░ ░ 
      ░    ░           ░  ░ ░       ░           ░    ░       ░           ░  ░      ░     ░ ░           ░ 
                                 ░                 ░                                                     
\033[0m
"""

# Print the ASCII art
print(ascii_art)

# Read the token from token.txt
token_file_path = os.path.join(os.getcwd(), 'token.txt')
if not os.path.exists(token_file_path):
    print(f"Token file not found at {token_file_path}")
    exit()

with open(token_file_path, 'r') as file:
    TOKEN = file.read().strip()

GATEWAY_URL = "wss://gateway.discord.gg/?v=9&encoding=json"

headers = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}

# Check if token is valid
def check_token():
    url = "https://discord.com/api/v9/users/@me"
    response = requests.get(url, headers=headers)
    if response.status_code in [200, 202]:
        return response.json()
    else:
        print("Invalid token")
        exit()

# Print user info to verify authentication
user_info = check_token()
print(f"Logged in as {user_info['username']}#{user_info['discriminator']}")

# Send a message
async def send_message(channel_id, content):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    data = {
        "content": content
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            return await response.json()

# Delete a message
async def delete_message(channel_id, message_id):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}"
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=headers) as response:
            return response.status

# Load commands from the commands folder
def load_command(command_name):
    try:
        module = importlib.import_module(f'commands.{command_name}')
        return module.execute
    except ModuleNotFoundError:
        print(f"Command {command_name} not found")
        return None

# Handle a single event
async def handle_event(event, websocket):
    if event["t"] == "MESSAGE_CREATE":
        content = event["d"]["content"]
        if content.startswith(';'):
            command_name = content[1:].split()[0]
            command_function = load_command(command_name)
            if command_function:
                print(f"Executed command: {command_name}")
                await delete_message(event["d"]["channel_id"], event["d"]["id"])
                await command_function(event["d"], send_message)

# Handle incoming events
async def handle_events():
    async with websockets.connect(GATEWAY_URL) as websocket:
        hello = await websocket.recv()
        heartbeat_interval = json.loads(hello)["d"]["heartbeat_interval"] / 1000

        # Identify payload
        identify_payload = {
            "op": 2,
            "d": {
                "token": TOKEN,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc"
                }
            }
        }

        await websocket.send(json.dumps(identify_payload))

        async def send_heartbeat():
            while True:
                await websocket.send(json.dumps({"op": 1, "d": None}))
                await asyncio.sleep(heartbeat_interval)

        asyncio.create_task(send_heartbeat())

        while True:
            message = await websocket.recv()
            event = json.loads(message)

            asyncio.create_task(handle_event(event, websocket))

asyncio.run(handle_events())
