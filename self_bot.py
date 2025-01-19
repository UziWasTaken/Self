import requests
import json
import asyncio
import websockets
import importlib
import os
import aiohttp
import ctypes
import logging
from typing import Optional, Dict, Callable
from aiohttp import ClientSession, ClientTimeout
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# Constants
API_VERSION = "v9"
API_BASE = f"https://discord.com/api/{API_VERSION}"
GATEWAY_URL = f"wss://gateway.discord.gg/?v={API_VERSION}&encoding=json"
TIMEOUT = ClientTimeout(total=30)
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1

class DiscordSelfBot:
    def __init__(self):
        self.token = self._load_token()
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
        self.session: Optional[ClientSession] = None
        self.heartbeat_interval: float = 0
        self.command_cache: Dict[str, Callable] = {}
        self._running = True

    def _load_token(self) -> str:
        token_file_path = os.path.join(os.getcwd(), 'token.txt')
        try:
            with open(token_file_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            logger.error(f"Token file not found at {token_file_path}")
            raise SystemExit(1)

    @asynccontextmanager
    async def get_session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=TIMEOUT)
        try:
            yield self.session
        except Exception as e:
            logger.error(f"Session error: {e}")
            await self.session.close()
            self.session = None
            raise

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        for attempt in range(RETRY_ATTEMPTS):
            try:
                async with self.get_session() as session:
                    async with session.request(
                        method, 
                        f"{API_BASE}{endpoint}", 
                        headers=self.headers, 
                        **kwargs
                    ) as response:
                        if response.status == 429:
                            retry_after = float(response.headers.get('Retry-After', RETRY_DELAY))
                            await asyncio.sleep(retry_after)
                            continue
                        response.raise_for_status()
                        return await response.json() if method != "DELETE" else {}
            except Exception as e:
                if attempt == RETRY_ATTEMPTS - 1:
                    logger.error(f"Request failed after {RETRY_ATTEMPTS} attempts: {e}")
                    raise
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
        return {}

    async def check_token(self) -> dict:
        return await self._make_request("GET", "/users/@me")

    async def send_message(self, channel_id: str, content: str) -> dict:
        return await self._make_request(
            "POST",
            f"/channels/{channel_id}/messages",
            json={"content": content}
        )

    async def delete_message(self, channel_id: str, message_id: str) -> None:
        await self._make_request(
            "DELETE",
            f"/channels/{channel_id}/messages/{message_id}"
        )

    def load_command(self, command_name: str) -> Optional[Callable]:
        if command_name in self.command_cache:
            return self.command_cache[command_name]
        
        try:
            module = importlib.import_module(f'commands.{command_name}')
            self.command_cache[command_name] = module.execute
            return module.execute
        except ModuleNotFoundError:
            logger.warning(f"Command {command_name} not found")
            return None

    async def handle_event(self, event: dict) -> None:
        if event["t"] == "MESSAGE_CREATE":
            content = event["d"]["content"]
            if content.startswith(';'):
                command_name = content[1:].split()[0]
                command_function = self.load_command(command_name)
                if command_function:
                    logger.info(f"Executing command: {command_name}")
                    try:
                        await self.delete_message(event["d"]["channel_id"], event["d"]["id"])
                        await command_function(event["d"], self.send_message)
                    except Exception as e:
                        logger.error(f"Error executing command {command_name}: {e}")

    async def heartbeat_loop(self, websocket):
        while self._running:
            try:
                await websocket.send(json.dumps({"op": 1, "d": None}))
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                break

    async def start(self):
        try:
            user_info = await self.check_token()
            logger.info(f"Logged in as {user_info['username']}#{user_info.get('discriminator', '')}")

            while self._running:
                try:
                    async with websockets.connect(GATEWAY_URL) as websocket:
                        hello = await websocket.recv()
                        self.heartbeat_interval = json.loads(hello)["d"]["heartbeat_interval"] / 1000

                        await websocket.send(json.dumps({
                            "op": 2,
                            "d": {
                                "token": self.token,
                                "properties": {
                                    "$os": "windows",
                                    "$browser": "chrome",
                                    "$device": "pc"
                                }
                            }
                        }))

                        heartbeat_task = asyncio.create_task(self.heartbeat_loop(websocket))

                        try:
                            while self._running:
                                message = await websocket.recv()
                                event = json.loads(message)
                                asyncio.create_task(self.handle_event(event))
                        except Exception as e:
                            logger.error(f"WebSocket error: {e}")
                        finally:
                            heartbeat_task.cancel()
                except Exception as e:
                    logger.error(f"Connection error: {e}")
                    await asyncio.sleep(5)  # Wait before reconnecting
        finally:
            self._running = False
            if self.session and not self.session.closed:
                await self.session.close()

def main():
    bot = DiscordSelfBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
