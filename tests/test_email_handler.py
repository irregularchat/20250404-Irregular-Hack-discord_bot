import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_handler import EmailHandler

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



class TestEmailHandler(unittest.TestCase):

    def setUp(self):
        # Create a patch for config values
        self.config_patcher = patch(
            "email_handler.config",
            IMAP_SERVER="test.server.com",
            IMAP_USER="test@example.com",
            IMAP_PASSWORD="testpassword",
            IMAP_PORT=993,
            WHITELISTED_EMAIL_ADDRESSES=["allowed@example.com"],
        )
        self.mock_config = self.config_patcher.start()
        self.handler = EmailHandler()

    def tearDown(self):
        self.config_patcher.stop()

    @patch("email_handler.IMAPClient")
    def test_connect_success(self, mock_imap):
        """Test successful connection to IMAP server"""
        mock_client = MagicMock()
        mock_imap.return_value = mock_client

        result = self.handler.connect()

        mock_imap.assert_called_once_with(
            "test.server.com", port=993, use_uid=True, ssl=True
        )
        mock_client.login.assert_called_once_with("test@example.com", "testpassword")
        self.assertTrue(result)

    @patch("email_handler.IMAPClient")
    def test_connect_failure(self, mock_imap):
        """Test failed connection to IMAP server"""
        mock_imap.side_effect = Exception("Connection failed")

        result = self.handler.connect()

        self.assertFalse(result)

    @patch("email_handler.IMAPClient")
    def test_disconnect(self, mock_imap):
        """Test disconnection from IMAP server"""
        mock_client = MagicMock()
        mock_imap.return_value = mock_client

        self.handler.connect()
        self.handler.disconnect()

        mock_client.logout.assert_called_once()

    @patch("email_handler.IMAPClient")
    def test_get_new_emails_none(self, mock_imap):
        """Test getting new emails when none are available"""
        mock_client = MagicMock()
        mock_client.search.return_value = []
        mock_imap.return_value = mock_client

        self.handler.connect()
        emails = self.handler.get_new_emails()

        mock_client.select_folder.assert_called_once_with("INBOX")
        mock_client.search.assert_called_once_with(["UNSEEN"])
        self.assertEqual(emails, [])

    @patch("email_handler.IMAPClient")
    @patch("email_handler.email.message_from_bytes")
    def test_get_new_emails_with_data(self, mock_message_from_bytes, mock_imap):
        """Test getting new emails when some are available"""
        # Set up mock IMAP client
        mock_client = MagicMock()
        mock_client.search.return_value = [1, 2]

        # Create mock email messages
        email1 = EmailMessage()
        email1["Subject"] = "Test Subject 1"
        email1["From"] = "allowed@example.com"
        email1["Date"] = "Thu, 01 Jan 2023 12:00:00 +0000"
        email1.set_content("Test body 1")

        email2 = EmailMessage()
        email2["Subject"] = "Test Subject 2"
        email2["From"] = "allowed@example.com"
        email2["Date"] = "Thu, 02 Jan 2023 12:00:00 +0000"
        email2.set_content("Test body 2")

        # Set up the mock fetch response
        fetch_response = {
            1: {b"ENVELOPE": "envelope1", b"RFC822": b"raw_email1"},
            2: {b"ENVELOPE": "envelope2", b"RFC822": b"raw_email2"},
        }
        mock_client.fetch.return_value = fetch_response
        mock_imap.return_value = mock_client

        # Set up mock message parsing
        mock_message_from_bytes.side_effect = [email1, email2]

        # Patch the _get_email_body method to return body without newlines
        with patch.object(EmailHandler, "_get_email_body") as mock_get_body:
            mock_get_body.side_effect = ["Test body 1", "Test body 2"]

            # Execute the method
            self.handler.connect()
            emails = self.handler.get_new_emails()

            # Assertions
            mock_client.select_folder.assert_called_once_with("INBOX")
            mock_client.search.assert_called_once_with(["UNSEEN"])
            mock_client.fetch.assert_called_once_with([1, 2], ["ENVELOPE", "RFC822"])

            self.assertEqual(len(emails), 2)
            self.assertEqual(emails[0]["uid"], 1)
            self.assertEqual(emails[0]["subject"], "Test Subject 1")
            self.assertEqual(emails[0]["from"], "allowed@example.com")
            self.assertEqual(emails[0]["body"], "Test body 1")

            self.assertEqual(emails[1]["uid"], 2)
            self.assertEqual(emails[1]["subject"], "Test Subject 2")

    def test_decode_email_header(self):
        """Test decoding of email headers"""
        handler = EmailHandler()

        # Test with simple ASCII header
        result = handler._decode_email_header("Simple Header")
        self.assertEqual(result, "Simple Header")

        # Test with None
        result = handler._decode_email_header(None)
        self.assertEqual(result, "")

    def test_get_email_body(self):
        """Test extracting the email body"""
        handler = EmailHandler()

        # Test with simple non-multipart message
        simple_email = EmailMessage()
        simple_email.set_content("Simple body text")

        # Get the body and strip any trailing newlines
        result = handler._get_email_body(simple_email).rstrip("\n")
        self.assertEqual(result, "Simple body text")

        # Test with multipart message - using MIME multipart instead of EmailMessage
        multipart_email = MIMEMultipart("mixed")
        plain_part = MIMEText("Plain text body", "plain")
        html_part = MIMEText("<p>HTML body</p>", "html")

        # Add the parts to the multipart message
        multipart_email.attach(plain_part)
        multipart_email.attach(html_part)

        # Get the body and strip any trailing newlines
        result = handler._get_email_body(multipart_email).rstrip("\n")
        self.assertEqual(result, "Plain text body")


if __name__ == "__main__":
    unittest.main()
