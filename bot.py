import logging
import sys
import os
import asyncio
import secrets
from dotenv import load_dotenv
from typing import Any, Dict
from aiohttp import ClientSession, web
from html import escape

# Enable logging
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt='%H:%M:%S', 
                    level=logging.DEBUG,
                    handlers=[logging.FileHandler('./logs/runtime.log'), 
                            stream_handler]
)
logger = logging.getLogger(__name__)
logging.info('Logs are activated for Vercel')
logging.error('Test logging an error (no error, chill)')

load_dotenv()

API_KEY = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT"))
DOMAIN = os.environ.get("DOMAIN")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{API_KEY}"
WEBHOOK_URL = f"https://{DOMAIN}:{PORT}"


async def set_webhook(session: ClientSession) -> None:
    await delete_webhook(session)
    payload = {
        'url': WEBHOOK_URL,
    }
    async with session.post(f"{TELEGRAM_API_URL}/setWebhook", json=payload) as resp:
        result = await resp.json()
        if not result['ok']:
            logging.error(f"Failed to set webhook: {result['description']}")


async def send_message(chat_id: int, text: str, session: ClientSession) -> None:
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
    }
    async with session.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload) as resp:
        await resp.json()


async def handle_update(update: Dict[str, Any], session: ClientSession) -> None:
    if 'message' in update:
        message = update['message']
        text = message['text']
        chat_id = message['chat']['id']

        if text == '/start':
            user_name = escape(message['from']['first_name'])
            await send_message(chat_id, f"At your service, sir <b>{user_name}</b>!", session)
        else:
            await send_message(chat_id, text, session)


async def webhook_handler(request) -> Any:
    update = await request.json()
    await handle_update(update, request.app['session'])
    return {'status': 'ok'}


async def on_startup(app) -> None:
    app['session'] = session = ClientSession()
    await set_webhook(session)


async def on_cleanup(app) -> None:
    await app['session'].close()


async def delete_webhook(session: ClientSession) -> None:
    async with session.post(f"{TELEGRAM_API_URL}/deleteWebhook") as resp:
        result = await resp.json()
        if not result['ok']:
            logging.error(f"Failed to delete webhook: {result['description']}")
            

async def main() -> None:
    app = web.Application()
    app.router.add_post("/", webhook_handler)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, DOMAIN, PORT)
    await site.start()


if __name__ == "__main__":
    logging.info('STARTING MAIN()')
    asyncio.get_event_loop().run_until_complete(main())

