# Email Monitor Discord Bot

A Discord bot that monitors an email inbox, uses AI to summarize email content, and sends notifications to a Discord channel.

## Features

- **Email Monitoring**: Automatically checks for new emails in a specified inbox
- **AI-Powered Summaries**: Uses OpenAI to generate concise summaries of email content
- **Discord Notifications**: Sends formatted notifications to a Discord channel
- **Email Filtering**: Option to whitelist specific email addresses

## Requirements

- Python 3.6+ (or Docker)
- Discord account and server with admin privileges
- Email account with IMAP access
- OpenAI API key

## Installation

### Option 1: Standard Installation

1. Clone this repository:

```bash
git clone https://github.com/irregularchat/20250404-Irregular-Hack-discord_bot
cd 20250404-Irregular-Hack-discord_bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Option 2: Docker Installation

1. Clone this repository:

```bash
git clone https://github.com/irregularchat/20250404-Irregular-Hack-discord_bot
cd 20250404-Irregular-Hack-discord_bot
```

2. Make sure Docker and Docker Compose are installed on your system.

## Configuration

### Option 1: Using .env file (for standard installation)

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

### Option 2: Using Unraid Environment Variables (for Docker installation)

When running the container in Unraid:

1. In the Unraid Docker UI, click "Add Container"
2. Find the container image or provide the repository URL
3. In the "Advanced View" section, add the following environment variables with your actual values:

| Variable Name | Example Value | Description |
|---------------|---------------|-------------|
| imap_server | imap.example.com | Your IMAP server address |
| imap_user | your-email@example.com | Your email username |
| imap_password | your-password-here | Your email password |
| imap_port | 993 | IMAP port (usually 993 for SSL) |
| imap_ssl | true | Whether to use SSL (true/false) |
| openai_api_key | your-openai-api-key | Your OpenAI API key |
| discord_token | your-discord-bot-token | Your Discord bot token |
| discord_channel_id | your-discord-channel-id | Your Discord channel ID |
| whitelisted_email_addresses | email1@example.com,email2@example.com | Comma-separated list of email addresses to monitor |
| log_level | INFO | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| log_concise | true | Whether to use concise logging (true/false) |
| log_to_file | false | Whether to log to file (true/false) |
| log_dir | logs | Directory to store logs |

4. Configure other container settings as needed (port mappings, volumes, etc.)
5. Click "Apply" to create and start the container

### Setting Up Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and configure a bot
3. Enable necessary bot permissions (Send Messages, Read Message History)
4. Generate and copy your bot token to the `.env` file
5. Invite the bot to your server using the OAuth2 URL generator

## Usage

### Running Locally

Run the bot with:

```bash
python bot.py
```

### Running with Docker

#### Standard Docker Compose

Start the bot using Docker Compose:

```bash
# Build and start in foreground (see logs in real-time)
docker-compose up

# Build and start in background (detached mode)
docker-compose up -d
```

To view logs when running in detached mode:

```bash
# View all logs
docker-compose logs -f

# View only the last 100 lines
docker-compose logs -f --tail=100
```

To stop the bot:

```bash
# If running in foreground, press Ctrl+C
# If running in background
docker-compose down
```

To rebuild the container after making changes:

```bash
docker-compose build
docker-compose up -d
```

#### Running in Unraid

1. In the Unraid Docker tab, click "Add Container"
2. Search for the container or provide the repository URL
3. Configure the environment variables as described in the Configuration section
4. Set up the appropriate paths for volumes
5. Apply the settings to start the container

### Docker Volume

The bot uses a Docker volume to persist logs. You can access these logs at any time, even after restarting the container.

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

This project is licensed under the [MIT License](LICENSE).