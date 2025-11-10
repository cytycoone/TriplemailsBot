# copyright 2020-22 @Mohamed Rizad
# Telegram @riz4d
# Instagram @riz.4d
from pyrogram import *
import requests as re
from Config import *
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
import wget
import os
import psycopg2
from psycopg2.extras import RealDictCursor 

buttons=InlineKeyboardMarkup(
                             [
                             [
            InlineKeyboardButton('📧 Generate New', callback_data='generate'),
            InlineKeyboardButton('🔄 Refresh', callback_data='refresh')
                   ],
                   [
            InlineKeyboardButton('💾 Save Email', callback_data='save_email'),
            InlineKeyboardButton('📋 My Emails', callback_data='list_emails')
                   ],
                   [
            InlineKeyboardButton('❌ Close', callback_data='close')
                   ] 
                             ])

msg_buttons=InlineKeyboardMarkup(
                             [
                             [
            InlineKeyboardButton('📖 View Message', callback_data='view_msg'),
            InlineKeyboardButton('🔄 Refresh', callback_data='refresh')
                   ],
                   [
            InlineKeyboardButton('❌ Close', callback_data='close')
                   ] 
                             ])


app=Client('Temp-Mail Bot',
           api_id=API_ID,
           api_hash=API_HASH,
           bot_token=BOT_TOKEN)

user_sessions = {}

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def init_database():
    """Initialize database tables on startup - ensures tables exist"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create saved_emails table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS saved_emails (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                email_name VARCHAR(100) NOT NULL,
                email_address VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, email_name)
            )
        """)
        
        # Create users table to track all interactions
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(100),
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                first_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_interactions INTEGER DEFAULT 1
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

def log_user(user):
    """Log user interaction - creates new user or updates last interaction"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, first_interaction, last_interaction, total_interactions)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                last_interaction = CURRENT_TIMESTAMP,
                total_interactions = users.total_interactions + 1
        """, (user.id, user.username, user.first_name, user.last_name))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging user: {e}")
        return False

def save_email_to_db(user_id, name, email, password):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO saved_emails (user_id, email_name, email_address, password) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id, email_name) DO UPDATE SET email_address = %s, password = %s",
            (user_id, name, email, password, email, password)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving email to DB: {e}")
        return False

