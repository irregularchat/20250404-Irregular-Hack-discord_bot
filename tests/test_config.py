import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import config


# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock the entire dotenv module before importing config
sys.modules["dotenv"] = MagicMock()
sys.modules["dotenv"].load_dotenv = MagicMock(return_value=True)


class TestConfig(unittest.TestCase):

    def setUp(self):
        # Reset the mock before each test
        sys.modules["dotenv"].load_dotenv.reset_mock()

        # Clear config from sys.modules to force fresh import in each test
        if "config" in sys.modules:
            del sys.modules["config"]

    def tearDown(self):
        # Clean up any config module imports
        if "config" in sys.modules:
            del sys.modules["config"]

    @patch("os.getenv")
    def test_config_loading(self, mock_getenv):
        """Test configuration loading from environment variables"""
        # Configure getenv mock to return specific values
        mock_getenv.side_effect = lambda key, default=None: {
            "imap_server": "test.server.com",
            "imap_user": "test@example.com",
            "imap_password": "testpassword",
            "imap_port": "993",
            "openai_api_key": "test_openai_key",
            "discord_token": "test_discord_token",
            "discord_channel_id": "123456789",
            "whitelisted_email_addresses": "test1@example.com,test2@example.com",
        }.get(key, default)

        # Import config after mocking
        import config

        # Verify load_dotenv was called
        sys.modules["dotenv"].load_dotenv.assert_called_once()

        # Verify configuration values were set correctly
        self.assertEqual(config.IMAP_SERVER, "test.server.com")
        self.assertEqual(config.IMAP_USER, "test@example.com")
        self.assertEqual(config.IMAP_PASSWORD, "testpassword")
        self.assertEqual(config.IMAP_PORT, 993)
        self.assertEqual(config.OPENAI_API_KEY, "test_openai_key")
        self.assertEqual(config.DISCORD_TOKEN, "test_discord_token")
        self.assertEqual(config.DISCORD_CHANNEL_ID, 123456789)
        self.assertEqual(
            config.WHITELISTED_EMAIL_ADDRESSES,
            ["test1@example.com", "test2@example.com"],
        )

    @patch("os.getenv")
    def test_config_with_missing_values(self, mock_getenv):
        """Test configuration with missing environment variables"""
        # Configure getenv mock to return None for some values
        mock_getenv.side_effect = lambda key, default=None: {
            "imap_server": "test.server.com",
            "imap_user": "test@example.com",
            "imap_password": "testpassword",
            "imap_port": "993",
            # Missing OpenAI key
            "discord_token": "test_discord_token",
            # Missing Discord channel ID
            # Missing whitelisted emails
        }.get(key, default)

        # Import config after mocking
        import config

        # Verify values that should be present
        self.assertEqual(config.IMAP_SERVER, "test.server.com")
        self.assertEqual(config.IMAP_USER, "test@example.com")
        self.assertEqual(config.IMAP_PASSWORD, "testpassword")
        self.assertEqual(config.IMAP_PORT, 993)
        self.assertEqual(config.DISCORD_TOKEN, "test_discord_token")

        # Verify missing values have appropriate defaults
        self.assertIsNone(config.OPENAI_API_KEY)
        self.assertIsNone(config.DISCORD_CHANNEL_ID)
        self.assertEqual(config.WHITELISTED_EMAIL_ADDRESSES, [])

    @patch("os.getenv")
    def test_default_imap_port(self, mock_getenv):
        """Test default IMAP port when not specified"""
        # Configure getenv to return None for port
        mock_getenv.side_effect = lambda key, default=None: {
            "imap_server": "test.server.com",
            "imap_user": "test@example.com",
            "imap_password": "testpassword",
            # Missing imap_port
            "openai_api_key": "test_openai_key",
            "discord_token": "test_discord_token",
            "discord_channel_id": "123456789",
        }.get(key, default)

        # Verify the default port was used
        self.assertEqual(config.IMAP_PORT, 993)

    @patch("os.getenv")
    def test_whitelist_parsing(self, mock_getenv):
        """Test parsing of whitelisted email addresses"""
        test_cases = [
            # Single email address
            "test@example.com",
            # Multiple addresses with spaces
            "test1@example.com, test2@example.com",
            # Empty string
            "",
            # None (missing)
            None,
        ]

        expected_results = [
            ["test@example.com"],
            ["test1@example.com", "test2@example.com"],  # Spaces should be trimmed
            [],
            [],
        ]

        for i, test_value in enumerate(test_cases):
            # Reset the mock and sys.modules for each iteration
            sys.modules["dotenv"].load_dotenv.reset_mock()
            if "config" in sys.modules:
                del sys.modules["config"]

            # Configure mock to return our test value for whitelisted_email_addresses
            mock_getenv.side_effect = lambda key, default=None: (
                test_value if key == "whitelisted_email_addresses" else default
            )

            # Import config after mocking
            import config

            # Verify whitelist was parsed correctly
            self.assertEqual(config.WHITELISTED_EMAIL_ADDRESSES, expected_results[i])


if __name__ == "__main__":
    unittest.main()
