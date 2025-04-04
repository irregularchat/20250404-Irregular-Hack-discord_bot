import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import discord
import asyncio

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from discord_notifier import DiscordNotifier

class TestDiscordNotifier(unittest.TestCase):
    
    def setUp(self):
        # Create a patch for config values
        self.config_patcher = patch('discord_notifier.config', 
                                  DISCORD_TOKEN='test_token',
                                  DISCORD_CHANNEL_ID=123456789)
        self.mock_config = self.config_patcher.start()
        
    def tearDown(self):
        self.config_patcher.stop()
    
    @patch('discord_notifier.commands.Bot.get_channel')
    @patch('discord_notifier.commands.Bot.__init__')
    def test_init(self, mock_bot_init, mock_get_channel):
        """Test initialization of DiscordNotifier"""
        # Configure mocks
        mock_bot_init.return_value = None
        
        # Create instance
        notifier = DiscordNotifier()
        
        # Verify Bot was initialized with expected parameters
        mock_bot_init.assert_called_once()
        # Check that intents were configured
        call_args = mock_bot_init.call_args[1]
        self.assertEqual(call_args['command_prefix'], '!')
        self.assertTrue(isinstance(call_args['intents'], discord.Intents))
        
        # Verify channel ID was set from config
        self.assertEqual(notifier.notification_channel_id, 123456789)
    
    @patch('discord_notifier.commands.Bot.get_channel')
    @patch('discord_notifier.commands.Bot.__init__')
    def test_on_ready(self, mock_bot_init, mock_get_channel):
        """Test on_ready event handler"""
        # Configure mocks
        mock_bot_init.return_value = None
        mock_channel = MagicMock()
        mock_channel.name = "test-channel"
        mock_get_channel.return_value = mock_channel
        
        # Create event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Create instance and setup attributes
            notifier = DiscordNotifier()
            
            # Use __dict__ to directly set attributes instead of using property setters
            notifier.__dict__['user'] = MagicMock(name="TestBot", id="12345")
            notifier.__dict__['guilds'] = ["guild1", "guild2"]
            
            # Run on_ready method
            loop.run_until_complete(notifier.on_ready())
            
            # Verify channel was fetched
            mock_get_channel.assert_called_once_with(123456789)
        finally:
            # Clean up the event loop
            loop.close()
    
    @patch('discord_notifier.commands.Bot.get_channel')
    @patch('discord_notifier.commands.Bot.__init__')
    def test_on_ready_no_channel(self, mock_bot_init, mock_get_channel):
        """Test on_ready when channel is not found"""
        # Configure mocks
        mock_bot_init.return_value = None
        mock_get_channel.return_value = None
        
        # Create event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Create instance and setup attributes
            notifier = DiscordNotifier()
            
            # Use __dict__ to directly set attributes instead of using property setters
            notifier.__dict__['user'] = MagicMock(name="TestBot", id="12345")
            notifier.__dict__['guilds'] = ["guild1"]
            
            # Run on_ready method
            loop.run_until_complete(notifier.on_ready())
            
            # Verify channel was attempted to be fetched
            mock_get_channel.assert_called_once_with(123456789)
        finally:
            # Clean up the event loop
            loop.close()
    
    @patch('discord_notifier.commands.Bot.get_channel')
    @patch('discord_notifier.commands.Bot.__init__')
    def test_send_email_notification_success(self, mock_bot_init, mock_get_channel):
        """Test successful sending of email notification"""
        # Configure mocks
        mock_bot_init.return_value = None
        mock_channel = AsyncMock()
        mock_get_channel.return_value = mock_channel
        
        # Create event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Prepare test data
            email_data = {
                'subject': 'Test Email',
                'from': 'sender@example.com',
                'date': 'Fri, 10 Mar 2023 12:00:00 +0000',
                'body': 'This is a test email body.',
                'summary': 'This is an AI-generated summary.'
            }
            
            # Create instance
            notifier = DiscordNotifier()
            
            # Run send_email_notification method
            result = loop.run_until_complete(notifier.send_email_notification(email_data))
            
            # Verify channel was fetched
            mock_get_channel.assert_called_once_with(123456789)
            
            # Verify message was sent
            mock_channel.send.assert_called_once()
            self.assertTrue(result)
            
            # Verify embed contents
            call_args = mock_channel.send.call_args[1]
            embed = call_args['embed']
            self.assertEqual(embed.title, 'Test Email')
            self.assertEqual(embed.fields[0].name, 'From')
            self.assertEqual(embed.fields[0].value, 'sender@example.com')
            self.assertEqual(embed.fields[1].name, 'Date')
            self.assertEqual(embed.fields[1].value, 'Fri, 10 Mar 2023 12:00:00 +0000')
            self.assertEqual(embed.fields[2].name, 'Summary')
            self.assertEqual(embed.fields[2].value, 'This is an AI-generated summary.')
        finally:
            # Clean up the event loop
            loop.close()
    
    @patch('discord_notifier.commands.Bot.get_channel')
    @patch('discord_notifier.commands.Bot.__init__')
    def test_send_email_notification_no_channel(self, mock_bot_init, mock_get_channel):
        """Test notification when channel is not found"""
        # Configure mocks
        mock_bot_init.return_value = None
        mock_get_channel.return_value = None
        
        # Create event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Prepare test data
            email_data = {
                'subject': 'Test Email',
                'from': 'sender@example.com',
                'body': 'This is a test email body.'
            }
            
            # Create instance
            notifier = DiscordNotifier()
            
            # Run send_email_notification method
            result = loop.run_until_complete(notifier.send_email_notification(email_data))
            
            # Verify channel was attempted to be fetched
            mock_get_channel.assert_called_once_with(123456789)
            
            # Verify no message was sent and result is False
            self.assertFalse(result)
        finally:
            # Clean up the event loop
            loop.close()
    
    @patch('discord_notifier.commands.Bot.get_channel')
    @patch('discord_notifier.commands.Bot.__init__')
    def test_send_email_notification_long_body(self, mock_bot_init, mock_get_channel):
        """Test notification with a long email body that needs truncation"""
        # Configure mocks
        mock_bot_init.return_value = None
        mock_channel = AsyncMock()
        mock_get_channel.return_value = mock_channel
        
        # Create event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Prepare test data with a long body
            long_body = "A" * 2000
            email_data = {
                'subject': 'Long Email',
                'from': 'sender@example.com',
                'date': 'Fri, 10 Mar 2023 12:00:00 +0000',
                'body': long_body,
                'summary': 'Summary of long email.'
            }
            
            # Create instance
            notifier = DiscordNotifier()
            
            # Run send_email_notification method
            result = loop.run_until_complete(notifier.send_email_notification(email_data))
            
            # Verify channel was fetched
            mock_get_channel.assert_called_once_with(123456789)
            
            # Verify message was sent
            mock_channel.send.assert_called_once()
            self.assertTrue(result)
            
            # Verify embed contents and truncation
            call_args = mock_channel.send.call_args[1]
            embed = call_args['embed']
            content_field = embed.fields[3]  # Content Preview field
            self.assertEqual(content_field.name, 'Content Preview')
            self.assertTrue(len(content_field.value) < 2000)
            self.assertTrue(content_field.value.endswith('...'))
        finally:
            # Clean up the event loop
            loop.close()
    
    @patch('discord_notifier.commands.Bot.get_channel')
    @patch('discord_notifier.commands.Bot.__init__')
    def test_send_email_notification_exception(self, mock_bot_init, mock_get_channel):
        """Test handling of exceptions during notification sending"""
        # Configure mocks
        mock_bot_init.return_value = None
        mock_channel = AsyncMock()
        mock_channel.send.side_effect = Exception("Discord API Error")
        mock_get_channel.return_value = mock_channel
        
        # Create event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Prepare test data
            email_data = {
                'subject': 'Test Email',
                'from': 'sender@example.com',
                'body': 'This is a test email body.'
            }
            
            # Create instance
            notifier = DiscordNotifier()
            
            # Run send_email_notification method
            result = loop.run_until_complete(notifier.send_email_notification(email_data))
            
            # Verify channel was fetched
            mock_get_channel.assert_called_once_with(123456789)
            
            # Verify message was attempted to be sent but failed
            mock_channel.send.assert_called_once()
            self.assertFalse(result)
        finally:
            # Clean up the event loop
            loop.close()

if __name__ == '__main__':
    unittest.main() 