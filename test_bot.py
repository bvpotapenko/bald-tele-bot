import unittest
from unittest.mock import MagicMock
from aiohttp import web
from aiohttp.test_utils import TestServer, TestClient, unittest_run_loop
import bot


class TestBot(unittest.TestCase):

    def setUp(self):
        self.app = web.Application()
        self.app.router.add_post("/", bot.webhook_handler)
        self.app.on_startup.append(bot.on_startup)
        self.app.on_cleanup.append(bot.on_cleanup)
        self.server = TestServer(self.app)
        self.client = TestClient(self.server)

    async def test_webhook_handler(self):
        update = {
            'message': {
                'chat': {'id': 12345},
                'text': '/start',
                'from': {'first_name': 'John'}
            }
        }

        bot.handle_update = MagicMock(return_value=None)

        async with self.client.post("/", json=update) as resp:
            self.assertEqual(resp.status, 200)
            result = await resp.json()
            self.assertEqual(result, {'status': 'ok'})

        bot.handle_update.assert_called_once_with(update, self.app['session'])

    async def test_handle_update(self):
        update = {
            'message': {
                'chat': {'id': 12345},
                'text': '/start',
                'from': {'first_name': 'John'}
            }
        }
        session = MagicMock()

        bot.send_message = MagicMock(return_value=None)
        await bot.handle_update(update, session)
        bot.send_message.assert_called_once_with(12345, 'At your service, sir <b>John</b>!', session)


if __name__ == '__main__':
    unittest.main()