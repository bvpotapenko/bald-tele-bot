from unittest import TestCase
import asyncio
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, Message, Chat, User
from telegram.ext import CallbackContext
from bot import start, help_command, echo
from typing import Any
import datetime

class TestCallbackContext(CallbackContext):
    @property
    def bot(self) -> Any:
        return self._bot
    
    @bot.setter
    def bot(self, value: Any) -> None:
        self._bot = value

class TestBot(TestCase):
    def setUp(self):
        self.from_user = User(id=123456789, first_name="John", last_name="Doe", is_bot=False)
        self.chat = Chat(id=123456789, type="private")
        self.context = TestCallbackContext(None)
        self.context.bot = AsyncMock() # Add this line to mock the bot
        self.message = MagicMock(spec=Message, reply_html=self._mock_reply_html)

    def _create_message(self, text):
        message = Message(
            message_id=1,
            from_user=self.from_user,
            chat=self.chat,
            date=None,
            text=text
        )
        return Update(update_id=1, message=message)
    
    def _create_update(self, text: str) -> Update:
        message = Message(
            message_id=1,
            from_user=self.from_user,
            date=datetime.datetime.now(),
            chat=self.chat,
            text=text,
        )
        return Update(update_id=1, message=message)
    
    def _mock_reply_html(self, *args, **kwargs):
        pass


    def test_start(self):
        update = self._create_update("/start")

        # Create a simple async function to run the test
        async def run_test():
            await start(update, self.context)

            expected_text = f"At your service, sir {self.from_user.mention_html()}!"
            self.context.bot.send_message_html.assert_called_once_with(
                chat_id=self.chat.id, text=expected_text, parse_mode="HTML"
            )

        # Run the async test function
        asyncio.run(run_test())

    def test_echo(self):
        update = self._create_update("test")
        echo(update, self.context)

    def test_help_command(self):
        update = self._create_update("/help")
        help_command(update, self.context)