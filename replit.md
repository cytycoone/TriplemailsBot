# TempMail Telegram Bot

## Overview
This is a Telegram bot that generates temporary email addresses using the Mail.tm API. Users can generate random temporary emails, check for new messages, and view message contents with attachments directly through Telegram. The bot supports multiple concurrent users with isolated mailbox sessions.

## Project Type
Telegram Bot (Python/Pyrogram)

## Architecture
- **Language**: Python 3.11
- **Framework**: Pyrogram (Telegram Bot API)
- **API**: Mail.tm for temporary email generation and management
- **Session Management**: Per-user sessions stored in memory
- **Dependencies**: 
  - pyrogram - Telegram bot framework
  - TgCrypto - Cryptography for Pyrogram
  - requests - HTTP requests to Mail.tm API
  - wget - File downloading for email attachments (future use)

## Configuration
The bot requires three environment variables (configured as secrets):
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `API_ID` - Telegram API ID from https://my.telegram.org
- `API_HASH` - Telegram API Hash from https://my.telegram.org

## Features
- **Generate** unlimited temporary email addresses
- **Save emails** with custom names for future reuse
- **Load saved emails** to receive new verification codes
- **Manage multiple emails** with list, delete, and current commands
- **Refresh** to check for new messages
- **View message details** including:
  - Sender information
  - Subject
  - Message body
  - Attachments list
- **Professional UI** with emoji buttons and intuitive navigation
- **PostgreSQL storage** for persistent email management

## Deployment
This bot runs as a worker process (no web frontend). It connects to Telegram's servers and listens for user commands.

## Available Commands

### Basic Commands
- `/start` - Start the bot and see main menu
- `/generate` - Create a new temporary email
- `/help` - Show comprehensive help guide

### Email Management Commands
- `/save <name>` - Save current email with a custom name (e.g., `/save gaming`)
- `/list` - List all your saved emails
- `/load <name>` - Load a saved email to reuse it
- `/delete <name>` - Delete a saved email
- `/current` - Show your current active email

### Button Actions
- 📧 **Generate New** - Create a fresh temporary email
- 🔄 **Refresh** - Check for new messages
- 💾 **Save Email** - Save current email for future reuse
- 📋 **My Emails** - View all your saved emails
- 📖 **View Message** - Read full message content
- ❌ **Close** - End current session

## Recent Changes
- 2025-11-10: Initial Replit setup and API migration
  - **Setup**: Added Python 3.11 environment
  - **Setup**: Installed dependencies via pip (pyrogram, TgCrypto, requests, wget, psycopg2-binary)
  - **Setup**: Updated .gitignore for Python and Telegram session files
  - **Setup**: Created workflow for bot execution
  - **Fix**: Added proper environment variable validation in Config.py
  - **Critical Fix**: Migrated from 1secmail.com to Mail.tm API (original API was blocked)
  - **Critical Fix**: Implemented per-user session management for multi-user support
  - **Enhancement**: Added comprehensive error handling with user-friendly messages
  - **Enhancement**: Improved message viewing with proper attachment listing
  - **Feature**: Added PostgreSQL database for persistent email storage
  - **Feature**: Implemented save/load/delete email functionality
  - **Feature**: Added professional command set (/save, /load, /list, /delete, /current, /help)
  - **Feature**: Enhanced UI with emoji buttons and better organization
  - **Feature**: Users can now reuse saved emails to receive new verification codes
  - Bot is now running successfully with full professional feature set

## Database Schema

### Tables

**users** - Tracks all users who interact with the bot
- `user_id` - Telegram user ID (unique)
- `username` - Telegram username
- `first_name` - User's first name
- `last_name` - User's last name
- `first_interaction` - When user first used the bot
- `last_interaction` - Most recent interaction
- `total_interactions` - Count of all interactions

**saved_emails** - Stores saved emails per user
- `user_id` - Telegram user ID
- `email_name` - Custom name for the email
- `email_address` - The temporary email address
- `password` - Email account password
- `created_at` - When email was saved

### Useful SQL Queries

**View all users:**
```sql
SELECT * FROM users ORDER BY last_interaction DESC;
```

**Count total users:**
```sql
SELECT COUNT(*) as total_users FROM users;
```

**View user activity:**
```sql
SELECT username, first_name, total_interactions, last_interaction 
FROM users 
ORDER BY total_interactions DESC;
```

**New users today:**
```sql
SELECT COUNT(*) as new_users_today 
FROM users 
WHERE DATE(first_interaction) = CURRENT_DATE;
```

**Active users (last 7 days):**
```sql
SELECT COUNT(*) as active_users 
FROM users 
WHERE last_interaction >= CURRENT_DATE - INTERVAL '7 days';
```

## Technical Notes
- **API**: Uses Mail.tm's free API with bearer token authentication
- **Database**: PostgreSQL stores saved emails and user data with proper isolation
- **Sessions**: Per-user session management in memory
- **Security**: Parameterized SQL queries prevent injection attacks
- **Multi-user**: Fully supports concurrent users with isolated data
- **Persistence**: All data survives bot restarts via database storage
- **User Tracking**: Automatically logs all users who interact with the bot
- **Future**: Consider connection pooling for high-traffic scenarios
