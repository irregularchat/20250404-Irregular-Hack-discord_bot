# Email Monitor Discord Bot

A Discord bot that monitors an email inbox, uses AI to summarize email content, and sends notifications to a Discord channel.

## Features

- **Email Monitoring**: Automatically checks for new emails in a specified inbox
- **AI-Powered Summaries**: Uses OpenAI to generate concise summaries of email content
- **Discord Notifications**: Sends formatted notifications to a Discord channel
- **Email Filtering**: Option to whitelist specific email addresses

## Requirements

- Python 3.6+
- Discord account and server with admin privileges
- Email account with IMAP access
- OpenAI API key

## Installation

1. Clone this repository:
```bash
git clone https://github.com/irregularchat/20250404-Irregular-Hack-discord_bot
cd 20250404-Irregular-Hack-discord_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file to create your configuration:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your actual credentials:

```
imap_server=your_imap_server.com
imap_user=your_email@example.com
imap_password=your_email_password
imap_port=993
imap_ssl=true
openai_api_key=your_openai_api_key
discord_token=your_discord_bot_token
discord_channel_id=your_discord_channel_id
whitelisted_email_addresses=email1@example.com,email2@example.com
```

> **Important**: Never commit your `.env` file with real credentials to version control. The `.env` file is already added to `.gitignore` to prevent accidental commits.

### Setting Up Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and configure a bot
3. Enable necessary bot permissions (Send Messages, Read Message History)
4. Generate and copy your bot token to the `.env` file
5. Invite the bot to your server using the OAuth2 URL generator

## Usage

Run the bot with:

```bash
python bot.py
```

The bot will:
1. Connect to your email server via IMAP
2. Check for new emails at regular intervals
3. Generate AI summaries for new email content
4. Send formatted notifications to your Discord channel

## Customization

You can modify the following aspects:
- Check frequency in the bot configuration
- Email filter criteria
- Discord message format
- AI prompt for email summarization

## License

[Your preferred license]