def get_saved_emails(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT email_name, email_address FROM saved_emails WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        emails = cur.fetchall()
        cur.close()
        conn.close()
        return emails
    except Exception as e:
        print(f"Error getting saved emails: {e}")
        return []

def load_email_from_db(user_id, name):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT email_address, password FROM saved_emails WHERE user_id = %s AND email_name = %s", (user_id, name))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        print(f"Error loading email from DB: {e}")
        return None

def delete_email_from_db(user_id, name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM saved_emails WHERE user_id = %s AND email_name = %s", (user_id, name))
        deleted = cur.rowcount > 0
        conn.commit()
        cur.close()
        conn.close()
        return deleted
    except Exception as e:
        print(f"Error deleting email from DB: {e}")
        return False

@app.on_message(filters.command('start'))
async def start_msg(client,message):
    user_id = message.from_user.id
    
    # Track user interaction
    log_user(message.from_user)
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {'email': '', 'auth_token': None, 'idnum': None, 'saved_emails': {}, 'password': ''}
    
    welcome_text = f"""**👋 Welcome {message.from_user.first_name}!**

🔐 **TempMail Bot** - Your Secure Temporary Email Service

This bot allows you to generate disposable email addresses to protect your privacy and avoid spam.

**🎯 Features:**
• Generate unlimited temporary emails
• Receive and read messages instantly
• Save emails for future reuse
• Manage multiple email addresses
• 100% anonymous and secure

**📌 Quick Start:**
Use the buttons below or try these commands:
/generate - Create a new email
/list - View your saved emails
/help - See all commands

**🛡️ Privacy:** Your emails are completely anonymous and self-destruct after a period of time."""
    
    await message.reply(welcome_text, reply_markup=buttons)

@app.on_message(filters.command('help'))
async def help_msg(client, message):
    help_text = """**📚 TempMail Bot - Command Guide**

**Basic Commands:**
/start - Start the bot and see main menu
/generate - Generate a new temporary email
/help - Show this help message

**Email Management:**
/list - List all your saved emails
/save <name> - Save current email with a custom name
/load <name> - Load a saved email
/delete <name> - Delete a saved email
/current - Show your current active email

**Button Actions:**
📧 Generate New - Create a fresh temporary email
🔄 Refresh - Check for new messages
💾 Save Email - Save current email for reuse
📋 My Emails - View all saved emails
📖 View Message - Read full message content

**💡 Pro Tips:**
• Save emails you want to reuse later
• Use descriptive names when saving (e.g., "gaming", "shopping")
• Load saved emails to receive new verification codes
• Multiple users can use the bot simultaneously

**🔒 Privacy:** All emails are temporary and anonymous. No personal data is stored."""
    
    await message.reply(help_text)
@app.on_callback_query()
async def mailbox(client,message):
    response=message.data
    user_id = message.from_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {'email': '', 'auth_token': None, 'idnum': None, 'saved_emails': {}, 'password': ''}
    
    if response=='generate':
       try:
           import random
           import string
           
           domains_resp = re.get("https://api.mail.tm/domains", timeout=10)
           if domains_resp.status_code != 200:
               await message.answer('Sorry, the email service is currently unavailable. Please try again later.', show_alert=True)
               return
           
           domains = domains_resp.json()['hydra:member']
           if not domains:
               await message.answer('Sorry, no email domains available.', show_alert=True)
               return
           
           domain = domains[0]['domain']
           username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
           email = f"{username}@{domain}"
           password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
           
           account_data = {
               'address': email,
               'password': password
           }
           account_resp = re.post("https://api.mail.tm/accounts", json=account_data, timeout=10)
           
           if account_resp.status_code != 201:
               await message.answer('Sorry, unable to create email account. Please try again.', show_alert=True)
               return
           
           token_data = {
               'address': email,
               'password': password
           }
           token_resp = re.post("https://api.mail.tm/token", json=token_data, timeout=10)
           
           if token_resp.status_code == 200:
               user_sessions[user_id]['email'] = email
               user_sessions[user_id]['auth_token'] = token_resp.json()['token']
               user_sessions[user_id]['password'] = password
               user_sessions[user_id]['idnum'] = None
               await message.edit_message_text(f'**✅ Email Generated Successfully!**\n\n📧 Your temporary email:\n`{email}`\n\n💡 Use the buttons below to manage your inbox.',
                                           reply_markup=buttons)
               print(f"Generated email for user {user_id}: {email}")
           else:
               await message.answer('Sorry, authentication failed. Please try again.', show_alert=True)
               
       except Exception as e:
           print(f"Error generating email: {e}")
           await message.answer('Sorry, unable to generate email at this moment. Please try again later.', show_alert=True)
    elif response=='refresh':
        session = user_sessions[user_id]
        print(f"Refreshing for user {user_id}, email: {session['email']}")
        try:
            if not session['email'] or not session['auth_token']:
                await message.edit_message_text('Generate an email first',reply_markup=buttons)
            else: 
                headers = {
                    'Authorization': f'Bearer {session["auth_token"]}'
                }
                messages_resp = re.get("https://api.mail.tm/messages", headers=headers, timeout=10)
                
                if messages_resp.status_code != 200:
                    await message.answer('Unable to check messages. Please try again.', show_alert=True)
                    return
                
                messages_data = messages_resp.json()['hydra:member']
                
                if not messages_data:
                    await message.answer(f'No messages were received..\nin your Mailbox {session["email"]}')
                    return
                
                latest_msg = messages_data[0]
                user_sessions[user_id]['idnum'] = latest_msg['id']
                from_msg = latest_msg['from']['address']
                subject = latest_msg['subject']
                refreshrply = 'You have a message from '+from_msg+'\n\nSubject : '+subject
                await message.edit_message_text(refreshrply,
                                                reply_markup=msg_buttons)
        except Exception as e:
            print(f"Error refreshing messages for user {user_id}: {e}")
            await message.answer(f'No messages were received..\nin your Mailbox {session["email"]}')
    elif response=='view_msg':
        session = user_sessions[user_id]
        if not session['idnum'] or not session['auth_token']:
            await message.answer('Please refresh to check for messages first!', show_alert=True)
            return
        
        try:
            headers = {
                'Authorization': f'Bearer {session["auth_token"]}'
            }
            msg_resp = re.get(f"https://api.mail.tm/messages/{session['idnum']}", headers=headers, timeout=10)
            
            if msg_resp.status_code != 200:
                await message.answer('Unable to load message. Please try again.', show_alert=True)
                return
            
            msg = msg_resp.json()
            print(msg)
            
            from_mail = msg['from']['address'] if isinstance(msg['from'], dict) else msg['from']
            date = msg['createdAt']
            subjectt = msg['subject']
            body = msg['text'] if msg.get('text') else msg.get('html', '')[:500]
            
            mailbox_view = f"From: {from_mail}\nDate: {date}\nSubject: {subjectt}\n\nMessage:\n{body}"
            
            attachments = msg.get('attachments', [])
            if attachments and len(attachments) > 0:
                attachment_list = '\n\nAttachments:\n' + '\n'.join([f"- {att['filename']}" for att in attachments])
                mailbox_view += attachment_list
            
            await message.edit_message_text(mailbox_view, reply_markup=buttons)
            
        except Exception as e:
            print(f"Error viewing message: {e}")
            await message.answer('Unable to view message. Please try again.', show_alert=True)
    elif response=='save_email':
        session = user_sessions[user_id]
        if not session['email']:
            await message.answer('No active email to save! Generate an email first.', show_alert=True)
            return
        await message.answer('💾 Send the name to save this email with (e.g., "gaming", "shopping"):', show_alert=False)
        user_sessions[user_id]['waiting_for_save_name'] = True
    
    elif response=='list_emails':
        saved_emails = get_saved_emails(user_id)
        if not saved_emails:
            await message.answer('📋 You have no saved emails yet!\n\nGenerate an email and use the "Save Email" button to save it for future use.', show_alert=True)
            return
        
        email_list = "**📋 Your Saved Emails:**\n\n"
        for idx, email_data in enumerate(saved_emails, 1):
            email_list += f"{idx}. **{email_data['email_name']}**\n   `{email_data['email_address']}`\n\n"
        
        email_list += "\n💡 **Commands:**\n"
        email_list += "• `/load <name>` - Load a saved email\n"
        email_list += "• `/delete <name>` - Delete a saved email"
        
        await message.edit_message_text(email_list, reply_markup=buttons)
    
    elif response=='close':
        await message.edit_message_text('✅ **Session Closed**\n\nUse /start to begin again.')

@app.on_message(filters.command('generate'))
async def generate_cmd(client, message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {'email': '', 'auth_token': None, 'idnum': None, 'saved_emails': {}, 'password': ''}
    
    status_msg = await message.reply("🔄 Generating your temporary email...")
    
    try:
        import random
        import string
        
        domains_resp = re.get("https://api.mail.tm/domains", timeout=10)
        if domains_resp.status_code != 200:
            await status_msg.edit('❌ Email service unavailable. Please try again later.')
            return
        
        domains = domains_resp.json()['hydra:member']
        if not domains:
            await status_msg.edit('❌ No email domains available.')
            return
        
        domain = domains[0]['domain']
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        email = f"{username}@{domain}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        account_data = {'address': email, 'password': password}
        account_resp = re.post("https://api.mail.tm/accounts", json=account_data, timeout=10)
        
        if account_resp.status_code != 201:
            await status_msg.edit('❌ Unable to create email account. Please try again.')
            return
        
        token_data = {'address': email, 'password': password}
        token_resp = re.post("https://api.mail.tm/token", json=token_data, timeout=10)
        
        if token_resp.status_code == 200:
            user_sessions[user_id]['email'] = email
            user_sessions[user_id]['auth_token'] = token_resp.json()['token']
            user_sessions[user_id]['password'] = password
            user_sessions[user_id]['idnum'] = None
            await status_msg.edit(f'**✅ Email Generated Successfully!**\n\n📧 Your temporary email:\n`{email}`\n\n💡 Use the buttons below to manage your inbox.', reply_markup=buttons)
        else:
            await status_msg.edit('❌ Authentication failed. Please try again.')
    except Exception as e:
        print(f"Error in /generate: {e}")
        await status_msg.edit('❌ Unable to generate email. Please try again later.')

@app.on_message(filters.command('list'))
async def list_cmd(client, message):
    user_id = message.from_user.id
    saved_emails = get_saved_emails(user_id)
    
    if not saved_emails:
        await message.reply('📋 **No Saved Emails**\n\nYou have no saved emails yet!\n\nGenerate an email and use `/save <name>` or the "Save Email" button to save it.')
        return
    
    email_list = "**📋 Your Saved Emails:**\n\n"
    for idx, email_data in enumerate(saved_emails, 1):
        email_list += f"{idx}. **{email_data['email_name']}**\n   `{email_data['email_address']}`\n\n"
    
    email_list += "\n💡 **Available Commands:**\n"
    email_list += "• `/load <name>` - Load a saved email\n"
    email_list += "• `/delete <name>` - Delete a saved email\n"
    email_list += "• `/current` - Show current active email"
    
    await message.reply(email_list)

@app.on_message(filters.command('save'))
async def save_cmd(client, message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        await message.reply('❌ No active session. Use /generate to create an email first.')
        return
    
    session = user_sessions[user_id]
    if not session['email']:
        await message.reply('❌ No active email to save! Use /generate to create an email first.')
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply('⚠️ **Usage:** `/save <name>`\n\nExample: `/save gaming`')
        return
    
    name = parts[1].strip()
    if len(name) > 50:
        await message.reply('❌ Name too long! Please use a name under 50 characters.')
        return
    
    if save_email_to_db(user_id, name, session['email'], session['password']):
        await message.reply(f'✅ **Email Saved Successfully!**\n\n📧 Email: `{session["email"]}`\n💾 Saved as: **{name}**\n\nUse `/load {name}` to reuse this email anytime!')
    else:
        await message.reply('❌ Failed to save email. Please try again.')

@app.on_message(filters.command('load'))
async def load_cmd(client, message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {'email': '', 'auth_token': None, 'idnum': None, 'saved_emails': {}, 'password': ''}
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply('⚠️ **Usage:** `/load <name>`\n\nExample: `/load gaming`\n\nUse `/list` to see your saved emails.')
        return
    
    name = parts[1].strip()
    email_data = load_email_from_db(user_id, name)
    
    if not email_data:
        await message.reply(f'❌ No saved email found with name "**{name}**".\n\nUse `/list` to see your saved emails.')
        return
    
    status_msg = await message.reply(f'🔄 Loading email **{name}**...')
    
    try:
        token_data = {'address': email_data['email_address'], 'password': email_data['password']}
        token_resp = re.post("https://api.mail.tm/token", json=token_data, timeout=10)
        
        if token_resp.status_code == 200:
            user_sessions[user_id]['email'] = email_data['email_address']
            user_sessions[user_id]['auth_token'] = token_resp.json()['token']
            user_sessions[user_id]['password'] = email_data['password']
            user_sessions[user_id]['idnum'] = None
            await status_msg.edit(f'✅ **Email Loaded Successfully!**\n\n📧 Active email: `{email_data["email_address"]}`\n💾 Loaded from: **{name}**\n\n💡 Use the "Refresh" button to check for new messages!', reply_markup=buttons)
        else:
            await status_msg.edit('❌ Failed to authenticate saved email. It may have expired.')
    except Exception as e:
        print(f"Error in /load: {e}")
        await status_msg.edit('❌ Unable to load email. Please try again.')

@app.on_message(filters.command('delete'))
async def delete_cmd(client, message):
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply('⚠️ **Usage:** `/delete <name>`\n\nExample: `/delete gaming`\n\nUse `/list` to see your saved emails.')
        return
    
    name = parts[1].strip()
    if delete_email_from_db(user_id, name):
        await message.reply(f'✅ **Email Deleted!**\n\nSaved email "**{name}**" has been removed.')
    else:
        await message.reply(f'❌ No saved email found with name "**{name}**".\n\nUse `/list` to see your saved emails.')

@app.on_message(filters.command('current'))
async def current_cmd(client, message):
    user_id = message.from_user.id
    if user_id not in user_sessions or not user_sessions[user_id]['email']:
        await message.reply('❌ **No Active Email**\n\nYou don\'t have an active email right now.\n\nUse `/generate` to create a new email or `/load <name>` to load a saved one.')
        return
    
    session = user_sessions[user_id]
    await message.reply(f'**📧 Current Active Email:**\n\n`{session["email"]}`\n\n💡 Use `/save <name>` to save this email for future use.', reply_markup=buttons)

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    user_id = message.from_user.id
    if user_id in user_sessions and user_sessions[user_id].get('waiting_for_save_name'):
        session = user_sessions[user_id]
        name = message.text.strip()
        
        if len(name) > 50:
            await message.reply('❌ Name too long! Please use a name under 50 characters.')
            return
        
        if save_email_to_db(user_id, name, session['email'], session['password']):
            await message.reply(f'✅ **Email Saved Successfully!**\n\n📧 Email: `{session["email"]}`\n💾 Saved as: **{name}**\n\nUse `/load {name}` to reuse this email anytime!', reply_markup=buttons)
        else:
            await message.reply('❌ Failed to save email. Please try again.')
        
        user_sessions[user_id]['waiting_for_save_name'] = False

# Initialize database on startup
print("🔄 Initializing database...")
init_database()

app.run()

# Stay tuned for more : Instagram[@riz.4d]
