import openai
import config
from openai import OpenAI
from logger import get_logger

logger = get_logger(__name__)


class AISummarizer:
    """
    Class to handle email summarization using OpenAI API
    """

    def __init__(self, api_key=None):
        """
        Initialize the AISummarizer with an OpenAI API key

        Args:
            api_key (str): OpenAI API key. If None, uses config.OPENAI_API_KEY
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        if not self.api_key:
            logger.error("No OpenAI API key provided")
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=self.api_key)

    async def summarize_email(self, email_data):
        """
        Summarize email content using OpenAI API

        Args:
            email_data (dict): Dictionary containing email details

        Returns:
            dict: Original email data with added summary
        """
        try:
            # Extract relevant information
            subject = email_data.get("subject", "No Subject")
            sender = email_data.get("from", "Unknown Sender")
            body = email_data.get("body", "")

            # Validate email data
            if not body:
                logger.warning(
                    f"Email has empty body, creating simple summary for: {subject}"
                )
                email_data["summary"] = (
                    f"Email from {sender} with subject '{subject}' (no content)."
                )
                return email_data

            # Log email details before summarization
            body_preview = body[:100] + "..." if len(body) > 100 else body
            logger.info(
                f"Summarizing email: From={sender}, Subject={subject}, Body preview: {body_preview}"
            )
            logger.info(f"Body length: {len(body)} characters")

            # Truncate body if it's too long (OpenAI has token limits)
            max_body_length = 4000
            truncated_body = (
                body[:max_body_length] + "..." if len(body) > max_body_length else body
            )
            truncated = len(body) > max_body_length
            if truncated:
                logger.info(
                    f"Body was truncated from {len(body)} to {max_body_length} characters"
                )

            # Create improved messages for OpenAI Chat API with emphasis on content analysis
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert email analyst who creates precise, actionable summaries.
                
                SUMMARY GUIDELINES:
                1. Analyze the BODY content thoroughly - extract meaning, not just keywords
                2. Identify the primary purpose of the email (information, request, update, etc.)
                3. Extract concrete action items with their deadlines or urgency level
                4. Highlight key facts, figures, and crucial details that require attention
                5. Note contextual elements like project references, stakeholder mentions, or background information
                6. If attachments/links are mentioned, highlight what they contain or their importance
                7. Structure your summary logically with the most important information first
                8. Be concise but thorough - 3-5 sentences optimally
                
                CRITICAL: Prioritize SUBSTANCE over FORM. Focus on what matters in the email content, not superficial elements.
                Avoid restating the subject line as your summary - analyze the actual message content.
                """,
                },
                {
                    "role": "user",
                    "content": f"""
                Analyze and summarize this email, focusing on extracting the valuable content from the BODY:
                
                FROM: {sender}
                SUBJECT: {subject}
                
                BODY:
                {truncated_body}
                
                Create a comprehensive summary that extracts:
                - The main purpose/message
                - Any specific action items and deadlines
                - Key details, facts or figures
                - Important context or background information
                
                Your summary should be concise but capture all essential information from the email body.
                """,
                },
            ]

            # Call OpenAI API with newer model
            logger.info("Sending request to OpenAI API")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=550,
                temperature=0.3,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )

            # Extract summary from response
            summary = response.choices[0].message.content.strip()

            # Add summary to email data
            email_data["summary"] = summary
            logger.info(f"Successfully generated summary for email: {subject}")

            # Enhanced logging for summary quality assessment
            summary_length = len(summary)
            words = summary.split()
            word_count = len(words)
            avg_word_length = sum(len(word) for word in words) / max(1, word_count)

            logger.info(
                f"Summary stats: {word_count} words, {summary_length} chars, {avg_word_length:.1f} avg word length"
            )
            logger.info(
                f"Summary quality indicators: {'action item' in summary.lower()=}, {'deadline' in summary.lower()=}"
            )
            logger.info(f"Summary content: {summary}")

            # Check if summary seems too generic
            generic_phrases = [
                "email contains",
                "the email is about",
                "this email discusses",
            ]
            if any(phrase in summary.lower() for phrase in generic_phrases):
                logger.warning(f"Summary may be too generic for email: {subject}")

            return email_data

        except openai.APIError as api_err:
            logger.error(f"OpenAI API error: {str(api_err)}")
            email_data["summary"] = (
                f"Email from {sender} about '{subject}' (summary unavailable due to API error)."
            )
            return email_data
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            logger.exception("Detailed exception information:")
            email_data["summary"] = (
                f"Email from {sender} about '{subject}' (summary unavailable)."
            )
            return email_data


# For backwards compatibility, provide the summarize_email function
def summarize_email(email_data):
    """
    Standalone function to summarize email content using OpenAI API
    This is provided for backwards compatibility and test compatibility

    Args:
        email_data (dict): Dictionary containing email details

    Returns:
        dict: Original email data with added summary
    """
    # Create a simple summary without calling the async function
    # This avoids "This event loop is already running" errors when called from an existing async context
    try:
        # Extract email information
        subject = email_data.get("subject", "No Subject")
        sender = email_data.get("from", "Unknown Sender")
        body = email_data.get("body", "")

        # Create a better-quality fallback summary with basic NLP-like extraction
        if body:
            # Extract first sentence as a potential summary starter
            first_sentence = (
                body.split(".")[0].strip() if "." in body else body[:50].strip()
            )

            # Look for potential action items
            action_keywords = [
                "please",
                "request",
                "need",
                "required",
                "urgent",
                "important",
                "deadline",
                "by tomorrow",
                "by next",
                "attached",
            ]
            action_items = []
            for keyword in action_keywords:
                if keyword.lower() in body.lower():
                    # Get the sentence containing the keyword
                    sentences = body.replace("\n", " ").split(".")
                    for sentence in sentences:
                        if keyword.lower() in sentence.lower():
                            action_items.append(sentence.strip())
                            break

            # Create a more informative fallback summary
            if action_items:
                action_summary = (
                    " Action item: " + action_items[0] + "." if action_items else ""
                )
                email_data["summary"] = (
                    f"Email from {sender} regarding {subject}. {first_sentence[:100]}...{action_summary}"
                )
            else:
                email_data["summary"] = (
                    f"Email from {sender} regarding {subject}. {first_sentence[:150]}..."
                )
        else:
            email_data["summary"] = (
                f"Email from {sender} with subject '{subject}' (no content)."
            )

        # Attempt to use async method only if we're not already in an event loop
        import asyncio

        try:
            # Check if we're in an event loop
            running_loop = asyncio.get_running_loop()
            # If we get here, we're in an event loop, so we'll use the basic summary
            logger.info(
                f"Using basic summary for email: {subject} (avoiding nested event loop)"
            )
        except RuntimeError:
            # No running event loop, we can safely create one
            summarizer = AISummarizer()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                email_data = loop.run_until_complete(
                    summarizer.summarize_email(email_data)
                )
            finally:
                loop.close()

        return email_data
    except Exception as e:
        logger.error(f"Error in synchronous summarize_email: {str(e)}")
        email_data["summary"] = (
            f"Email about {email_data.get('subject', 'unknown subject')}."
        )
        return email_data
