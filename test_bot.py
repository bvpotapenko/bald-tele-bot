from unittest import IsolatedAsyncioTestCase
import asyncio
from unittest.mock import AsyncMock, MagicMock, ANY
from telegram import ForceReply, Update, Message, Chat, User
from telegram.ext import CallbackContext
from bot import start, help_command, echo
import datetime


class TestCallbackContext(CallbackContext):
    @property
    def bot(self) -> ANY:
        return self._bot

    @bot.setter
    def bot(self, value: ANY) -> None:
        self._bot = value


class TestBot(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.from_user = User(id=123456789, first_name="John", last_name="Doe", is_bot=False)
        self.chat = Chat(id=123456789, type="private")
        self.context = TestCallbackContext(None)
        self.context.bot = AsyncMock()
        self.message = MagicMock(spec=Message)
        self.message.from_user = self.from_user
        self.message.chat = self.chat
        self.message.reply_html = AsyncMock()
        self.message.reply_text = AsyncMock()

    def _create_update(self, text: str, message: Message) -> Update:
        # message = MagicMock(spec=Message)
        # message.from_user = self.from_user
        # message.chat = self.chat
        message.text = text
        # update = Update(update_id=1, message=message)
        return Update(update_id=1, message=message)

    async def test_start(self):
        update = self._create_update("/start", self.message)
        await start(update, self.context)

        expected_text = f"At your service, sir {self.from_user.mention_html()}!"
        self.message.reply_html.assert_called_once_with(
            expected_text,
            reply_markup=ForceReply(selective=True),
        )

    async def test_echo(self):
        update = self._create_update("test", self.message)
        await echo(update, self.context)
        self.message.reply_text.assert_called_once_with("test")

    async def test_help_command(self):
        update = self._create_update("/help", self.message)
        await help_command(update, self.context)
        self.message.reply_text.assert_called_once_with("Help!")