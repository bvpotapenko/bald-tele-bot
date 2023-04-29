import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

# Import the start function from bot.py
from bot import start

# Create a test class for our bot
class TestBot(unittest.TestCase):
    # Test the start command
    def test_start_command(self):
        # Create a mock update and context
        update = MagicMock()
        context = MagicMock()

        # Redirect the standard output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            # Call the start function with the mock update and context
            start(update, context)

            # Check if the expected message is sent to the user
            self.assertIn("At your service, sir.", update.message.reply_text.call_args.args)

# Run the tests
if __name__ == "__main__":
    unittest.main()