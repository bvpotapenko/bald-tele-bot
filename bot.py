import logging
import sys

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

import os
import asyncio
import secrets
from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackContext
)

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
logging.info('Logs are activated')
logging.error('Test logging an error (no error, chill)')

load_dotenv()
shutdown_event = asyncio.Event()

# /start comand handler
async def start(update: Update, context: CallbackContext) -> None:
    logger.info('Start command received')
    print('Start command received')
    # Send a message to the user when the /start command is issued
    user = update.effective_user
    await update.message.reply_html( 
        rf"At your service, sir {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
        )
    
async def help_command(update: Update, context: CallbackContext) -> None:
    logger.info('Help command received')
    print('Help command received')
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def main() -> None:
    logger.info('Started main()')
    print('Started main()')
    # Get the Telegram bot API key from the environment variable
    api_key = os.environ.get("TELEGRAM_BOT_TOKEN")
    port = int(os.environ.get("PORT"))
    # ssl_key = os.environ.get('private.key')
    # ssl_cert = os.environ.get('cert.pem')
    domain = os.environ.get("DOMAI")

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(api_key).build()
    logger.info('Application created')

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    logger.info('Three handlers are added')

    # Set up the webhook
    logger.info('Running the webhook')
    # await application.run_webhook(listen="0.0.0.0", 
    #                               port=port, 
    #                               secret_token=api_key,
    #                               webhook_url=f"https://{domain}:{port}"
    #                               )
    # logger.info('webhook is running')

    # # Run the bot until you press Ctrl-C
    # await application.idle()

    async with application:  # Calls `initialize` and `shutdown`
        await application.start()
        secret_token = secrets.token_hex(16)  # Generates a random 32-character long hexadecimal string
        await application.updater.start_webhook(listen="0.0.0.0",
                                                port=port,
                                                secret_token=secret_token,
                                                webhook_url=f"https://{domain}:{port}/{secret_token}")
        # Wait for the shutdown_event to be set
        await shutdown_event.wait()

        # Stop the other asyncio frameworks here
        await application.updater.stop()
        await application.stop()

async def stop_application():
    await application.stop()
    shutdown_event.set()

async def main_wrapper():
    main_task = asyncio.create_task(main())

    # Here, you can add other asyncio tasks or frameworks that you want to run alongside the bot

    # Run the stop_application() coroutine when you want to stop the application
    # For example, you can run it after some time, when a specific condition is met, or when you receive a signal
    # In this example, we'll stop the application after 60 seconds
    asyncio.get_event_loop().call_later(60, asyncio.ensure_future, stop_application())

    # Run the main_task until it's complete
    await main_task

if __name__ == "__main__":
    asyncio.run(main_wrapper())