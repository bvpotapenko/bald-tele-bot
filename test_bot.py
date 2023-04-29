import os
import asyncio
import unittest
from unittest.mock import patch
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes
from bot import start, help_command, echo

# Create a test class for our bot
class TestBot(unittest.TestCase):
    
    def setUp(self):
        self.update = Update(update_id=1)
        self.context = ContextTypes.DEFAULT_TYPE()
        self.update.message = Message(
            message_id=1,
            from_user=User(id=1, first_name="Test", is_bot=False),
            chat=Chat(id=1, type="private"),
            text="",
        )

    @patch("telegram.Message.reply_html")
    def test_start(self, mock_reply_html):
        self.update.message.text = "/start"
        asyncio.run(start(self.update, self.context))
        mock_reply_html.assert_called()

    @patch("telegram.Message.reply_text")
    def test_help_command(self, mock_reply_text):
        self.update.message.text = "/help"
        asyncio.run(help_command(self.update, self.context))
        mock_reply_text.assert_called()

    @patch("telegram.Message.reply_text")
    def test_echo(self, mock_reply_text):
        self.update.message.text = "test"
        asyncio.run(echo(self.update, self.context))
        mock_reply_text.assert_called_with("test")

if __name__ == "__main__":
    unittest.main()