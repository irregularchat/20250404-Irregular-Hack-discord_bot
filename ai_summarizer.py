import openai
import logging
import config
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            subject = email_data.get('subject', 'No Subject')
            sender = email_data.get('from', 'Unknown Sender')
            body = email_data.get('body', '')
            
            # Truncate body if it's too long (OpenAI has token limits)
            max_body_length = 4000
            truncated_body = body[:max_body_length] + "..." if len(body) > max_body_length else body
            
            # Create messages for OpenAI Chat API
            messages = [
                {"role": "system", "content": "You are a helpful assistant that summarizes emails concisely."},
                {"role": "user", "content": f"""
                Please provide a concise summary (3-5 sentences) of the following email:
                
                From: {sender}
                Subject: {subject}
                
                Body:
                {truncated_body}
                
                Summary:
                """}
            ]
            
            # Call OpenAI API with newer model
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.3,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract summary from response
            summary = response.choices[0].message.content.strip()
            
            # Add summary to email data
            email_data['summary'] = summary
            logger.info(f"Successfully generated summary for email: {subject}")
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            email_data['summary'] = "Error generating summary."
            return email_data

# For backwards compatibility, provide the summarize_email function
def summarize_email(email_data):
    """
    Standalone function to summarize email content using OpenAI API
    This is provided for backwards compatibility
    
    Args:
        email_data (dict): Dictionary containing email details
        
    Returns:
        dict: Original email data with added summary
    """
    summarizer = AISummarizer()
    # Since the class method is async, we need to run it in a synchronous manner for compatibility
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(summarizer.summarize_email(email_data))
