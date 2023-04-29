import logging

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
from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

# /start comand handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Send a message to the user when the /start command is issued
    user = update.effective_user
    await update.message.reply_html( 
        rf"At your service, sir {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
        )
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def main() -> None:
    # Get the Telegram bot API key from the environment variable
    api_key = os.environ.get("TELEGRAM_BOT_TOKEN")
    port = int(os.environ.get("PORT"))
    # ssl_key = os.environ.get('private.key')
    # ssl_cert = os.environ.get('cert.pem')
    domain = os.environ.get("DOMAI")

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(api_key).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Set up the webhook
    await application.set_webhook(url=f"https://{domain}:{port}/{api_key}")

    # Start the webhook server
    await application.start_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=api_key,
        webhook_url=f"https://{domain}:{port}/{api_key}",
    )

    # Run the bot until you press Ctrl-C
    await application.idle()

if __name__ == "__main__":
    asyncio.run(main())