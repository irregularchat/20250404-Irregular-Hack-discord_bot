import email
import logging
from email.header import decode_header
from imapclient import IMAPClient
from datetime import datetime, timedelta
from src.utils import config
from src.utils.logger import get_logger

logger = get_logger(
    __name__,
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    concise=config.LOG_CONCISE,
    file=config.LOG_TO_FILE,
    log_file=config.LOG_FILE,
)


class EmailHandler:
    def __init__(self):
        self.server = None
        self.last_checked = datetime.now() - timedelta(
            hours=1
        )  # Start by checking emails from the last hour

    def connect(self):
        """Connect to the IMAP server"""
        try:
            logger.info(f"Connecting to IMAP server: {config.IMAP_SERVER}")
            self.server = IMAPClient(
                config.IMAP_SERVER, port=config.IMAP_PORT, use_uid=True, ssl=True
            )
            self.server.login(config.IMAP_USER, config.IMAP_PASSWORD)
            logger.info("Successfully connected to IMAP server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from the IMAP server"""
        if self.server:
            try:
                self.server.logout()
                logger.info("Disconnected from IMAP server")
            except Exception as e:
                logger.error(f"Error disconnecting from IMAP server: {str(e)}")

    def get_new_emails(self):
        """Fetch new emails from the server"""
        if not self.server:
            if not self.connect():
                return []

        try:
            # Select the inbox
            self.server.select_folder("INBOX")

            # Search for unseen emails
            messages = self.server.search(["UNSEEN"])

            if not messages:
                logger.info("No new emails found")
                return []

            logger.info(f"Found {len(messages)} new emails")

            # Fetch email data
            email_data = []
            for uid, message_data in self.server.fetch(
                messages, ["ENVELOPE", "RFC822"]
            ).items():
                try:
                    raw_email = message_data[b"RFC822"]
                    email_message = email.message_from_bytes(raw_email)

                    # Extract email details
                    subject = self._decode_email_header(email_message["Subject"])
                    from_address = self._decode_email_header(email_message["From"])
                    date = email_message["Date"]

                    # Check if email is from a whitelisted address (if whitelist is enabled)
                    if config.WHITELISTED_EMAIL_ADDRESSES:
                        if not any(
                            addr in from_address
                            for addr in config.WHITELISTED_EMAIL_ADDRESSES
                        ):
                            logger.info(
                                f"Skipping email from non-whitelisted address: {from_address}"
                            )
                            continue

                    # Extract email body
                    body = self._get_email_body(email_message)

                    email_data.append(
                        {
                            "uid": uid,
                            "subject": subject,
                            "from": from_address,
                            "date": date,
                            "body": body,
                        }
                    )

                except Exception as e:
                    logger.error(f"Error processing email: {str(e)}")

            self.last_checked = datetime.now()
            return email_data

        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            # Try to reconnect
            self.disconnect()
            self.connect()
            return []

    def _decode_email_header(self, header):
        """Decode email header"""
        if header is None:
            return ""

        decoded_header = decode_header(header)
        header_parts = []

        for content, encoding in decoded_header:
            if isinstance(content, bytes):
                if encoding:
                    header_parts.append(
                        content.decode(encoding or "utf-8", errors="replace")
                    )
                else:
                    header_parts.append(content.decode("utf-8", errors="replace"))
            else:
                header_parts.append(content)

        return "".join(header_parts)

    def _get_email_body(self, email_message):
        """Extract the email body"""
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(
                            "utf-8", errors="replace"
                        )
                    except:
                        body = part.get_payload(decode=True).decode(
                            "latin-1", errors="replace"
                        )
                    break

                if content_type == "text/html" and not body:
                    try:
                        body = part.get_payload(decode=True).decode(
                            "utf-8", errors="replace"
                        )
                    except:
                        body = part.get_payload(decode=True).decode(
                            "latin-1", errors="replace"
                        )
        else:
            # Not multipart - get the payload directly
            try:
                body = email_message.get_payload(decode=True).decode(
                    "utf-8", errors="replace"
                )
            except:
                body = email_message.get_payload(decode=True).decode(
                    "latin-1", errors="replace"
                )

        return body
