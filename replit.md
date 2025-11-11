# TempMail Telegram Bot

## Overview
This is a Telegram bot that generates temporary email addresses using two different services: Mail.tm and 1secMail. Users can choose between fast generation (1secMail) or secure password-protected emails (Mail.tm). The bot supports multiple concurrent users with isolated mailbox sessions and can save/reuse emails across both services.

## Project Type
Telegram Bot (Python/Pyrogram)

## Architecture
- **Language**: Python 3.11
- **Framework**: Pyrogram (Telegram Bot API)
- **Email APIs**: 
  - Mail.tm - Secure password-protected emails
  - 1secMail - Fast no-auth email generation
- **Session Management**: Per-user sessions stored in memory
- **Database**: PostgreSQL for persistent email storage and user tracking
- **Dependencies**: 
  - pyrogram - Telegram bot framework
  - TgCrypto - Cryptography for Pyrogram
  - requests - HTTP requests to email APIs
  - psycopg2-binary - PostgreSQL database adapter
  - wget - File downloading for email attachments (future use)

## Configuration
The bot requires three environment variables (configured as secrets):
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `API_ID` - Telegram API ID from https://my.telegram.org
- `API_HASH` - Telegram API Hash from https://my.telegram.org

## Features
- **Dual Email Services** - Choose between two providers:
  - ⚡ **1secMail** - Fast generation, no authentication, different domains
  - 🔐 **Mail.tm** - Secure with password protection, reliable delivery
- **Generate** unlimited temporary email addresses
- **Better Website Support** - Different domains help bypass email blocks
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
- **PostgreSQL storage** for persistent email management across both services

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
- 2025-11-11: Multi-Service Integration
  - **Feature**: Added 1secMail as second email service alongside Mail.tm
  - **Feature**: Users can now choose between two email services with different benefits
  - **Database**: Added `email_service` column to track which service each saved email uses
  - **Enhancement**: Better website compatibility with multiple email domains
  - **Fix**: Updated init_database() to include email_service column for fresh deployments
  - Bot now offers ⚡ 1secMail (fast) and 🔐 Mail.tm (secure) options

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
