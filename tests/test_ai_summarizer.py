import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import importlib

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestAISummarizer(unittest.TestCase):
    
    def setUp(self):
        # Create a patch for OpenAI client class
        self.openai_patcher = patch('openai.OpenAI')
        self.mock_openai_class = self.openai_patcher.start()
        
        # Set up mock client instance
        self.mock_client = MagicMock()
        self.mock_openai_class.return_value = self.mock_client
        
        # Set up mock chat completions
        self.mock_chat_completions = MagicMock()
        self.mock_client.chat.completions = self.mock_chat_completions
        
        # Save original OpenAI import to restore it later
        self.original_openai_import = sys.modules.get('openai')
        
    def tearDown(self):
        self.openai_patcher.stop()
        
        # Restore original OpenAI import
        if self.original_openai_import:
            sys.modules['openai'] = self.original_openai_import
    
    @patch('config.OPENAI_API_KEY', 'test_api_key')
    def test_summarize_email_success(self):
        """Test successful email summarization"""
        # Import summarize_email function after mocking
        import importlib
        if 'ai_summarizer' in sys.modules:
            del sys.modules['ai_summarizer']
        from ai_summarizer import summarize_email
        
        # Prepare test data
        email_data = {
            'subject': 'Test Subject',
            'from': 'test@example.com',
            'body': 'This is a test email body with some content to summarize.',
        }
        
        # Configure mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a summarized version of the email."
        self.mock_chat_completions.create.return_value = mock_response
        
        # Call the function
        result = summarize_email(email_data)
        
        # Verify the OpenAI API was called with expected parameters
        self.mock_chat_completions.create.assert_called_once()
        call_args = self.mock_chat_completions.create.call_args[1]
        self.assertEqual(call_args['model'], 'gpt-3.5-turbo')
        self.assertEqual(len(call_args['messages']), 2)
        self.assertEqual(call_args['messages'][0]['role'], 'system')
        self.assertEqual(call_args['messages'][1]['role'], 'user')
        self.assertIn('Test Subject', call_args['messages'][1]['content'])
        self.assertIn('test@example.com', call_args['messages'][1]['content'])
        self.assertIn('This is a test email body', call_args['messages'][1]['content'])
        
        # Verify the result contains the summary
        self.assertEqual(result['summary'], "This is a summarized version of the email.")
        self.assertEqual(result['subject'], 'Test Subject')
        self.assertEqual(result['from'], 'test@example.com')
        self.assertEqual(result['body'], 'This is a test email body with some content to summarize.')
    
    @patch('config.OPENAI_API_KEY', 'test_api_key')
    def test_summarize_email_long_body(self):
        """Test summarization with a long email body that requires truncation"""
        # Import summarize_email function after mocking
        import importlib
        if 'ai_summarizer' in sys.modules:
            del sys.modules['ai_summarizer']
        from ai_summarizer import summarize_email
        
        # Prepare test data with a long body
        long_body = "A" * 5000  # Create a 5000 character body
        email_data = {
            'subject': 'Long Email',
            'from': 'test@example.com',
            'body': long_body,
        }
        
        # Configure mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Summary of long email."
        self.mock_chat_completions.create.return_value = mock_response
        
        # Call the function
        result = summarize_email(email_data)
        
        # Verify the body was truncated in the prompt
        self.mock_chat_completions.create.assert_called_once()
        call_args = self.mock_chat_completions.create.call_args[1]
        # Check if the content includes truncation marker and doesn't exceed expected length
        user_message = call_args['messages'][1]['content']
        self.assertTrue(len(user_message) < 5000 + 200)  # Content should be shorter than body + other text
        self.assertIn('...', user_message)  # Should contain truncation indicator
        
        # Verify the summary is in the result
        self.assertEqual(result['summary'], "Summary of long email.")
    
    @patch('config.OPENAI_API_KEY', 'test_api_key')
    def test_summarize_email_api_error(self):
        """Test handling of API errors"""
        # Import summarize_email function after mocking
        import importlib
        if 'ai_summarizer' in sys.modules:
            del sys.modules['ai_summarizer']
        from ai_summarizer import summarize_email
        
        # Prepare test data
        email_data = {
            'subject': 'Test Subject',
            'from': 'test@example.com',
            'body': 'This is a test email body.',
        }
        
        # Configure OpenAI to raise an exception
        self.mock_chat_completions.create.side_effect = Exception("API Error")
        
        # Call the function
        result = summarize_email(email_data)
        
        # Verify error handling
        self.assertEqual(result['summary'], "Error generating summary.")
        self.assertEqual(result['subject'], 'Test Subject')
    
    @patch('config.OPENAI_API_KEY', 'test_api_key')
    def test_summarize_email_missing_fields(self):
        """Test summarization with missing email fields"""
        # Import summarize_email function after mocking
        import importlib
        if 'ai_summarizer' in sys.modules:
            del sys.modules['ai_summarizer']
        from ai_summarizer import summarize_email
        
        # Prepare test data with missing fields
        email_data = {}
        
        # Configure mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Summary of email with missing fields."
        self.mock_chat_completions.create.return_value = mock_response
        
        # Call the function
        result = summarize_email(email_data)
        
        # Verify the function handled missing fields
        self.mock_chat_completions.create.assert_called_once()
        call_args = self.mock_chat_completions.create.call_args[1]
        user_message = call_args['messages'][1]['content']
        self.assertIn('No Subject', user_message)
        self.assertIn('Unknown Sender', user_message)
        
        # Verify the summary is in the result
        self.assertEqual(result['summary'], "Summary of email with missing fields.")

if __name__ == '__main__':
    unittest.main() 