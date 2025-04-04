import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import asyncio

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot import EmailMonitorBot, main

class TestEmailMonitorBot(unittest.TestCase):
    
    def setUp(self):
        # Mock out real connections to external services
        self.patch_env = patch.dict('os.environ', {
            'imap_server': 'test_server',
            'imap_user': 'test_user',
            'imap_password': 'test_password',
            'imap_port': '993',
            'imap_ssl': 'true',
            'openai_api_key': 'test_api_key',
            'discord_token': 'test_token',
            'discord_channel_id': '123456789',
            'whitelisted_email_addresses': 'test@example.com',
        })
        self.patch_env.start()

        # Create patches for dependencies
        self.email_handler_patcher = patch('bot.EmailHandler')
        self.discord_notifier_patcher = patch('bot.DiscordNotifier')
        self.summarize_email_patcher = patch('bot.summarize_email')
        self.config_patcher = patch('bot.config', 
                                  CHECK_INTERVAL=10,
                                  IMAP_SERVER='test_server',
                                  IMAP_USER='test_user',
                                  IMAP_PASSWORD='test_password',
                                  IMAP_SSL=True,
                                  OPENAI_API_KEY='test_api_key',
                                  DISCORD_TOKEN='test_token',
                                  DISCORD_CHANNEL_ID=123456789,
                                  WHITELISTED_EMAIL_ADDRESSES=['test@example.com'])
        
        # Start the patches
        self.mock_email_handler = self.email_handler_patcher.start()
        self.mock_discord_notifier = self.discord_notifier_patcher.start()
        self.mock_summarize_email = self.summarize_email_patcher.start()
        self.mock_config = self.config_patcher.start()
        
        # Configure mocks
        self.mock_handler_instance = MagicMock()
        self.mock_notifier_instance = MagicMock()
        self.mock_email_handler.return_value = self.mock_handler_instance
        self.mock_discord_notifier.return_value = self.mock_notifier_instance
        
        # Setup the discord notifier mock for async methods
        self.mock_notifier_instance.send_email_notification = AsyncMock(return_value=True)
        self.mock_notifier_instance.start = AsyncMock()
        self.mock_notifier_instance.close = AsyncMock()
        
        # Configure email handler mock
        self.mock_handler_instance.connect = MagicMock(return_value=True)
        self.mock_handler_instance.disconnect = MagicMock()
        self.mock_handler_instance.get_new_emails = MagicMock(return_value=[])
        
        # Setup event loop for async testing
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    def tearDown(self):
        # Stop the patches
        self.email_handler_patcher.stop()
        self.discord_notifier_patcher.stop()
        self.summarize_email_patcher.stop()
        self.config_patcher.stop()
        self.patch_env.stop()
        
        # Close the event loop
        self.loop.close()
    
    def test_init(self):
        """Test initialization of EmailMonitorBot"""
        # Create bot instance
        bot = EmailMonitorBot()
        
        # Verify initialization of components
        self.mock_email_handler.assert_called_once()
        self.mock_discord_notifier.assert_called_once()
        self.assertEqual(bot.email_handler, self.mock_handler_instance)
        self.assertEqual(bot.discord_bot, self.mock_notifier_instance)
        self.assertFalse(bot.running)
    
    @patch('bot.asyncio.sleep')
    def test_check_emails_no_new_emails(self, mock_sleep):
        """Test check_emails method when no new emails are found"""
        # Configure email handler to return no emails
        self.mock_handler_instance.get_new_emails.return_value = []
        
        # Create bot instance
        bot = EmailMonitorBot()
        
        # Run check_emails method
        self.loop.run_until_complete(bot.check_emails())
        
        # Verify behavior
        self.mock_handler_instance.get_new_emails.assert_called_once()
        self.mock_summarize_email.assert_not_called()
        self.mock_notifier_instance.send_email_notification.assert_not_called()
        mock_sleep.assert_not_called()
    
    @patch('bot.asyncio.sleep')
    def test_check_emails_with_new_emails(self, mock_sleep):
        """Test check_emails method when new emails are found"""
        # Mock email data and summarization
        email1 = {'subject': 'Email 1', 'body': 'Content 1'}
        email2 = {'subject': 'Email 2', 'body': 'Content 2'}
        
        self.mock_handler_instance.get_new_emails.return_value = [email1, email2]
        self.mock_summarize_email.side_effect = lambda email: {**email, 'summary': f"Summary of {email['subject']}"}
        
        # Make send_email_notification a coroutine mock
        self.mock_notifier_instance.send_email_notification = AsyncMock()
        
        # Create bot instance
        bot = EmailMonitorBot()
        
        # Run check_emails method
        self.loop.run_until_complete(bot.check_emails())
        
        # Verify behavior
        self.mock_handler_instance.get_new_emails.assert_called_once()
        self.assertEqual(self.mock_summarize_email.call_count, 2)
        self.mock_summarize_email.assert_any_call(email1)
        self.mock_summarize_email.assert_any_call(email2)
        self.assertEqual(self.mock_notifier_instance.send_email_notification.call_count, 2)
        mock_sleep.assert_called_with(1)  # Should sleep 1 second between emails
    
    @patch('bot.asyncio.sleep')
    def test_start_monitoring_connection_failure(self, mock_sleep):
        """Test start_monitoring when email connection fails"""
        # Configure email handler to fail connection
        self.mock_handler_instance.connect.return_value = False
        
        # Create bot instance
        bot = EmailMonitorBot()
        
        # Run start_monitoring method
        self.loop.run_until_complete(bot.start_monitoring())
        
        # Verify behavior
        self.mock_handler_instance.connect.assert_called_once()
        self.mock_handler_instance.get_new_emails.assert_not_called()
        mock_sleep.assert_not_called()
    
    @patch('bot.asyncio.sleep')
    def test_start_monitoring_loop(self, mock_sleep):
        """Test the monitoring loop in start_monitoring"""
        # Configure email handler
        self.mock_handler_instance.connect.return_value = True
        
        # Create a side effect that stops the loop after one iteration
        def side_effect(*args, **kwargs):
            bot.running = False
            return []
            
        self.mock_handler_instance.get_new_emails.side_effect = side_effect
        
        # Create bot instance
        bot = EmailMonitorBot()
        bot.running = True
        
        # Run start_monitoring method
        self.loop.run_until_complete(bot.start_monitoring())
        
        # Verify behavior
        self.mock_handler_instance.connect.assert_called_once()
        self.mock_handler_instance.get_new_emails.assert_called_once()
        mock_sleep.assert_called_once_with(10)  # Should sleep CHECK_INTERVAL seconds
    
    @patch('bot.asyncio.sleep')
    def test_start_monitoring_exception_handling(self, mock_sleep):
        """Test exception handling in the monitoring loop"""
        # Configure email handler
        self.mock_handler_instance.connect.return_value = True
        
        # Create an exception and a side effect that stops the loop after exception handling
        call_count = 0
        
        def mock_get_emails_with_exception(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                # First call raises an exception
                raise Exception("Test error")
            else:
                # Second call stops the loop
                bot.running = False
                return []
        
        # Set the side effect on the mock
        self.mock_handler_instance.get_new_emails.side_effect = mock_get_emails_with_exception
        
        # Create bot instance
        bot = EmailMonitorBot()
        bot.running = True
        
        # Run start_monitoring method
        self.loop.run_until_complete(bot.start_monitoring())
        
        # Verify behavior
        self.mock_handler_instance.connect.assert_called_once()
        self.assertEqual(self.mock_handler_instance.get_new_emails.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 2)
    
    def test_stop_monitoring(self):
        """Test stop_monitoring method"""
        # Create bot instance and start it
        bot = EmailMonitorBot()
        bot.running = True
        
        # Stop monitoring
        bot.stop_monitoring()
        
        # Verify behavior
        self.assertFalse(bot.running)
        self.mock_handler_instance.disconnect.assert_called_once()
    
    @patch('bot.asyncio.create_task')
    def test_run(self, mock_create_task):
        """Test run method"""
        # Configure mocks
        mock_task = AsyncMock()
        mock_create_task.return_value = mock_task
        self.mock_notifier_instance.start = AsyncMock()
        self.mock_notifier_instance.close = AsyncMock()
        
        # Create bot instance
        bot = EmailMonitorBot()
        
        # Run the bot
        self.loop.run_until_complete(bot.run())
        
        # Verify behavior
        mock_create_task.assert_called_once()
        self.mock_notifier_instance.start.assert_called_once_with('test_token')
        self.mock_notifier_instance.close.assert_called_once()
    
    @patch('bot.asyncio.create_task')
    def test_run_with_exception(self, mock_create_task):
        """Test run method when an exception occurs"""
        # Configure mocks
        mock_task = AsyncMock()
        mock_create_task.return_value = mock_task
        self.mock_notifier_instance.start = AsyncMock(side_effect=Exception("Discord error"))
        self.mock_notifier_instance.close = AsyncMock()
        
        # Create bot instance
        bot = EmailMonitorBot()
        
        # Run the bot
        self.loop.run_until_complete(bot.run())
        
        # Verify behavior
        mock_create_task.assert_called_once()
        self.mock_notifier_instance.start.assert_called_once_with('test_token')
        self.mock_notifier_instance.close.assert_called_once()
    
    @patch('bot.EmailMonitorBot')
    def test_main_with_valid_config(self, mock_bot_class):
        """Test main function with valid configuration"""
        # Configure mock
        mock_bot_instance = MagicMock()
        mock_bot_instance.run = AsyncMock()
        mock_bot_class.return_value = mock_bot_instance
        
        # Run main function
        self.loop.run_until_complete(main())
        
        # Verify behavior
        mock_bot_class.assert_called_once()
        mock_bot_instance.run.assert_called_once()
    
    @patch('bot.EmailMonitorBot')
    @patch('bot.config')
    def test_main_with_missing_email_config(self, mock_config, mock_bot_class):
        """Test main function with missing email configuration"""
        # Configure mock config with missing email values
        mock_config.IMAP_SERVER = None
        mock_config.IMAP_USER = 'test_user'
        mock_config.IMAP_PASSWORD = 'test_password'
        mock_config.OPENAI_API_KEY = 'test_api_key'
        mock_config.DISCORD_TOKEN = 'test_token'
        mock_config.DISCORD_CHANNEL_ID = 123456789
        
        # Run main function
        self.loop.run_until_complete(main())
        
        # Verify behavior
        mock_bot_class.assert_not_called()
    
    @patch('bot.EmailMonitorBot')
    @patch('bot.config')
    def test_main_with_missing_openai_config(self, mock_config, mock_bot_class):
        """Test main function with missing OpenAI configuration"""
        # Configure mock config with missing OpenAI API key
        mock_config.IMAP_SERVER = 'test_server'
        mock_config.IMAP_USER = 'test_user'
        mock_config.IMAP_PASSWORD = 'test_password'
        mock_config.OPENAI_API_KEY = None
        mock_config.DISCORD_TOKEN = 'test_token'
        mock_config.DISCORD_CHANNEL_ID = 123456789
        
        # Run main function
        self.loop.run_until_complete(main())
        
        # Verify behavior
        mock_bot_class.assert_not_called()
    
    @patch('bot.EmailMonitorBot')
    @patch('bot.config')
    def test_main_with_missing_discord_config(self, mock_config, mock_bot_class):
        """Test main function with missing Discord configuration"""
        # Configure mock config with missing Discord values
        mock_config.IMAP_SERVER = 'test_server'
        mock_config.IMAP_USER = 'test_user'
        mock_config.IMAP_PASSWORD = 'test_password'
        mock_config.OPENAI_API_KEY = 'test_api_key'
        mock_config.DISCORD_TOKEN = None
        mock_config.DISCORD_CHANNEL_ID = None
        
        # Run main function
        self.loop.run_until_complete(main())
        
        # Verify behavior
        mock_bot_class.assert_not_called()

if __name__ == '__main__':
    unittest.main() 