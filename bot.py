import base64
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import io
import random
import string
import requests
import json
import os
import urllib.parse
import re
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pymongo import MongoClient
import threading
from PIL import Image

# ================= KREDENTIALS =================
TOKEN = '8800996502:AAG3jcKM94hCPC1iwY3o5pV2puS5-Wm8VyI'
ADMIN_ID = "8691419913"
IMGBB_API_KEY = "YOUR_IMGBB_API_KEY_HERE"

# ================= MONGODB =================
MONGO_URI = "mongodb+srv://jihadarahata_db_user:jihadarahata_db_user@cluster0.yqzqslh.mongodb.net/?appName=Cluster0"
MONGO_DB_NAME = "telegram_bot"

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    mongo_db = mongo_client[MONGO_DB_NAME]
    mongo_collection = mongo_db["bot_data"]
    print("✅ MongoDB Connected!")
except Exception as e:
    print(f"❌ MongoDB Error: {e}")
    mongo_collection = None

# ================= FORCE SUB =================
FORCE_CHANNELS = [
    {"id": "-1004328566497", "link": "https://t.me/+ERxRWjTD_HYyNmVl", "name": "📢 Official"},
    {"id": "-1003855006043", "link": "https://t.me/+d-S6E1EUrBUwOTY1", "name": "📢 Backup"},
]
BACKUP_CHANNEL_ID = "-1003913034867"
BACKUP_CHANNEL_LINK = "https://t.me/+7hqmxlrvp7kyOTFl"

bot = telebot.TeleBot(TOKEN)

# ================= CONSTANTS =================
COIN_REWARD_REFERRAL = 10
COIN_REWARD_NEW_USER = 5
COIN_COST_OBFUSCATE = 5
COIN_COST_URL = 5
COIN_COST_IMAGE = 5
COIN_DAILY_BONUS = 5
LIVE_CHAT_COOLDOWN_SECONDS = 3600
PURCHASE_COOLDOWN_SECONDS = 3600

STREAK_REWARDS = {1:5,2:5,3:5,4:5,5:5,6:5,7:25}

COIN_PACKAGES = {
    "50":{"coins":50,"price":20},"100":{"coins":100,"price":35},
    "250":{"coins":250,"price":80},"500":{"coins":500,"price":150},
    "1000":{"coins":1000,"price":280},
}

DEFAULT_TEXTS = {
    "welcome": "═══════════════════════════\n🎉𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗧𝗢𝗟𝗟 𝗕𝗢𝗧🎉\n═══════════════════════════\n👑𝐀𝐋𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐓𝐎𝐋𝐋𝐒 𝐅𝐑𝐄𝐄👑\n\n☠️𝐀𝐋𝐋 𝐇𝐀𝐂𝐊'𝐒 𝐓𝐎𝐋𝐋 𝐅𝐑𝐄𝐄☠️\n\n🎁𝗔𝗟𝗟 𝗚𝗜𝗩𝗘𝗔𝗪𝗔𝗬 𝗢𝗡 𝗧𝗛𝗘 𝗕𝗢𝗧🎁\n\n⚠️𝗩𝗘𝗥𝗬 𝗜𝗠𝗣𝗢𝗥𝗧𝗔𝗡𝗧 𝗙𝗢𝗥 '𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘' 𝗩𝗜𝗗𝗘𝗢⚠️\n\n⬇️𝐂𝐋𝐈𝐂𝐊 𝐓𝐇𝐈𝐒 𝐁𝐔𝐓𝐓𝐎𝐍 𝐀𝐍𝐃 𝐖𝐀𝐓𝐂𝐇 𝐓𝐇𝐄 𝐕𝗜𝗗𝗘𝗢⬇️",
    "obf_prompt": "⚠️ <b>HTML Obfuscate</b>\n\n📄 <b>Send your .html file!</b>",
    "url_prompt": "📍 <b>URL to HTML</b>\n\n🎁 <b>Send a URL!</b>",
    "img_prompt": "📸 <b>Image to URL</b>\n\n<b>Send Your Image!</b>",
    "rename_prompt": "📝 <b>File Renamer</b>\n\n<b>Step 1:</b> ফাইল পাঠান"
}

def get_default_db():
    return {
        "_id": "main",
        "users": [], "activities": [], "bot_active": True,
        "saved_urls": [], "saved_files": [], "texts": DEFAULT_TEXTS,
        "stats": {"obf":0,"url":0,"img":0,"rename":0,"shorten":0,"b64":0,"passgen":0,"imgcomp":0,"conv":0},
        "coins": {}, "banned_users": [], "referrals": {},
        "referral_claimed": [], "referral_pending": {},
        "coin_history": {},
        "daily_bonus": {}, "pending_orders": {},
        "order_counter": 1000, "coin_packages": COIN_PACKAGES.copy(),
        "daily_streak": {}, "vouchers": {}, "voucher_history": {},
        "order_history": {}, "support_tickets": {}, "ticket_counter": 5000,
        "live_chat": {}, "user_profiles": {},
        "user_notes": {}, "ban_reasons": {},
        "live_chat_cooldown": {}, "purchase_cooldown": {},
        "how_to_use_link": "https://t.me/+ERxRWjTD_HYyNmVl",
        "bkash_number": "01631628306",
        "user_language": {}, "user_notifications": {},
        "recent_activity": {},
        "sub_admins": [],
        "milestone_sent": [],
        "promo_last_sent": "",
        "coin_settings": {
            "welcome_bonus":5,"referral_reward":10,
            "daily_bonus":5,"daily_milestone_7":25,
            "cost_obfuscate":5,"cost_url":5,"cost_image":5,
            "live_chat_cooldown":3600,"purchase_cooldown":3600,
        },
        "settings_updated": "",
    }

def load_db():
    if mongo_collection is None: return get_default_db()
    try:
        data = mongo_collection.find_one({"_id": "main"})
        if not data:
            default = get_default_db()
            mongo_collection.insert_one(default)
            return default
        default = get_default_db()
        for key in default:
            if key not in data: data[key] = default[key]
        return data
    except Exception as e:
        print(f"❌ Load Error: {e}")
        return get_default_db()

def save_db(data=None):
    global db
    if mongo_collection is None: return
    try:
        save_data = {k: v for k, v in (data or db).items() if k != "_id"}
        mongo_collection.update_one({"_id": "main"}, {"$set": save_data}, upsert=True)
    except Exception as e:
        print(f"❌ Save Error: {e}")

db = load_db()

if "coin_packages" in db and db["coin_packages"]:
    try:
        COIN_PACKAGES.clear(); COIN_PACKAGES.update(db["coin_packages"])
    except: pass

user_states = {}

# ================= COOLDOWN =================
def get_live_chat_cooldown_seconds():
    return db.get("coin_settings", {}).get("live_chat_cooldown", LIVE_CHAT_COOLDOWN_SECONDS)

def check_live_chat_cooldown(user_id):
    uid = str(user_id)
    cu = db.get("live_chat_cooldown", {}).get(uid)
    if not cu: return (True, 0)
    now = time.time()
    if now >= cu:
        if uid in db["live_chat_cooldown"]: del db["live_chat_cooldown"][uid]; save_db()
        return (True, 0)
    return (False, int(cu - now))

def set_live_chat_cooldown(user_id):
    uid = str(user_id); cs = get_live_chat_cooldown_seconds()
    if cs <= 0: return
    db["live_chat_cooldown"][uid] = time.time() + cs; save_db()

def reset_live_chat_cooldown(user_id):
    uid = str(user_id)
    if uid in db["live_chat_cooldown"]: del db["live_chat_cooldown"][uid]; save_db()

def get_purchase_cooldown_seconds():
    return db.get("coin_settings", {}).get("purchase_cooldown", PURCHASE_COOLDOWN_SECONDS)

def check_purchase_cooldown(user_id):
    uid = str(user_id)
    cu = db.get("purchase_cooldown", {}).get(uid)
    if not cu: return (True, 0)
    now = time.time()
    if now >= cu:
        if uid in db["purchase_cooldown"]: del db["purchase_cooldown"][uid]; save_db()
        return (True, 0)
    return (False, int(cu - now))

def set_purchase_cooldown(user_id):
    uid = str(user_id); cs = get_purchase_cooldown_seconds()
    if cs <= 0: return
    db["purchase_cooldown"][uid] = time.time() + cs; save_db()

def reset_purchase_cooldown(user_id):
    uid = str(user_id)
    if uid in db["purchase_cooldown"]: del db["purchase_cooldown"][uid]; save_db()

def format_remaining_time(seconds):
    if seconds < 60: return f"{seconds} সেকেন্ড"
    elif seconds < 3600: return f"{seconds//60} মিনিট {seconds%60} সেকেন্ড"
    else: return f"{seconds//3600} ঘণ্টা {(seconds%3600)//60} মিনিট"

# ================= AUTO-DELETE =================
temp_messages = {}

def send_temp_reply(message, text, **kwargs):
    try:
        msg = bot.reply_to(message, text, **kwargs)
        cid = message.chat.id
        if cid not in temp_messages: temp_messages[cid] = []
        temp_messages[cid].append(msg.message_id)
        return msg
    except: return None

def clear_temp(chat_id):
    if chat_id not in temp_messages: return
    for mid in temp_messages[chat_id]:
        try: bot.delete_message(chat_id, mid)
        except: pass
    temp_messages[chat_id] = []

# ================= KEYBOARDS =================
def get_page1_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, input_field_placeholder="একটা অপশন বেছে নিন...")
    kb.row(KeyboardButton("🌐 Render URL"), KeyboardButton("🔒 Obfuscate"))
    kb.row(KeyboardButton("📸 Image to URL"), KeyboardButton("💰 My Coins"))
    kb.row(KeyboardButton("🎁 Refer & Earn"), KeyboardButton("⏰ Daily Bonus"))
    kb.row(KeyboardButton("➡️ More Options"))
    return kb

def get_page2_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, input_field_placeholder="একটা অপশন বেছে নিন...")
    kb.row(KeyboardButton("💳 Buy Coins"), KeyboardButton("🎟️ Voucher"))
    kb.row(KeyboardButton("📝 File Renamer"), KeyboardButton("👤 Profile"))
    kb.row(KeyboardButton("📜 Orders"), KeyboardButton("📊 My Stats"))
    kb.row(KeyboardButton("🔗 URL Shortener"), KeyboardButton("🔐 Base64"))
    kb.row(KeyboardButton("🔑 Password Gen"), KeyboardButton("🖼️ Image Compressor"))
    kb.row(KeyboardButton("🔄 Format Convert"), KeyboardButton("🔗 Share Bot"))
    kb.row(KeyboardButton("🆘 Support"), KeyboardButton("⬅️ Back"))
    return kb

def get_main_keyboard():
    return get_page1_keyboard()

# ================= DYNAMIC SETTINGS =================
def get_coin_setting(key, default=0):
    return db.get("coin_settings", {}).get(key, default)

def set_coin_setting(key, value):
    if "coin_settings" not in db: db["coin_settings"] = {}
    db["coin_settings"][key] = value
    db["settings_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_db()

def refresh_coin_constants():
    global COIN_REWARD_REFERRAL, COIN_REWARD_NEW_USER, COIN_COST_OBFUSCATE
    global COIN_COST_URL, COIN_COST_IMAGE, COIN_DAILY_BONUS, STREAK_REWARDS
    global LIVE_CHAT_COOLDOWN_SECONDS, PURCHASE_COOLDOWN_SECONDS
    COIN_REWARD_NEW_USER = get_coin_setting("welcome_bonus", 5)
    COIN_REWARD_REFERRAL = get_coin_setting("referral_reward", 10)
    COIN_DAILY_BONUS = get_coin_setting("daily_bonus", 5)
    COIN_COST_OBFUSCATE = get_coin_setting("cost_obfuscate", 5)
    COIN_COST_URL = get_coin_setting("cost_url", 5)
    COIN_COST_IMAGE = get_coin_setting("cost_image", 5)
    LIVE_CHAT_COOLDOWN_SECONDS = get_coin_setting("live_chat_cooldown", 3600)
    PURCHASE_COOLDOWN_SECONDS = get_coin_setting("purchase_cooldown", 3600)
    dbn = get_coin_setting("daily_bonus", 5)
    ms = get_coin_setting("daily_milestone_7", 25)
    STREAK_REWARDS = {1:dbn,2:dbn,3:dbn,4:dbn,5:dbn,6:dbn,7:ms}

refresh_coin_constants()

# ================= HELPERS =================
def get_bkash_number():
    return db.get("bkash_number", "01631628306")

def add_user(user_id):
    if str(user_id) not in db['users']:
        db['users'].append(str(user_id))
        if str(user_id) not in db["user_profiles"]:
            db["user_profiles"][str(user_id)] = {
                "joined": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total_obf":0,"total_url":0,"total_img":0,"total_rename":0,
                "total_referrals":0,"total_spent":0,
            }
        save_db()

def log_activity(user_id, action):
    tn = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db['activities'].append(f"[{tn}] UID: {user_id} -> {action}")
    if len(db['activities']) > 50: db['activities'] = db['activities'][-50:]
    # Recent Activity for user
    uid = str(user_id)
    if uid not in db.get("recent_activity", {}): db["recent_activity"][uid] = []
    db["recent_activity"][uid].append(f"[{datetime.now().strftime('%m-%d %H:%M')}] {action}")
    db["recent_activity"][uid] = db["recent_activity"][uid][-20:]
    save_db()

def get_coins(user_id):
    return db["coins"].get(str(user_id), 0)

def add_coins(user_id, amount, reason="Manual"):
    uid = str(user_id)
    db["coins"][uid] = db["coins"].get(uid, 0) + amount
    if uid not in db["coin_history"]: db["coin_history"][uid] = []
    db["coin_history"][uid].append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "amount": amount, "reason": reason, "balance": db["coins"][uid]})
    db["coin_history"][uid] = db["coin_history"][uid][-30:]
    save_db()
    return db["coins"][uid]

def deduct_coins(user_id, amount, reason="Usage"):
    uid = str(user_id)
    cur = db["coins"].get(uid, 0)
    if cur < amount: return False
    db["coins"][uid] = cur - amount
    if uid not in db["coin_history"]: db["coin_history"][uid] = []
    db["coin_history"][uid].append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "amount": -amount, "reason": reason, "balance": db["coins"][uid]})
    db["coin_history"][uid] = db["coin_history"][uid][-30:]
    save_db()
    return True

def is_banned(user_id):
    return str(user_id) in db.get("banned_users", [])

def ban_user(user_id, reason="Not specified"):
    uid = str(user_id)
    if uid not in db["banned_users"]:
        db["banned_users"].append(uid); db["ban_reasons"][uid] = reason; save_db()

def unban_user(user_id):
    uid = str(user_id)
    if uid in db["banned_users"]:
        db["banned_users"].remove(uid)
        if uid in db["ban_reasons"]: del db["ban_reasons"][uid]
        save_db()

def check_banned(chat_id):
    if is_banned(chat_id):
        reason = db["ban_reasons"].get(str(chat_id), "Not specified")
        bot.send_message(chat_id, f"🚫 <b>Banned!</b>\n\n📝 কারণ: {reason}", parse_mode="HTML")
        return True
    return False

# ================= FORCE SUB =================
def check_channel_membership(user_id, channel_id):
    try:
        status = bot.get_chat_member(channel_id, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"[FORCE SUB] {channel_id}: {e}")
        return False

def is_subscribed(user_id):
    if str(user_id) == ADMIN_ID: return True
    for ch in FORCE_CHANNELS:
        if not check_channel_membership(user_id, ch["id"]): return False
    return True

def get_missing_channels(user_id):
    if str(user_id) == ADMIN_ID: return []
    missing = []
    for ch in FORCE_CHANNELS:
        if not check_channel_membership(user_id, ch["id"]): missing.append(ch)
    return missing

def check_force_sub(chat_id):
    if not is_subscribed(chat_id):
        missing = get_missing_channels(chat_id)
        markup = InlineKeyboardMarkup(row_width=1)
        text = "⚠️ <b>Access Denied!</b>\n\n🔒 এই বট ব্যবহার করতে হলে <b>সব চ্যানেলে</b> join করতে হবে:\n\n"
        for ch in FORCE_CHANNELS:
            ij = not any(m["id"] == ch["id"] for m in missing)
            text += f"{'✅' if ij else '❌'} <b>{ch['name']}</b>\n"
            if not ij:
                markup.add(InlineKeyboardButton(f"📢 Join {ch['name']}", url=ch["link"]))
        text += "\n👇 সবগুলোতে join করার পর <b>✅ Check</b> চাপুন"
        markup.add(InlineKeyboardButton("✅ Check", callback_data="check_sub"))
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
        return False
    return True

# ================= REFERRAL =================
def try_claim_referral_bonus(user_id):
    uid = str(user_id)
    if uid not in db['referrals']: return False
    if uid in db['referral_claimed']: return False
    if not is_subscribed(uid):
        db["referral_pending"][uid] = {"referrer": db['referrals'][uid], "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
        save_db()
        return False
    referrer = db['referrals'][uid]
    if referrer == uid: return False
    add_coins(referrer, COIN_REWARD_REFERRAL, f"Referral: {uid}")
    db['referral_claimed'].append(uid)
    if uid in db["referral_pending"]: del db["referral_pending"][uid]
    if referrer in db["user_profiles"]:
        db["user_profiles"][referrer]["total_referrals"] = db["user_profiles"][referrer].get("total_referrals", 0) + 1
    save_db()
    try:
        bot.send_message(int(referrer), f"🎉 <b>Referral Verified!</b>\n\n💰 <b>+{COIN_REWARD_REFERRAL}</b>\n💵 <b>{get_coins(referrer)}</b>", parse_mode="HTML")
    except: pass
    return True

# ================= BACKUP =================
def get_user_display(user_id, fn=None, un=None):
    name = fn or "Unknown"
    uname = f"@{un}" if un else "No Username"
    return f"<a href='tg://user?id={user_id}'>{name}</a> ({uname})"

def send_backup_file(user_id, fb, fname, cat, extra="", fn=None, un=None):
    if not BACKUP_CHANNEL_ID: return False
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cap = f"📦 <b>#{cat}</b>\n━━━━━━━━━━━━━━━━━━━━\n👤 <b>User:</b> {get_user_display(user_id, fn, un)}\n🆔 <b>ID:</b> <code>{user_id}</code>\n📁 <b>File:</b> <code>{fname}</code>\n📊 <b>Size:</b> {len(fb.getvalue())/1024:.1f} KB\n"
        if extra: cap += f"\n{extra}\n"
        cap += f"\n🕐 <b>Time:</b> {now}"
        fb.seek(0)
        bot.send_document(BACKUP_CHANNEL_ID, fb, caption=cap, parse_mode="HTML")
        return True
    except: return False

def send_backup_photo(user_id, pb, capt, cat, fn=None, un=None):
    if not BACKUP_CHANNEL_ID: return False
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cap = f"📸 <b>#{cat}</b>\n━━━━━━━━━━━━━━━━━━━━\n👤 <b>User:</b> {get_user_display(user_id, fn, un)}\n🆔 <b>ID:</b> <code>{user_id}</code>\n\n{capt}\n\n🕐 <b>Time:</b> {now}"
        pb.seek(0)
        bot.send_photo(BACKUP_CHANNEL_ID, pb, caption=cap, parse_mode="HTML")
        return True
    except: return False

def send_backup_text(user_id, title, content, cat, fn=None, un=None):
    if not BACKUP_CHANNEL_ID: return False
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"📝 <b>#{cat}</b>\n━━━━━━━━━━━━━━━━━━━━\n👤 <b>User:</b> {get_user_display(user_id, fn, un)}\n🆔 <b>ID:</b> <code>{user_id}</code>\n\n<b>{title}</b>\n{content}\n\n🕐 <b>Time:</b> {now}"
        bot.send_message(BACKUP_CHANNEL_ID, msg, parse_mode="HTML", disable_web_page_preview=True)
        return True
    except: return False

def format_file_size(b):
    if b < 1024: return f"{b} B"
    if b < 1024*1024: return f"{b/1024:.2f} KB"
    if b < 1024*1024*1024: return f"{b/(1024*1024):.2f} MB"
    return f"{b/(1024*1024*1024):.2f} GB"

# ================= NEW FEATURES =================

def shorten_url(long_url):
    try:
        r = requests.get(f"https://tinyurl.com/api-create.php?url={long_url}", timeout=10)
        if r.status_code == 200 and r.text.startswith("http"):
            return r.text.strip()
        return None
    except: return None

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(chars, k=length))

def get_personal_stats(user_id):
    uid = str(user_id)
    p = db["user_profiles"].get(uid, {})
    total_refs = sum(1 for k in db['referral_claimed'] if db['referrals'].get(k) == uid)
    pending_refs = sum(1 for k in db['referral_pending'] if db['referral_pending'][k].get("referrer") == uid)
    orders = db["order_history"].get(uid, [])
    approved = sum(1 for o in orders if o["status"] == "approved")
    pending = sum(1 for o in orders if o["status"] == "pending")
    total_spent = sum(o["price"] for o in orders if o["status"] == "approved")
    return (
        f"📊 <b>Your Statistics</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>ID:</b> <code>{user_id}</code>\n"
        f"📅 <b>Joined:</b> {p.get('joined', 'N/A')}\n\n"
        f"💰 <b>Balance:</b> {get_coins(user_id)} coins\n\n"
        f"🎁 <b>Referrals:</b>\n   ✅ Successful: <b>{total_refs}</b>\n   ⏳ Pending: <b>{pending_refs}</b>\n\n"
        f"🔄 <b>Operations:</b>\n"
        f"   Obfuscate: <b>{p.get('total_obf', 0)}</b>\n"
        f"   URL Fetch: <b>{p.get('total_url', 0)}</b>\n"
        f"   Image to URL: <b>{p.get('total_img', 0)}</b>\n"
        f"   File Renamed: <b>{p.get('total_rename', 0)}</b>\n\n"
        f"💳 <b>Orders:</b>\n"
        f"   ✅ Approved: <b>{approved}</b>\n"
        f"   ⏳ Pending: <b>{pending}</b>\n"
        f"   💵 Spent: <b>৳{total_spent}</b>"
    )

def get_order_history(user_id):
    uid = str(user_id)
    orders = db["order_history"].get(uid, [])
    if not orders: return None
    text = "📜 <b>Your Order History</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for o in orders[-15:]:
        e = {"approved":"✅","pending":"⏳","rejected":"❌"}.get(o["status"],"❔")
        text += f"{e} <b>{o['order_id']}</b>\n   💰 {o['coins']} coins | 💵 ৳{o['price']}\n   📱 {o['method'].upper()} | {o['time']}\n\n"
    text += f"<i>মোট {len(orders)} টি অর্ডার</i>"
    return text

def get_referral_list(user_id):
    uid = str(user_id)
    text = "🎁 <b>Your Referrals</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
    confirmed = [k for k in db['referral_claimed'] if db['referrals'].get(k) == uid]
    pending = [k for k in db['referral_pending'] if db['referral_pending'][k].get("referrer") == uid]
    text += f"✅ <b>Confirmed ({len(confirmed)}):</b>\n"
    if confirmed:
        for u in confirmed[-10:]: text += f"   • <code>{u}</code>\n"
    else: text += "   <i>এখনো কেউ নেই</i>\n"
    text += f"\n⏳ <b>Pending ({len(pending)}):</b>\n"
    if pending:
        for u in pending[-10:]: text += f"   • <code>{u}</code>\n"
    else: text += "   <i>এখনো কেউ নেই</i>\n"
    text += f"\n💰 <b>Total Earned:</b> {len(confirmed) * COIN_REWARD_REFERRAL} coins"
    return text

def get_recent_activity(user_id):
    uid = str(user_id)
    acts = db.get("recent_activity", {}).get(uid, [])
    if not acts: return "📌 <b>Recent Activity</b>\n\n<i>কোনো activity নেই।</i>"
    text = "📌 <b>Recent Activity</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for a in acts[-15:]: text += f"• {a}\n"
    return text

def compress_image(image_bytes, quality=50, max_width=1200):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        out = io.BytesIO()
        if img.mode in ('RGBA', 'P'): img = img.convert('RGB')
        img.save(out, format='JPEG', quality=quality, optimize=True)
        out.seek(0)
        return out
    except Exception as e:
        print(f"[IMG COMPRESS] {e}")
        return None

def convert_image_format(image_bytes, target_format):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        out = io.BytesIO()
        fmt = target_format.upper()
        if fmt == 'JPG': fmt = 'JPEG'
        if fmt in ('JPEG', 'JPG') and img.mode in ('RGBA','P'): img = img.convert('RGB')
        img.save(out, format=fmt)
        out.seek(0)
        return out
    except Exception as e:
        print(f"[CONVERT] {e}")
        return None

def check_milestone():
    count = len(db["users"])
    milestones = [100, 500, 1000, 5000, 10000, 50000, 100000]
    for m in milestones:
        if count >= m and m not in db.get("milestone_sent", []):
            db.setdefault("milestone_sent", []).append(m)
            save_db()
            return m
    return None

# ================= DAILY STREAK =================
def get_streak_info(user_id):
    uid = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    info = db["daily_streak"].get(uid)
    if not info: return {"streak":0,"can_claim":True,"next_reward":COIN_DAILY_BONUS}
    ld = info.get("last_date"); st = info.get("streak", 0)
    if ld == today: return {"streak":st,"can_claim":False,"next_reward":0}
    ns = st + 1 if ld == yesterday else 1
    if ns > 7: ns = 1
    return {"streak":ns,"can_claim":True,"next_reward":STREAK_REWARDS.get(ns, COIN_DAILY_BONUS)}

def claim_daily_bonus_streak(user_id):
    uid = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    info = db["daily_streak"].get(uid, {})
    ld = info.get("last_date"); st = info.get("streak", 0)
    if ld == today: return None
    ns = st + 1 if ld == yesterday else 1
    if ns > 7: ns = 1
    reward = STREAK_REWARDS.get(ns, COIN_DAILY_BONUS)
    add_coins(uid, reward, f"Daily Bonus (Day {ns})")
    db["daily_streak"][uid] = {"streak": ns, "last_date": today}
    save_db()
    return {"streak":ns,"reward":reward,"is_milestone":ns==7}

def get_streak_text(user_id):
    info = get_streak_info(user_id)
    cs = info["streak"]; cc = info["can_claim"]
    cal = ""
    for day in range(1, 8):
        if day < cs: cal += f"✅ Day {day}: {STREAK_REWARDS.get(day, 5)}💰\n"
        elif day == cs and cc: cal += f"🎁 Day {day}: {STREAK_REWARDS.get(day, 5)}💰 ← এখানে\n"
        elif day == cs: cal += f"✅ Day {day}: {STREAK_REWARDS.get(day, 5)}💰 (আজ)\n"
        else: cal += f"⬜ Day {day}: {STREAK_REWARDS.get(day, 5)}💰\n"
    return f"⏰ <b>Daily Bonus Streak</b>\n\n🔥 Streak: <b>{cs}/7</b>\n\n📅 <b>Calendar:</b>\n{cal}", cc

# ================= VOUCHER =================
def generate_voucher_code(prefix="GIFT"):
    while True:
        rp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        code = f"{prefix}{rp}"
        if code not in db["vouchers"]: return code

def create_voucher(coins, mu=1, ed=None):
    code = generate_voucher_code()
    exp = (datetime.now() + timedelta(days=ed)).strftime("%Y-%m-%d %H:%M") if ed else None
    db["vouchers"][code] = {"coins": coins, "used_by": [], "max_uses": mu, "expires": exp, "created": datetime.now().strftime("%Y-%m-%d %H:%M")}
    save_db()
    return code

def redeem_voucher(user_id, code):
    uid = str(user_id); code = code.strip().upper()
    v = db["vouchers"].get(code)
    if not v: return {"success":False,"msg":"❌ সঠিক কোড নয়।"}
    if v.get("expires"):
        try:
            if datetime.now() > datetime.strptime(v["expires"], "%Y-%m-%d %H:%M"):
                return {"success":False,"msg":"⏰ মেয়াদ শেষ।"}
        except: pass
    if uid in v["used_by"]: return {"success":False,"msg":"⚠️ আপনি ব্যবহার করেছেন।"}
    if len(v["used_by"]) >= v["max_uses"]: return {"success":False,"msg":"❌ সর্বোচ্চ ব্যবহার শেষ।"}
    add_coins(uid, v["coins"], f"Voucher: {code}")
    v["used_by"].append(uid)
    if uid not in db["voucher_history"]: db["voucher_history"][uid] = []
    db["voucher_history"][uid].append(code)
    save_db()
    return {"success":True,"msg":f"🎉 <b>Voucher!</b>\n\n💰 +{v['coins']}\n💵 <b>{get_coins(uid)}</b>"}

# ================= ORDER =================
def add_order_to_history(user_id, oid, coins, price, method, status="pending"):
    uid = str(user_id)
    if uid not in db["order_history"]: db["order_history"][uid] = []
    db["order_history"][uid].append({"order_id":oid,"coins":coins,"price":price,"method":method,"status":status,"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
    db["order_history"][uid] = db["order_history"][uid][-50:]
    save_db()

def update_order_status(user_id, oid, ns):
    uid = str(user_id)
    if uid in db["order_history"]:
        for o in db["order_history"][uid]:
            if o["order_id"] == oid: o["status"] = ns
        save_db()

# ================= SUPPORT =================
def create_ticket(user_id, msg):
    tid = f"TKT{db['ticket_counter']}"
    db["ticket_counter"] += 1
    db["support_tickets"][tid] = {"uid":str(user_id),"msg":msg,"status":"open","time":datetime.now().strftime("%Y-%m-%d %H:%M"),"replies":[]}
    save_db()
    return tid

def add_chat_message(user_id, fw, msg):
    uid = str(user_id)
    if uid not in db["live_chat"]: db["live_chat"][uid] = []
    db["live_chat"][uid].append({"from":fw,"msg":msg,"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
    db["live_chat"][uid] = db["live_chat"][uid][-50:]
    save_db()

# ================= OBFUSCATION =================
def mask_scripts(hc):
    def ps(m):
        st,sc,se = m.group(1),m.group(2),m.group(3)
        if 'src=' in st.lower() or not sc.strip(): return m.group(0)
        b64 = base64.b64encode(sc.encode('utf-8')).decode('utf-8')
        return f"{st}\neval(decodeURIComponent(escape(atob('{b64}'))));\n{se}"
    return re.sub(r'(<script[^>]*>)(.*?)(</script>)', ps, hc, flags=re.IGNORECASE | re.DOTALL)

def rc4_crypt_bytes(data, key):
    S = list(range(256)); j = 0; out = bytearray()
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    for c in data:
        i = (i + 1) % 256; j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(c ^ S[(S[i] + S[j]) % 256])
    return out

def hardcore_hex_obfuscate(hc):
    hc = mask_scripts(hc)
    b64 = base64.b64encode(urllib.parse.quote(hc).encode('utf-8'))
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    cipher = rc4_crypt_bytes(b64, key.encode('utf-8'))
    arr = ",".join(map(str, [ord(c) for c in cipher.hex()]))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ci = f"\n╔══════════════════════════════════════════════════════════╗\n║  🔒 PROTECTED HTML - DO NOT MODIFY 🔒                    ║\n║  Obfuscated By: @HTML_SECURE_BOT                         ║\n║  Timestamp: {ts}                    ║\n║  Signature: DXF PROTECTOR [TOKEN: {key}]             ║\n╚══════════════════════════════════════════════════════════╝"
    hc_c = f"<!--{ci}\n-->"
    exp = re.sub(r'\s+', '', ci)
    djs = f"""
document.addEventListener('contextmenu', e => e.preventDefault());
document.onkeydown = function(e){{ if(e.keyCode==123) return false;
if(e.ctrlKey && e.shiftKey && e.keyCode=='I'.charCodeAt(0)) return false;
if(e.ctrlKey && e.shiftKey && e.keyCode=='C'.charCodeAt(0)) return false;
if(e.ctrlKey && e.shiftKey && e.keyCode=='J'.charCodeAt(0)) return false;
if(e.ctrlKey && e.keyCode=='U'.charCodeAt(0)) return false; }};
setInterval(function(){{debugger;}}, 50); console.clear();
var _s=false, _k="";
var _it = document.createTreeWalker(document, 128, null, false);
var _nd; var _exp = "{exp}";
while ((_nd = _it.nextNode())) {{
  var _v = _nd.nodeValue;
  if (_v.indexOf('PROTECTED HTML') !== -1) {{
    if (_v.replace(/\\s+/g,'') === _exp) {{
      var _i = _v.indexOf('[TOKEN: ');
      if (_i !== -1) {{ _k = _v.substring(_i+8, _i+24); _s=true; break; }}
    }}
  }}
}}
if (!_s || _k.length !== 16) {{
  document.write('<h1 style="color:red;text-align:center;">🚨 TAMPER DETECTED!</h1>');
  while(true) {{ debugger; }} return;
}}
function _R(k,s){{ var _s=[],j=0,x,r='';
for(var i=0;i<256;i++)_s[i]=i;
for(i=0;i<256;i++){{j=(j+_s[i]+k.charCodeAt(i%k.length))%256;x=_s[i];_s[i]=_s[j];_s[j]=x;}}
i=0;j=0;
for(var y=0;y<s.length;y++){{i=(i+1)%256;j=(j+_s[i])%256;x=_s[i];_s[i]=_s[j];_s[j]=x;r+=String.fromCharCode(s.charCodeAt(y)^_s[(_s[i]+_s[j])%256]);}}
return r; }}
var _A = [{arr}]; var _h = '';
for(var i=0;i<_A.length;i++)_h+=String.fromCharCode(_A[i]);
var _c = ''; for(var i=0;i<_h.length;i+=2)_c+=String.fromCharCode(parseInt(_h.substr(i,2),16));
var _b = _R(_k, _c);
try {{ var _f = decodeURIComponent(atob(_b)); document.open(); document.write(_f); document.close(); }}
catch(e) {{ document.write('<h1 style="color:red;">🚨 ERROR!</h1>'); }}"""
    enc = base64.b64encode(djs.encode('utf-8')).decode('utf-8')
    chunk = len(enc)//2
    p1, p2 = enc[:chunk], enc[chunk:]
    return f"""{hc_c}
<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body oncontextmenu="return false;">
<script>
(function(){{
  var _p = decodeURIComponent(escape(atob('{p1}' + '{p2}')));
  new Function(_p)();
}})();
</script>
<noscript>⚠️ Enable JavaScript.</noscript>
</body></html>"""

# ================= MAIN MENU =================
def send_main_menu(chat_id, reply_to_message=None):
    text = db["texts"]["welcome"]
    inline_mk = InlineKeyboardMarkup()
    inline_mk.add(InlineKeyboardButton("📖 𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 📖", callback_data="how_to_use"))
    if reply_to_message:
        try:
            bot.reply_to(reply_to_message, text, reply_markup=get_page1_keyboard(), parse_mode="HTML")
            bot.send_message(chat_id, "⬇️ <b>নিচের বাটনে ক্লিক করুন</b> ⬇️", reply_markup=inline_mk, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=get_page1_keyboard(), parse_mode="HTML")
            bot.send_message(chat_id, "⬇️ <b>নিচের বাটনে ক্লিক করুন</b> ⬇️", reply_markup=inline_mk, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=get_page1_keyboard(), parse_mode="HTML")
        bot.send_message(chat_id, "⬇️ <b>নিচের বাটনে ক্লিক করুন</b> ⬇️", reply_markup=inline_mk, parse_mode="HTML")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id; user_id = str(chat_id)
    if check_banned(chat_id): return
    ref_id = None
    if len(message.text.split()) > 1:
        arg = message.text.split()[1]
        if arg.startswith("ref_"):
            rid = arg.replace("ref_", "")
            if rid != user_id and rid.isdigit(): ref_id = rid
    is_new = user_id not in db['users']
    if is_new:
        add_user(user_id)
        add_coins(user_id, COIN_REWARD_NEW_USER, "Welcome Bonus")
        if ref_id and ref_id in db['users']:
            db['referrals'][user_id] = ref_id; save_db()
    log_activity(chat_id, "Started Bot")
    user_states[chat_id] = ""
    if not db['bot_active'] and str(chat_id) != ADMIN_ID:
        bot.reply_to(message, "🛠️ Maintenance!", reply_markup=get_page1_keyboard()); return
    if not check_force_sub(chat_id): return
    try_claim_referral_bonus(chat_id)
    send_main_menu(chat_id, reply_to_message=message)

@bot.message_handler(commands=['menu'])
def show_menu(message):
    if check_banned(message.chat.id): return
    if not check_force_sub(message.chat.id): return
    bot.reply_to(message, "🏠 Menu", reply_markup=get_page1_keyboard(), parse_mode="HTML")

@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    user_states[message.chat.id] = ""
    bot.reply_to(message, "❌ বাতিল।", reply_markup=get_page1_keyboard())

@bot.message_handler(commands=['setcooldown'])
def set_cooldown_cmd(message):
    if str(message.chat.id) != ADMIN_ID: return
    try:
        m = int(message.text.split()[1])
        set_coin_setting("live_chat_cooldown", m * 60); refresh_coin_constants()
        bot.reply_to(message, f"✅ Live Chat Cooldown: {m} মিনিট" if m > 0 else "✅ বন্ধ")
    except: bot.reply_to(message, "❌ /setcooldown minutes")

@bot.message_handler(commands=['setpurchasecooldown'])
def set_pur_cmd(message):
    if str(message.chat.id) != ADMIN_ID: return
    try:
        m = int(message.text.split()[1])
        set_coin_setting("purchase_cooldown", m * 60); refresh_coin_constants()
        bot.reply_to(message, f"✅ Purchase Cooldown: {m} মিনিট" if m > 0 else "✅ বন্ধ")
    except: bot.reply_to(message, "❌ /setpurchasecooldown minutes")

@bot.message_handler(commands=['sethowtouse'])
def set_how_cmd(message):
    if str(message.chat.id) != ADMIN_ID: return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "❌ /sethowtouse [link]", parse_mode="HTML"); return
        nl = parts[1].strip()
        if not nl.startswith("http"): nl = "https://" + nl
        old = db.get("how_to_use_link", "")
        db["how_to_use_link"] = nl; save_db()
        bot.reply_to(message, f"✅ Link Updated!\n❌ Old: <code>{old}</code>\n✅ New: <code>{nl}</code>", parse_mode="HTML")
    except: bot.reply_to(message, "❌ Error")

@bot.message_handler(commands=['setbkash'])
def set_bkash_cmd(message):
    if str(message.chat.id) != ADMIN_ID: return
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "❌ /setbkash 01631628306", parse_mode="HTML"); return
        nn = parts[1].strip().replace(" ", "").replace("-", "")
        if not nn.isdigit() or len(nn) != 11:
            bot.reply_to(message, "❌ ১১ digit নাম্বার দিন।"); return
        old = db.get("bkash_number", "")
        db["bkash_number"] = nn; save_db()
        bot.reply_to(message, f"✅ bKash Updated!\n❌ Old: <code>{old}</code>\n✅ New: <code>{nn}</code>", parse_mode="HTML")
    except: bot.reply_to(message, "❌ Error")

# ================= ADMIN PANEL =================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.chat.id) != ADMIN_ID: return
    user_states[message.chat.id] = ""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("👥 Users", callback_data="admin_view_users"), InlineKeyboardButton("📝 Logs", callback_data="admin_view_logs"))
    markup.add(InlineKeyboardButton("🌐 URLs", callback_data="admin_view_urls"), InlineKeyboardButton("📁 Files", callback_data="admin_view_files"))
    markup.add(InlineKeyboardButton("📣 Broadcast", callback_data="admin_broadcast"))
    markup.add(InlineKeyboardButton("✏️ Edit Texts", callback_data="admin_edit_texts"))
    markup.add(InlineKeyboardButton("💰 Coin Settings", callback_data="admin_coin_settings"))
    markup.add(InlineKeyboardButton("💰 Manage Coins", callback_data="admin_coins"), InlineKeyboardButton("🚫 Ban/Unban", callback_data="admin_ban"))
    markup.add(InlineKeyboardButton("👥 All Coins", callback_data="admin_all_coins"))
    markup.add(InlineKeyboardButton("🎁 Give All", callback_data="admin_giveall_info"))
    markup.add(InlineKeyboardButton("💳 Orders", callback_data="admin_orders"), InlineKeyboardButton("📦 Prices", callback_data="admin_edit_prices"))
    markup.add(InlineKeyboardButton("🎟️ Vouchers", callback_data="admin_vouchers"))
    markup.add(InlineKeyboardButton("🆘 Tickets", callback_data="admin_tickets"), InlineKeyboardButton("💬 Chats", callback_data="admin_chats"))
    markup.add(InlineKeyboardButton("⏱️ Chat Cooldown", callback_data="admin_cooldown_settings"))
    markup.add(InlineKeyboardButton("⏱️ Purchase Cooldown", callback_data="admin_purchase_cooldown"))
    markup.add(InlineKeyboardButton("📖 How To Use", callback_data="admin_how_to_use_settings"))
    markup.add(InlineKeyboardButton("💳 bKash Number", callback_data="admin_bkash_settings"))
    markup.add(InlineKeyboardButton("👑 Sub-Admins", callback_data="admin_sub_admins"))
    markup.add(InlineKeyboardButton("📢 Send Promo", callback_data="admin_send_promo"))
    markup.add(InlineKeyboardButton("❓ ADMIN HELP", callback_data="admin_help_main"))
    markup.add(InlineKeyboardButton("🔴 OFF", callback_data="admin_off"), InlineKeyboardButton("🟢 ON", callback_data="admin_on"))
    bot.reply_to(message, "🛡️ <b>ADMIN PANEL</b>", reply_markup=markup, parse_mode="HTML")

# ================= CALLBACKS =================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "check_sub":
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ Verified!")
            try: bot.delete_message(chat_id, call.message.message_id)
            except: pass
            try_claim_referral_bonus(chat_id)
            send_main_menu(chat_id)
        else:
            missing = get_missing_channels(call.from_user.id)
            bot.answer_callback_query(call.id, f"❌ {len(missing)}টি চ্যানেলে join করেননি!", show_alert=True)
            try: bot.delete_message(chat_id, call.message.message_id)
            except: pass
            check_force_sub(chat_id)
        return

    if call.data == "how_to_use":
        bot.answer_callback_query(call.id)
        link = db.get("how_to_use_link", "https://t.me/+ERxRWjTD_HYyNmVl")
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🎬 𝗪𝗔𝗧𝗖𝗛 𝗩𝗜𝗗𝗘𝗢 𝗡𝗢𝗪 🎬", url=link))
        bot.send_message(chat_id, "📖 <b>𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘</b>\n━━━━━━━━━━━━━━━━━━━━\n\n🎬 নিচের বাটনে ক্লিক করে Video দেখুন", reply_markup=mk, parse_mode="HTML")
        return

    bot.answer_callback_query(call.id)

    # ===== ADMIN HELP =====
    if call.data == "admin_help_main":
        if str(chat_id) != ADMIN_ID: return
        help_keys = [
            ("👥 Users", "admin_view_users"), ("📝 Logs", "admin_view_logs"),
            ("🌐 URLs", "admin_view_urls"), ("📁 Files", "admin_view_files"),
            ("📣 Broadcast", "admin_broadcast"), ("✏️ Texts", "admin_edit_texts"),
            ("💰 Settings", "admin_coin_settings"), ("💰 Coins", "admin_coins"),
            ("🚫 Ban", "admin_ban"), ("👥 All Coins", "admin_all_coins"),
            ("🎁 Give All", "admin_giveall_info"), ("💳 Orders", "admin_orders"),
            ("📦 Prices", "admin_edit_prices"), ("🎟️ Vouchers", "admin_vouchers"),
            ("🆘 Tickets", "admin_tickets"), ("💬 Chats", "admin_chats"),
            ("⏱️ Chat CD", "admin_cooldown_settings"), ("⏱️ Pur CD", "admin_purchase_cooldown"),
            ("📖 Link", "admin_how_to_use_settings"), ("💳 bKash", "admin_bkash_settings"),
            ("👑 Sub-Admins", "admin_sub_admins"), ("📢 Promo", "admin_send_promo"),
        ]
        mk = InlineKeyboardMarkup(row_width=2)
        for label, key in help_keys:
            mk.add(InlineKeyboardButton(label, callback_data=f"help_show_{key}"))
        mk.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back_to_panel"))
        bot.send_message(chat_id, "📖 <b>ADMIN HELP</b>\n\nকোন বাটন সম্পর্কে জানতে ক্লিক করুন:", reply_markup=mk, parse_mode="HTML")
        return

    if call.data.startswith("help_show_"):
        if str(chat_id) != ADMIN_ID: return
        key = call.data.replace("help_show_", "")
        help_texts = {
            "admin_view_users": ("👥 View Users", "মোট ইউজার ও ব্যান সংখ্যা।", "ক্লিক করুন।", "👥 1250 | 🚫 12"),
            "admin_view_logs": ("📝 Live Logs", "সাম্প্রতিক activity।", "ক্লিক করুন।", "[01-15] UID: 123456 → Started"),
            "admin_view_urls": ("🌐 URLs", "সাম্প্রতিক fetched URL।", "ক্লিক করুন।", "[01-15] UID: 123 → example.com"),
            "admin_view_files": ("📁 Files", "সাম্প্রতিক obfuscated file।", "ক্লিক করুন।", "📅 time / 👤 user"),
            "admin_broadcast": ("📣 Broadcast", "সবাইকে message।", "Message পাঠান।", "🎉 নতুন অফার!"),
            "admin_edit_texts": ("✏️ Edit Texts", "Bot এর text পরিবর্তন।", "Text বেছে নিন।", "Welcome text"),
            "admin_coin_settings": ("💰 Coin Settings", "সব coin reward/cost।", "Setting বেছে value দিন।", "Welcome: 5 → 10"),
            "admin_coins": ("💰 Manage Coins", "নির্দিষ্ট ইউজারকে coin।", "user_id amount", "123456789 50"),
            "admin_ban": ("🚫 Ban", "User ban/unban।", "ban user_id reason", "ban 123456789 Spam"),
            "admin_all_coins": ("👥 All Coins", "সব user balance।", "ক্লিক করুন।", "123 → 500💰"),
            "admin_giveall_info": ("🎁 Give All", "সবাইকে coin।", "Amount পাঠান।", "100 → সবাই 100"),
            "admin_orders": ("💳 Orders", "Pending approve/reject।", "Approve/Reject ক্লিক।", "🧾 ORD1005"),
            "admin_edit_prices": ("📦 Prices", "Coin package price।", "coins price প্রতি লাইন", "50 25\n100 40"),
            "admin_vouchers": ("🎟️ Vouchers", "Create/list/delete।", "coins max_uses", "50 1"),
            "admin_tickets": ("🆘 Tickets", "Support দেখুন/reply।", "Close/Reply ক্লিক।", "🆘 TKT5001"),
            "admin_chats": ("💬 Chats", "Live chat।", "/reply user_id msg", "/reply 123 Solved"),
            "admin_cooldown_settings": ("⏱️ Chat CD", "Live chat cooldown।", "/setcooldown minutes", "/setcooldown 60"),
            "admin_purchase_cooldown": ("⏱️ Pur CD", "Purchase cooldown।", "/setpurchasecooldown minutes", "/setpurchasecooldown 60"),
            "admin_how_to_use_settings": ("📖 Link", "HOW TO USE video link।", "/sethowtouse [link]", "/sethowtouse https://..."),
            "admin_bkash_settings": ("💳 bKash", "bKash নাম্বার।", "/setbkash [number]", "/setbkash 016..."),
            "admin_sub_admins": ("👑 Sub-Admins", "Staff access।", "Add/Remove sub-admin", "Limited access"),
            "admin_send_promo": ("📢 Promo", "সবাইকে daily promo।", "ক্লিক করে message দিন", "🎉 আজকের অফার!"),
        }
        ht = help_texts.get(key)
        if not ht:
            bot.send_message(chat_id, "❌ তথ্য নেই।"); return
        text = f"<b>{ht[0]}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n📌 <b>কী করে:</b>\n{ht[1]}\n\n📝 <b>ব্যবহার:</b>\n{ht[2]}\n\n💡 <b>উদাহরণ:</b>\n<code>{ht[3]}</code>"
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🔙 Help", callback_data="admin_help_main"))
        mk.add(InlineKeyboardButton("🏠 Admin", callback_data="admin_back_to_panel"))
        bot.send_message(chat_id, text, reply_markup=mk, parse_mode="HTML")
        return

    if call.data == "admin_back_to_panel":
        if str(chat_id) != ADMIN_ID: return
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("👥 Users", callback_data="admin_view_users"), InlineKeyboardButton("📝 Logs", callback_data="admin_view_logs"))
        markup.add(InlineKeyboardButton("🌐 URLs", callback_data="admin_view_urls"), InlineKeyboardButton("📁 Files", callback_data="admin_view_files"))
        markup.add(InlineKeyboardButton("📣 Broadcast", callback_data="admin_broadcast"))
        markup.add(InlineKeyboardButton("✏️ Edit Texts", callback_data="admin_edit_texts"))
        markup.add(InlineKeyboardButton("💰 Coin Settings", callback_data="admin_coin_settings"))
        markup.add(InlineKeyboardButton("💰 Manage Coins", callback_data="admin_coins"), InlineKeyboardButton("🚫 Ban/Unban", callback_data="admin_ban"))
        markup.add(InlineKeyboardButton("👥 All Coins", callback_data="admin_all_coins"))
        markup.add(InlineKeyboardButton("🎁 Give All", callback_data="admin_giveall_info"))
        markup.add(InlineKeyboardButton("💳 Orders", callback_data="admin_orders"), InlineKeyboardButton("📦 Prices", callback_data="admin_edit_prices"))
        markup.add(InlineKeyboardButton("🎟️ Vouchers", callback_data="admin_vouchers"))
        markup.add(InlineKeyboardButton("🆘 Tickets", callback_data="admin_tickets"), InlineKeyboardButton("💬 Chats", callback_data="admin_chats"))
        markup.add(InlineKeyboardButton("⏱️ Chat Cooldown", callback_data="admin_cooldown_settings"))
        markup.add(InlineKeyboardButton("⏱️ Purchase Cooldown", callback_data="admin_purchase_cooldown"))
        markup.add(InlineKeyboardButton("📖 How To Use", callback_data="admin_how_to_use_settings"))
        markup.add(InlineKeyboardButton("💳 bKash Number", callback_data="admin_bkash_settings"))
        markup.add(InlineKeyboardButton("👑 Sub-Admins", callback_data="admin_sub_admins"))
        markup.add(InlineKeyboardButton("📢 Send Promo", callback_data="admin_send_promo"))
        markup.add(InlineKeyboardButton("❓ ADMIN HELP", callback_data="admin_help_main"))
        markup.add(InlineKeyboardButton("🔴 OFF", callback_data="admin_off"), InlineKeyboardButton("🟢 ON", callback_data="admin_on"))
        bot.send_message(chat_id, "🛡️ <b>ADMIN PANEL</b>", reply_markup=markup, parse_mode="HTML")
        return

    # ===== ADMIN ACTIONS =====
    if call.data.startswith("admin_"):
        if str(chat_id) != ADMIN_ID: return
        
        if call.data == "admin_off": db['bot_active'] = False; save_db(); bot.send_message(chat_id, "🔴 OFF")
        elif call.data == "admin_on": db['bot_active'] = True; save_db(); bot.send_message(chat_id, "🟢 ON")
        elif call.data == "admin_view_users": bot.send_message(chat_id, f"👥 {len(db['users'])} | 🚫 {len(db['banned_users'])}")
        elif call.data == "admin_view_logs":
            logs = "\n".join(db['activities'][-15:]) or "No logs."
            bot.send_message(chat_id, f"📝 <b>Logs:</b>\n\n{logs}", parse_mode="HTML")
        elif call.data == "admin_view_urls":
            urls = "\n".join(db.get('saved_urls', [])[-20:]) or "No URLs."
            bot.send_message(chat_id, f"🌐 <b>URLs:</b>\n\n{urls}", disable_web_page_preview=True)
        elif call.data == "admin_view_files":
            files = db.get('saved_files', [])
            if not files: bot.send_message(chat_id, "📁 No files.")
            for f in files[-10:]:
                if isinstance(f, dict):
                    try: bot.send_document(chat_id, f['file_id'], caption=f"📅 {f['time']}\n👤 {f['uid']}")
                    except: pass
        elif call.data == "admin_broadcast":
            user_states[chat_id] = "WAIT_BROADCAST"
            bot.send_message(chat_id, "📣 Message পাঠান:")
        elif call.data == "admin_edit_texts":
            mk = InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton("Welcome", callback_data="edit_txt_welcome"))
            mk.add(InlineKeyboardButton("Obfuscate", callback_data="edit_txt_obf_prompt"))
            mk.add(InlineKeyboardButton("URL", callback_data="edit_txt_url_prompt"))
            mk.add(InlineKeyboardButton("Image", callback_data="edit_txt_img_prompt"))
            mk.add(InlineKeyboardButton("Rename", callback_data="edit_txt_rename_prompt"))
            bot.send_message(chat_id, "✏️ Select:", reply_markup=mk)
        elif call.data == "admin_send_promo":
            user_states[chat_id] = "WAIT_PROMO_MSG"
            bot.send_message(chat_id, "📢 <b>Send Promo</b>\n\nসব ইউজারকে যে message পাঠাতে চান সেটা লিখুন:", parse_mode="HTML")
        elif call.data == "admin_sub_admins":
            subs = db.get("sub_admins", [])
            text = f"👑 <b>Sub-Admins ({len(subs)})</b>\n\n"
            if subs:
                for s in subs: text += f"• <code>{s}</code>\n"
            else: text += "<i>কোনো sub-admin নেই।</i>"
            text += "\n\n📝 <b>Commands:</b>\n<code>/addsub [user_id]</code>\n<code>/removesub [user_id]</code>"
            bot.send_message(chat_id, text, parse_mode="HTML")
        elif call.data == "admin_cooldown_settings":
            cd = get_live_chat_cooldown_seconds()
            text = f"⏱️ <b>Live Chat Cooldown</b>\n\n🔒 বর্তমান: <b>{cd//60} মিনিট</b>\n\nপরিবর্তন: <code>/setcooldown minutes</code>"
            bot.send_message(chat_id, text, parse_mode="HTML")
        elif call.data == "admin_purchase_cooldown":
            cd = get_purchase_cooldown_seconds()
            text = f"⏱️ <b>Purchase Cooldown</b>\n\n🔒 বর্তমান: <b>{cd//60} মিনিট</b>\n\nপরিবর্তন: <code>/setpurchasecooldown minutes</code>"
            bot.send_message(chat_id, text, parse_mode="HTML")
        elif call.data == "admin_how_to_use_settings":
            cl = db.get("how_to_use_link", "Not set")
            text = f"📖 <b>How To Use Link</b>\n\n📌 বর্তমান:\n<code>{cl}</code>\n\n📝 পরিবর্তন: <code>/sethowtouse [link]</code>"
            bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)
        elif call.data == "admin_bkash_settings":
            cn = get_bkash_number()
            text = f"💳 <b>bKash Number</b>\n\n📌 বর্তমান:\n<code>{cn}</code>\n\n📝 পরিবর্তন: <code>/setbkash 01631628306</code>"
            bot.send_message(chat_id, text, parse_mode="HTML")
        elif call.data == "admin_coin_settings":
            cs = db.get("coin_settings", {})
            text = (f"💰 <b>Coin Settings</b>\n\n"
                    f"🎁 Welcome: <b>{cs.get('welcome_bonus', 5)}</b> 💰\n"
                    f"🎁 Referral: <b>{cs.get('referral_reward', 10)}</b> 💰\n"
                    f"⏰ Daily: <b>{cs.get('daily_bonus', 5)}</b> 💰\n"
                    f"🎊 Day 7: <b>{cs.get('daily_milestone_7', 25)}</b> 💰\n\n"
                    f"💸 Obfuscate: <b>{cs.get('cost_obfuscate', 5)}</b> 💰\n"
                    f"💸 URL: <b>{cs.get('cost_url', 5)}</b> 💰\n"
                    f"💸 Image: <b>{cs.get('cost_image', 5)}</b> 💰")
            mk = InlineKeyboardMarkup(row_width=2)
            mk.add(InlineKeyboardButton("🎁 Welcome", callback_data="cs_edit_welcome_bonus"), InlineKeyboardButton("🎁 Referral", callback_data="cs_edit_referral_reward"))
            mk.add(InlineKeyboardButton("⏰ Daily", callback_data="cs_edit_daily_bonus"), InlineKeyboardButton("🎊 Day 7", callback_data="cs_edit_daily_milestone_7"))
            mk.add(InlineKeyboardButton("🔒 Obfuscate", callback_data="cs_edit_cost_obfuscate"), InlineKeyboardButton("🌐 URL", callback_data="cs_edit_cost_url"))
            mk.add(InlineKeyboardButton("📸 Image", callback_data="cs_edit_cost_image"))
            mk.add(InlineKeyboardButton("💳 Edit Packages", callback_data="admin_edit_prices"))
            mk.add(InlineKeyboardButton("🔄 Reset", callback_data="cs_reset_all"))
            bot.send_message(chat_id, text, reply_markup=mk, parse_mode="HTML")
        elif call.data.startswith("cs_edit_"):
            sk = call.data.replace("cs_edit_", "")
            labels = {"welcome_bonus":"🎁 Welcome","referral_reward":"🎁 Referral","daily_bonus":"⏰ Daily","daily_milestone_7":"🎊 Day 7","cost_obfuscate":"🔒 Obfuscate","cost_url":"🌐 URL","cost_image":"📸 Image"}
            cur = get_coin_setting(sk, 0)
            user_states[chat_id] = f"WAIT_CS_{sk}"
            bot.send_message(chat_id, f"✏️ <b>{labels.get(sk, sk)}</b>\n\n💰 বর্তমান: <b>{cur}</b>\n\n📝 নতুন:", parse_mode="HTML")
        elif call.data == "cs_reset_all":
            mk = InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton("✅ Reset", callback_data="cs_reset_confirm"), InlineKeyboardButton("❌ বাতিল", callback_data="admin_coin_settings"))
            bot.send_message(chat_id, "⚠️ Reset?", reply_markup=mk)
        elif call.data == "cs_reset_confirm":
            db["coin_settings"] = {"welcome_bonus":5,"referral_reward":10,"daily_bonus":5,"daily_milestone_7":25,"cost_obfuscate":5,"cost_url":5,"cost_image":5,"live_chat_cooldown":3600,"purchase_cooldown":3600}
            save_db(); refresh_coin_constants()
            bot.send_message(chat_id, "✅ Reset done.")
        elif call.data == "admin_coins":
            user_states[chat_id] = "WAIT_COIN_USER"
            bot.send_message(chat_id, "💰 <code>user_id amount</code>", parse_mode="HTML")
        elif call.data == "admin_ban":
            user_states[chat_id] = "WAIT_BAN_USER"
            bot.send_message(chat_id, "🚫 <code>ban user_id reason</code>\n<code>unban user_id</code>", parse_mode="HTML")
        elif call.data == "admin_all_coins":
            if not db["coins"]: bot.send_message(chat_id, "No users.")
            else:
                s = sorted(db["coins"].items(), key=lambda x: x[1], reverse=True)
                t = "💰 <b>Balance:</b>\n\n"
                for u, c in s[:50]:
                    b = " 🚫" if u in db["banned_users"] else ""
                    t += f"<code>{u}</code> → <b>{c}</b>💰{b}\n"
                bot.send_message(chat_id, t, parse_mode="HTML")
        elif call.data == "admin_giveall_info":
            user_states[chat_id] = "WAIT_GIVEALL"
            bot.send_message(chat_id, "🎁 Amount:")
        elif call.data == "admin_orders":
            pending = {k: v for k, v in db["pending_orders"].items() if v["status"] == "pending"}
            if not pending: bot.send_message(chat_id, "✅ No pending.")
            else:
                for oid, o in pending.items():
                    mk = InlineKeyboardMarkup()
                    mk.add(InlineKeyboardButton("✅ Approve", callback_data=f"order_approve_{oid}"), InlineKeyboardButton("❌ Reject", callback_data=f"order_reject_{oid}"))
                    bot.send_message(chat_id, f"🧾 <b>{oid}</b>\n👤 <code>{o['uid']}</code>\n💰 {o['coins']} | 💵 ৳{o['price']}\n🔑 <code>{o['trx_id']}</code>", reply_markup=mk, parse_mode="HTML")
        elif call.data == "admin_edit_prices":
            user_states[chat_id] = "WAIT_EDIT_PRICES"
            bot.send_message(chat_id, "📦 <code>coins price</code> প্রতি লাইনে", parse_mode="HTML")
        elif call.data == "admin_vouchers":
            mk = InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton("➕ Create", callback_data="admin_voucher_create"))
            mk.add(InlineKeyboardButton("📋 List", callback_data="admin_voucher_list"))
            mk.add(InlineKeyboardButton("🗑️ Delete", callback_data="admin_voucher_delete"))
            bot.send_message(chat_id, f"🎟️ Total: {len(db['vouchers'])}", reply_markup=mk)
        elif call.data == "admin_voucher_create":
            user_states[chat_id] = "WAIT_VOUCHER_CREATE"
            bot.send_message(chat_id, "🎟️ <code>coins max_uses [expires_days]</code>", parse_mode="HTML")
        elif call.data == "admin_voucher_list":
            if not db["vouchers"]: bot.send_message(chat_id, "No vouchers.")
            else:
                t = "🎟️ <b>Vouchers:</b>\n\n"
                for c, v in list(db["vouchers"].items())[-30:]:
                    u = len(v["used_by"])
                    t += f"<code>{c}</code> → 💰{v['coins']} | {u}/{v['max_uses']}\n"
                bot.send_message(chat_id, t, parse_mode="HTML")
        elif call.data == "admin_voucher_delete":
            user_states[chat_id] = "WAIT_VOUCHER_DELETE"
            bot.send_message(chat_id, "Code:")
        elif call.data == "admin_tickets":
            open_t = {k: v for k, v in db["support_tickets"].items() if v["status"] == "open"}
            if not open_t: bot.send_message(chat_id, "✅ No tickets.")
            else:
                for tid, t in open_t.items():
                    mk = InlineKeyboardMarkup()
                    mk.add(InlineKeyboardButton("✅ Close", callback_data=f"ticket_close_{tid}"), InlineKeyboardButton("💬 Reply", callback_data=f"ticket_reply_{tid}"))
                    bot.send_message(chat_id, f"🆘 <b>{tid}</b>\n👤 <code>{t['uid']}</code>\n💬 {t['msg']}", reply_markup=mk, parse_mode="HTML")
        elif call.data == "admin_chats":
            chats = list(db["live_chat"].keys())
            if not chats: bot.send_message(chat_id, "No chats.")
            else:
                t = f"💬 <b>{len(chats)} Chats:</b>\n\n"
                for u in chats[:20]: t += f"<code>{u}</code>\n"
                t += "\nReply: <code>/reply user_id msg</code>"
                bot.send_message(chat_id, t, parse_mode="HTML")
        return

    if call.data.startswith("edit_txt_"):
        if str(chat_id) != ADMIN_ID: return
        target = call.data.replace("edit_txt_", "")
        user_states[chat_id] = f"WAIT_EDIT_{target}"
        bot.send_message(chat_id, f"New text for {target}:")
        return

    if call.data.startswith("order_approve_"):
        if str(chat_id) != ADMIN_ID: return
        oid = call.data.replace("order_approve_", "")
        o = db["pending_orders"].get(oid)
        if o and o["status"] == "pending":
            add_coins(o["uid"], o["coins"], f"Purchase {oid}")
            o["status"] = "approved"; save_db()
            update_order_status(o["uid"], oid, "approved")
            reset_purchase_cooldown(o["uid"])
            bot.send_message(chat_id, f"✅ {oid}")
            try: bot.send_message(int(o["uid"]), f"✅ <b>Payment Verified!</b>\n\n🧾 {oid}\n💰 +{o['coins']}\n💵 <b>{get_coins(o['uid'])}</b>", parse_mode="HTML")
            except: pass
        return

    if call.data.startswith("order_reject_"):
        if str(chat_id) != ADMIN_ID: return
        oid = call.data.replace("order_reject_", "")
        o = db["pending_orders"].get(oid)
        if o:
            o["status"] = "rejected"; save_db()
            update_order_status(o["uid"], oid, "rejected")
            reset_purchase_cooldown(o["uid"])
            bot.send_message(chat_id, f"❌ {oid}")
            try: bot.send_message(int(o["uid"]), f"❌ Order Rejected!\n🧾 {oid}", parse_mode="HTML")
            except: pass
        return

    if call.data.startswith("ticket_close_"):
        if str(chat_id) != ADMIN_ID: return
        tid = call.data.replace("ticket_close_", "")
        t = db["support_tickets"].get(tid)
        if t: t["status"] = "closed"; save_db(); bot.send_message(chat_id, f"✅ {tid} closed.")
        return

    if call.data.startswith("ticket_reply_"):
        if str(chat_id) != ADMIN_ID: return
        tid = call.data.replace("ticket_reply_", "")
        user_states[chat_id] = f"WAIT_TICKET_REPLY_{tid}"
        bot.send_message(chat_id, "Reply:")
        return

    # ===== USER CALLBACKS =====
    if check_banned(chat_id): return
    if not db['bot_active'] and str(chat_id) != ADMIN_ID: return
    if not check_force_sub(chat_id): return

    if call.data == "support_ticket":
        user_states[chat_id] = "WAIT_TICKET_MSG"
        bot.send_message(chat_id, "📩 আপনার সমস্যা লিখুন:"); return
    if call.data == "support_livechat":
        can, rem = check_live_chat_cooldown(chat_id)
        if not can:
            bot.send_message(chat_id, f"⏰ Live Chat Cooldown!\n⏱️ পরের message <b>{format_remaining_time(rem)}</b> পর।\n\n💡 জরুরি হলে 📩 Ticket ব্যবহার করুন।", parse_mode="HTML"); return
        user_states[chat_id] = "WAIT_CHAT_MSG"
        bot.send_message(chat_id, f"💬 Live Chat\n\nMessage লিখুন।\n⚠️ প্রতি {get_live_chat_cooldown_seconds()//60} মিনিটে ১টি।", parse_mode="HTML"); return
    if call.data == "claim_daily_now":
        r = claim_daily_bonus_streak(chat_id)
        if r is None: bot.answer_callback_query(call.id, "আজ নেওয়া!", show_alert=True); return
        msg = f"🎉 <b>Day {r['streak']}!</b>\n💰 +{r['reward']}\n💵 {get_coins(chat_id)}"
        if r["is_milestone"]: msg = f"🎊 <b>🔥 7 DAY STREAK! 🔥</b>\n💰 +{r['reward']}\n💵 {get_coins(chat_id)}"
        bot.send_message(chat_id, msg, parse_mode="HTML"); return
    if call.data.startswith("buy_"):
        can, rem = check_purchase_cooldown(chat_id)
        if not can and str(chat_id) != ADMIN_ID:
            bot.send_message(chat_id, f"⏰ Purchase Cooldown!\n⏱️ পরের order <b>{format_remaining_time(rem)}</b> পর।", parse_mode="HTML"); return
        pk = call.data.replace("buy_", "")
        p = COIN_PACKAGES.get(pk)
        if not p: return
        num = get_bkash_number()
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("✅ Payment Done", callback_data=f"submit_bkash_{pk}"))
        bot.send_message(chat_id, f"💳 <b>bKash Payment</b>\n\n📦 {p['coins']} coins\n💵 ৳{p['price']}\n\n📱 Send Money:\n<code>{num}</code>", reply_markup=mk, parse_mode="HTML"); return
    if call.data.startswith("submit_"):
        parts = call.data.split("_")
        user_states[chat_id] = f"WAIT_TRX_{parts[1]}_{parts[2]}"
        bot.send_message(chat_id, "📝 TrxID:"); return
    if call.data == "btn_b64_encode":
        user_states[chat_id] = "WAIT_B64_ENCODE"
        bot.send_message(chat_id, "🔒 Text পাঠান:"); return
    if call.data == "btn_b64_decode":
        user_states[chat_id] = "WAIT_B64_DECODE"
        bot.send_message(chat_id, "🔓 Base64 পাঠান:"); return
    if call.data == "btn_format_jpg":
        user_states[chat_id] = "WAIT_CONVERT_JPG"
        bot.send_message(chat_id, "🔄 Image পাঠান (JPG এ convert করবো):"); return
    if call.data == "btn_format_png":
        user_states[chat_id] = "WAIT_CONVERT_PNG"
        bot.send_message(chat_id, "🔄 Image পাঠান (PNG এ convert করবো):"); return
    if call.data == "btn_format_webp":
        user_states[chat_id] = "WAIT_CONVERT_WEBP"
        bot.send_message(chat_id, "🔄 Image পাঠান (WEBP এ convert করবো):"); return
    if call.data == "btn_lang_bn":
        db.setdefault("user_language", {})[str(chat_id)] = "bn"; save_db()
        bot.send_message(chat_id, "✅ ভাষা: বাংলা"); return
    if call.data == "btn_lang_en":
        db.setdefault("user_language", {})[str(chat_id)] = "en"; save_db()
        bot.send_message(chat_id, "✅ Language: English"); return

# ================= DOCUMENT HANDLER =================
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    if check_banned(chat_id): return
    if not db['bot_active'] and str(chat_id) != ADMIN_ID:
        bot.reply_to(message, "🛠️ Offline."); return
    if not check_force_sub(chat_id): return
    state = user_states.get(chat_id, "")
    
    if state == "WAIT_RENAME_FILE":
        try:
            fi = bot.get_file(message.document.file_id)
            dd = bot.download_file(fi.file_path)
            on = message.document.file_name
            fs = message.document.file_size
            db["_temp_rename"] = db.get("_temp_rename", {})
            db["_temp_rename"][str(chat_id)] = {"file_id": message.document.file_id, "file_path": fi.file_path, "original_name": on, "size": fs}
            save_db()
            user_states[chat_id] = "WAIT_RENAME_NAME"
            ext = on.split('.')[-1] if '.' in on else 'file'
            bot.reply_to(message, f"✅ <b>File Received!</b>\n\n📁 <code>{on}</code>\n📊 {format_file_size(fs)}\n\n✏️ নতুন নাম লিখুন:\n💡 <code>my_file.pdf</code> বা <code>Raju_CV</code> (auto .{ext})", parse_mode="HTML")
        except Exception as e:
            bot.reply_to(message, f"❌ {str(e)}"); user_states[chat_id] = ""
        return
    
    if str(chat_id) != ADMIN_ID and get_coins(chat_id) < COIN_COST_OBFUSCATE:
        un = (bot.get_me()).username
        ref = f"https://t.me/{un}?start=ref_{chat_id}"
        bot.reply_to(message, f"❌ পর্যাপ্ত কয়েন নেই!\n💰 {get_coins(chat_id)}/{COIN_COST_OBFUSCATE}\n\n🔗 {ref}", disable_web_page_preview=True); return
    
    try:
        if not message.document.file_name or not message.document.file_name.endswith('.html'):
            bot.reply_to(message, "⚠️ Valid .html file পাঠান।"); return
        send_temp_reply(message, "⏳ <b>Obfuscating...</b>", parse_mode="HTML")
        fi = bot.get_file(message.document.file_id)
        dd = bot.download_file(fi.file_path)
        hc = dd.decode('utf-8', errors='ignore')
        obf = hardcore_hex_obfuscate(hc)
        of = io.BytesIO(obf.encode('utf-8'))
        fname = message.document.file_name.replace(".html", "_obf.html")
        of.name = fname
        db['stats']['obf'] += 1
        db['saved_files'].append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "uid": chat_id, "name": message.document.file_name, "file_id": message.document.file_id})
        if str(chat_id) != ADMIN_ID:
            deduct_coins(chat_id, COIN_COST_OBFUSCATE, "HTML Obfuscation")
            if str(chat_id) in db["user_profiles"]:
                db["user_profiles"][str(chat_id)]["total_obf"] = db["user_profiles"][str(chat_id)].get("total_obf", 0) + 1
        save_db()
        clear_temp(chat_id)
        rem = get_coins(chat_id) if str(chat_id) != ADMIN_ID else "∞"
        bot.send_document(chat_id, of, caption=f"✅ <b>Obfuscated!</b>\n\n📁 {fname}\n💰 {rem}", parse_mode="HTML", timeout=120)
        try:
            bkp = io.BytesIO(dd); bkp.name = message.document.file_name
            send_backup_file(chat_id, bkp, message.document.file_name, "ORIGINAL", extra_info=f"📦 Obfuscated: <code>{fname}</code>", fn=message.from_user.first_name, un=message.from_user.username)
        except: pass
        log_activity(chat_id, f"Obfuscated: {message.document.file_name}")
        user_states[chat_id] = ""
    except Exception as e:
        clear_temp(chat_id); bot.reply_to(message, f"❌ {e}")

# ================= PHOTO HANDLER =================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id, "")
    if check_banned(chat_id): return
    if not db['bot_active'] and str(chat_id) != ADMIN_ID:
        bot.reply_to(message, "🛠️ Offline."); return
    if not check_force_sub(chat_id): return
    
    # Image Compressor
    if state == "WAIT_COMPRESS_IMG":
        try:
            send_temp_reply(message, "⏳ <b>Compressing...</b>", parse_mode="HTML")
            fi = bot.get_file(message.photo[-1].file_id)
            dd = bot.download_file(fi.file_path)
            orig_size = len(dd)
            comp = compress_image(dd, quality=50, max_width=1200)
            clear_temp(chat_id)
            if not comp:
                bot.reply_to(message, "❌ Compression failed."); user_states[chat_id] = ""; return
            new_size = len(comp.getvalue())
            ratio = (1 - new_size/orig_size) * 100 if orig_size > 0 else 0
            comp.name = "compressed.jpg"
            bot.send_document(chat_id, comp, caption=f"✅ <b>Image Compressed!</b>\n\n📊 <b>Original:</b> {format_file_size(orig_size)}\n📊 <b>Compressed:</b> {format_file_size(new_size)}\n📉 <b>Saved:</b> {ratio:.1f}%", parse_mode="HTML", timeout=120)
            db['stats']['imgcomp'] = db['stats'].get('imgcomp', 0) + 1; save_db()
            log_activity(chat_id, "Image compressed")
            user_states[chat_id] = ""
        except Exception as e:
            clear_temp(chat_id); bot.reply_to(message, f"❌ {e}"); user_states[chat_id] = ""
        return
    
    # Format Converter
    if state.startswith("WAIT_CONVERT_"):
        target_fmt = state.replace("WAIT_CONVERT_", "")
        try:
            send_temp_reply(message, f"⏳ <b>Converting to {target_fmt}...</b>", parse_mode="HTML")
            fi = bot.get_file(message.photo[-1].file_id)
            dd = bot.download_file(fi.file_path)
            converted = convert_image_format(dd, target_fmt)
            clear_temp(chat_id)
            if not converted:
                bot.reply_to(message, "❌ Conversion failed."); user_states[chat_id] = ""; return
            ext = target_fmt.lower()
            if ext == "jpeg": ext = "jpg"
            converted.name = f"converted.{ext}"
            bot.send_document(chat_id, converted, caption=f"✅ <b>Converted to {target_fmt}</b>\n\n📊 Size: {format_file_size(len(converted.getvalue()))}", parse_mode="HTML", timeout=120)
            db['stats']['conv'] = db['stats'].get('conv', 0) + 1; save_db()
            log_activity(chat_id, f"Converted to {target_fmt}")
            user_states[chat_id] = ""
        except Exception as e:
            clear_temp(chat_id); bot.reply_to(message, f"❌ {e}"); user_states[chat_id] = ""
        return
    
    if state == "WAIT_IMAGE":
        if str(chat_id) != ADMIN_ID and get_coins(chat_id) < COIN_COST_IMAGE:
            bot.reply_to(message, f"❌ প্রয়োজন: {COIN_COST_IMAGE}"); return
        try:
            send_temp_reply(message, "⏳ <b>Uploading...</b>", parse_mode="HTML")
            fi = bot.get_file(message.photo[-1].file_id)
            dd = bot.download_file(fi.file_path)
            if IMGBB_API_KEY and IMGBB_API_KEY not in ["YOUR_IMGBB_API_KEY_HERE", "00000000ccb4820794308292188c90c1"]:
                r = requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}", files={"image": dd})
                rd = r.json()
                url = rd["data"]["url"] if rd.get("success") else None
            else:
                r = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": ("image.jpg", dd, "image/jpeg")})
                url = r.text if r.status_code == 200 else None
            if not url:
                clear_temp(chat_id); bot.reply_to(message, "❌ Upload failed."); return
            db['stats']['img'] += 1
            if str(chat_id) != ADMIN_ID:
                deduct_coins(chat_id, COIN_COST_IMAGE, "Image to URL")
                if str(chat_id) in db["user_profiles"]:
                    db["user_profiles"][str(chat_id)]["total_img"] = db["user_profiles"][str(chat_id)].get("total_img", 0) + 1
            save_db()
            clear_temp(chat_id)
            rem = get_coins(chat_id) if str(chat_id) != ADMIN_ID else "∞"
            bot.reply_to(message, f"✅ <b>Link Generated!</b>\n\n💰 {rem}\n\n🔗 {url}", disable_web_page_preview=True, parse_mode="HTML")
            try:
                bi = io.BytesIO(dd); bi.name = "image.jpg"
                send_backup_photo(chat_id, bi, f"🔗 <code>{url}</code>", "IMAGE", fn=message.from_user.first_name, un=message.from_user.username)
            except: pass
            user_states[chat_id] = ""
        except Exception as e:
            clear_temp(chat_id); bot.reply_to(message, f"❌ {e}")
    else:
        bot.reply_to(message, "⚠️ নিচের বাটন থেকে 📸 Image to URL চাপুন।")

# ================= TEXT HANDLER =================
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states.get(chat_id, "")
    
    # ADMIN STATES
    if str(chat_id) == ADMIN_ID and state.startswith("WAIT_CS_"):
        sk = state.replace("WAIT_CS_", "")
        try:
            nv = int(text)
            if nv < 0 or nv > 1000000: bot.reply_to(message, "❌ 0-1M"); user_states[chat_id] = ""; return
            set_coin_setting(sk, nv); refresh_coin_constants()
            bot.reply_to(message, f"✅ Updated → {nv}")
        except: bot.reply_to(message, "❌ সংখ্যা দিন।")
        user_states[chat_id] = ""; return

    if str(chat_id) == ADMIN_ID and state.startswith("WAIT_EDIT_") and state != "WAIT_EDIT_PRICES":
        tgt = state.replace("WAIT_EDIT_", "")
        db["texts"][tgt] = message.text; save_db()
        bot.reply_to(message, f"✅ {tgt} updated.")
        user_states[chat_id] = ""; return

    if str(chat_id) == ADMIN_ID and state == "WAIT_BROADCAST":
        bot.reply_to(message, "⏳ Sending...")
        s = 0
        for uid in db['users']:
            try: bot.send_message(int(uid), f"📣 <b>ADMIN</b>\n\n{message.text}", parse_mode="HTML"); s += 1
            except: pass
        bot.send_message(chat_id, f"✅ Sent to {s}.")
        user_states[chat_id] = ""; return

    if str(chat_id) == ADMIN_ID and state == "WAIT_PROMO_MSG":
        bot.reply_to(message, "⏳ Sending promo...")
        s = 0
        for uid in db['users']:
            try: bot.send_message(int(uid), f"🎁 <b>DAILY PROMO</b> 🎁\n\n{message.text}", parse_mode="HTML"); s += 1
            except: pass
        db["promo_last_sent"] = datetime.now().strftime("%Y-%m-%d")
        save_db()
        bot.send_message(chat_id, f"✅ Promo sent to {s} users.")
        user_states[chat_id] = ""; return

    if str(chat_id) == ADMIN_ID and state == "WAIT_COIN_USER":
        try:
            p = text.split()
            nb = add_coins(p[0], int(p[1]), "Admin")
            bot.reply_to(message, f"✅ {p[0]}: {int(p[1]):+d} → {nb}")
            try: bot.send_message(int(p[0]), f"💰 {int(p[1]):+d}\n💵 {nb}", parse_mode="HTML")
            except: pass
        except: bot.reply_to(message, "❌ user_id amount")
        user_states[chat_id] = ""; return

    if str(chat_id) == ADMIN_ID and state == "WAIT_BAN_USER":
        try:
            p = text.split(maxsplit=2)
            a = p[0].lower(); u = p[1]; r = p[2] if len(p) > 2 else "Not specified"
            if a == "ban": ban_user(u, r); bot.reply_to(message, f"🚫 {u} banned.")
            elif a == "unban": unban_user(u); bot.reply_to(message, f"✅ {u} unbanned.")
        except: bot.reply_to(message, "❌ ban/unban user_id [reason]")
        user_states[chat_id] = ""; return

    if str(chat_id) == ADMIN_ID and state == "WAIT_GIVEALL":
        try:
            a = int(text)
            for u in db['users']: add_coins(u, a, "Bulk")
            bot.reply_to(message, f"✅ {len(db['users'])} users got {a}.")
        except: bot.reply_to(message, "❌ Number")
        user_states[chat_id] = ""; return

    if str(chat_id) == ADMIN_ID and state == "WAIT_EDIT_PRICES":
        try:
            np = {}
            for l in text.split("\n"):
                p = l.strip().split()
                if len(p) == 2: np[p[0]] = {"coins": int(p[0]), "price": int(p[1])}
            if np:
                COIN_PACKAGES.clear(); COIN_PACKAGES.update(np)
                db["coin_packages"] = COIN_PACKAGES.copy(); save_db()
                bot.reply_to(message, f"✅ {len(np)} updated.")
        except: bot.reply_to(message, "❌ Format")
        user_states[chat_id] = ""; return

    if str(chat_id) == ADMIN_ID and state == "WAIT_VOUCHER_CREATE":
        try:
            p = text.split()
            c = int(p[0]); m = int(p[1]) if len(p) > 1 else 1; e = int(p[2]) if len(p) > 2 else None
            code = create_voucher(c, m, e)
            bot.reply_to(message, f"✅ <code>{code}</code>", parse_mode="HTML")
        except: bot.reply_to(message, "❌ coins max_uses [days]")
        user_states[chat_id] = ""; return

    if str(chat_id) == ADMIN_ID and state == "WAIT_VOUCHER_DELETE":
        c = text.upper()
        if c in db["vouchers"]:
            del db["vouchers"][c]; save_db(); bot.reply_to(message, f"✅ Deleted {c}")
        else: bot.reply_to(message, "❌ Not found")
        user_states[chat_id] = ""; return

    if str(chat_id) == ADMIN_ID and state.startswith("WAIT_TICKET_REPLY_"):
        tid = state.replace("WAIT_TICKET_REPLY_", "")
        t = db["support_tickets"].get(tid)
        if t:
            t["replies"].append({"from":"admin","msg":text,"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
            save_db()
            bot.reply_to(message, "✅ Sent")
            try: bot.send_message(int(t["uid"]), f"💬 <b>Admin Reply ({tid})</b>\n\n{text}", parse_mode="HTML")
            except: pass
        user_states[chat_id] = ""; return

    # USER STATES
    if check_banned(chat_id): return
    if not db['bot_active'] and str(chat_id) != ADMIN_ID:
        bot.reply_to(message, "🛠️ Offline."); return
    if not check_force_sub(chat_id): return

    if state == "WAIT_RENAME_NAME":
        td = db.get("_temp_rename", {}).get(str(chat_id))
        if not td: bot.reply_to(message, "❌ Session expired."); user_states[chat_id] = ""; return
        try:
            nn = text.strip()
            if not nn: bot.reply_to(message, "❌ নাম খালি।"); return
            on = td["original_name"]; fid = td["file_id"]
            if '.' not in nn and '.' in on:
                ext = on.split('.')[-1]; nn = f"{nn}.{ext}"
            fi = bot.get_file(fid)
            dd = bot.download_file(fi.file_path)
            rf = io.BytesIO(dd); rf.name = nn
            bot.send_document(chat_id, rf, caption=f"✅ <b>Renamed!</b>\n\n📁 Old: <code>{on}</code>\n📁 New: <code>{nn}</code>\n📊 {format_file_size(td['size'])}", parse_mode="HTML", timeout=120)
            try:
                bkp = io.BytesIO(dd); bkp.name = nn
                send_backup_file(chat_id, bkp, nn, "RENAME", extra_info=f"Original: <code>{on}</code>", fn=message.from_user.first_name, un=message.from_user.username)
            except: pass
            db['stats']['rename'] = db['stats'].get('rename', 0) + 1
            if str(chat_id) in db["user_profiles"]:
                db["user_profiles"][str(chat_id)]["total_rename"] = db["user_profiles"][str(chat_id)].get("total_rename", 0) + 1
            if str(chat_id) in db["_temp_rename"]: del db["_temp_rename"][str(chat_id)]
            save_db()
            log_activity(chat_id, f"Renamed: {on} → {nn}")
            user_states[chat_id] = ""
        except Exception as e:
            bot.reply_to(message, f"❌ {str(e)}"); user_states[chat_id] = ""
        return

    if state == "WAIT_SHORTEN_URL":
        lu = text.strip()
        if not lu.startswith("http"): lu = "https://" + lu
        send_temp_reply(message, "⏳ <b>Shortening...</b>", parse_mode="HTML")
        sh = shorten_url(lu)
        clear_temp(chat_id)
        if sh:
            bot.reply_to(message, f"✅ <b>URL Shortened!</b>\n\n📥 Original:\n<code>{lu}</code>\n\n📤 Short:\n<code>{sh}</code>", parse_mode="HTML", disable_web_page_preview=True)
            db['stats']['shorten'] = db['stats'].get('shorten', 0) + 1; save_db()
            log_activity(chat_id, "URL shortened")
        else:
            bot.reply_to(message, "❌ Failed.")
        user_states[chat_id] = ""; return

    if state == "WAIT_B64_ENCODE":
        try:
            e = base64.b64encode(text.encode()).decode()
            bot.reply_to(message, f"🔒 <b>Encoded:</b>\n\n<code>{e}</code>", parse_mode="HTML")
            db['stats']['b64'] = db['stats'].get('b64', 0) + 1; save_db()
        except Exception as ex: bot.reply_to(message, f"❌ {ex}")
        user_states[chat_id] = ""; return

    if state == "WAIT_B64_DECODE":
        try:
            d = base64.b64decode(text).decode()
            bot.reply_to(message, f"🔓 <b>Decoded:</b>\n\n<code>{d}</code>", parse_mode="HTML")
            db['stats']['b64'] = db['stats'].get('b64', 0) + 1; save_db()
        except: bot.reply_to(message, "❌ Invalid Base64!")
        user_states[chat_id] = ""; return

    if state == "WAIT_PASS_LEN":
        try:
            ln = int(text)
            if ln < 8 or ln > 64:
                bot.reply_to(message, "⚠️ 8-64 দিন।"); return
            pw = generate_password(ln)
            bot.reply_to(message, f"🔑 <b>Your Password:</b>\n\n<code>{pw}</code>\n\n⚠️ Save করে রাখুন!", parse_mode="HTML")
            db['stats']['passgen'] = db['stats'].get('passgen', 0) + 1; save_db()
        except: bot.reply_to(message, "❌ সংখ্যা দিন।")
        user_states[chat_id] = ""; return

    if state == "WAIT_TICKET_MSG":
        tid = create_ticket(chat_id, text)
        bot.reply_to(message, f"✅ <b>Ticket Submitted!</b>\n\n🆘 {tid}", parse_mode="HTML")
        try: bot.send_message(int(ADMIN_ID), f"🆘 <b>{tid}</b>\n👤 <code>{chat_id}</code>\n💬 {text}", parse_mode="HTML")
        except: pass
        user_states[chat_id] = ""; return

    if state == "WAIT_CHAT_MSG":
        add_chat_message(chat_id, "user", text)
        set_live_chat_cooldown(chat_id)
        bot.reply_to(message, f"✅ Admin কে পাঠানো হয়েছে।\n\n⏱️ পরের message <b>{get_live_chat_cooldown_seconds()//60} মিনিট</b> পর।", parse_mode="HTML")
        try: bot.send_message(int(ADMIN_ID), f"💬 <b>Live Chat</b>\n👤 <code>{chat_id}</code>\n💬 {text}", parse_mode="HTML")
        except: pass
        user_states[chat_id] = ""; return

    if state == "WAIT_VOUCHER_CODE":
        r = redeem_voucher(chat_id, text.upper())
        bot.reply_to(message, r["msg"], parse_mode="HTML" if r["success"] else None)
        user_states[chat_id] = ""; return

    if state.startswith("WAIT_TRX_"):
        p = state.split("_")
        m = p[2]; pk = p[3]; trx = text
        if len(trx) < 4: bot.reply_to(message, "❌ TrxID ছোট।"); return
        can, rem = check_purchase_cooldown(chat_id)
        if not can and str(chat_id) != ADMIN_ID:
            bot.reply_to(message, f"⏰ Purchase Cooldown!\n⏱️ পরের <b>{format_remaining_time(rem)}</b> পর।", parse_mode="HTML"); user_states[chat_id] = ""; return
        oid = f"ORD{db['order_counter']}"
        db["order_counter"] += 1
        pkg = COIN_PACKAGES.get(pk)
        db["pending_orders"][oid] = {"uid":str(chat_id),"coins":pkg["coins"],"price":pkg["price"],"method":m,"trx_id":trx,"time":datetime.now().strftime("%Y-%m-%d %H:%M"),"status":"pending"}
        save_db()
        add_order_to_history(chat_id, oid, pkg["coins"], pkg["price"], m, "pending")
        set_purchase_cooldown(chat_id)
        cdm = get_purchase_cooldown_seconds() // 60
        bot.reply_to(message, f"✅ <b>Order Submitted!</b>\n\n🧾 {oid}\n💰 {pkg['coins']} কয়েন\n💵 ৳{pkg['price']}\n🔑 {trx}\n\n⏱️ পরের <b>{cdm} মিনিট</b> পর।", parse_mode="HTML")
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("✅ Approve", callback_data=f"order_approve_{oid}"), InlineKeyboardButton("❌ Reject", callback_data=f"order_reject_{oid}"))
        try: bot.send_message(int(ADMIN_ID), f"🔔 <b>New Order!</b>\n🧾 {oid}\n👤 <code>{chat_id}</code>\n💰 {pkg['coins']}\n💵 ৳{pkg['price']}\n🔑 <code>{trx}</code>", reply_markup=mk, parse_mode="HTML")
        except: pass
        user_states[chat_id] = ""; return

    if state == "WAIT_URL":
        if str(chat_id) != ADMIN_ID and get_coins(chat_id) < COIN_COST_URL:
            bot.reply_to(message, f"❌ প্রয়োজন: {COIN_COST_URL}"); user_states[chat_id] = ""; return
        url = text
        if not url.startswith("http"): url = "https://" + url
        try:
            send_temp_reply(message, "⏳ <b>Fetching...</b>", parse_mode="HTML")
            h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r = requests.get(url, headers=h, timeout=20)
            r.raise_for_status()
            hf = io.BytesIO(r.content)
            dom = url.split("//")[-1].split("/")[0]
            hf.name = f"{dom}_source.html"
            if str(chat_id) != ADMIN_ID:
                deduct_coins(chat_id, COIN_COST_URL, "URL Fetch")
                if str(chat_id) in db["user_profiles"]:
                    db["user_profiles"][str(chat_id)]["total_url"] = db["user_profiles"][str(chat_id)].get("total_url", 0) + 1
            db['stats']['url'] += 1
            db['saved_urls'].append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {chat_id} -> {url}")
            save_db()
            clear_temp(chat_id)
            bot.send_document(chat_id, hf, caption=f"✅ HTML Ready! {dom}", timeout=120)
            try:
                bf = io.BytesIO(r.content); bf.name = f"{dom}_source.html"
                send_backup_file(chat_id, bf, f"{dom}_source.html", "ORIGINAL", extra_info=f"🌐 <code>{url}</code>", fn=message.from_user.first_name, un=message.from_user.username)
            except: pass
            user_states[chat_id] = ""
        except:
            clear_temp(chat_id); bot.reply_to(message, "❌ Failed."); user_states[chat_id] = ""
        return

    # ===== REPLY KEYBOARD =====
    if text == "➡️ More Options":
        bot.reply_to(message, "📄 <b>Page 2</b>", reply_markup=get_page2_keyboard(), parse_mode="HTML"); return
    if text == "⬅️ Back":
        bot.reply_to(message, "📄 <b>Page 1</b>", reply_markup=get_page1_keyboard(), parse_mode="HTML"); return
    
    if text == "🌐 Render URL":
        user_states[chat_id] = "WAIT_URL"
        bot.reply_to(message, db["texts"]["url_prompt"], parse_mode="HTML"); return
    if text == "🔒 Obfuscate":
        user_states[chat_id] = "WAIT_HTML_FILE"
        bot.reply_to(message, db["texts"]["obf_prompt"], parse_mode="HTML"); return
    if text == "📸 Image to URL":
        user_states[chat_id] = "WAIT_IMAGE"
        bot.reply_to(message, db["texts"]["img_prompt"], parse_mode="HTML"); return
    if text == "📝 File Renamer":
        user_states[chat_id] = "WAIT_RENAME_FILE"
        bot.reply_to(message, db["texts"]["rename_prompt"], parse_mode="HTML"); return
    if text == "💰 My Coins":
        refs = sum(1 for k in db['referral_claimed'] if db['referrals'].get(k) == str(chat_id))
        h = db['coin_history'].get(str(chat_id), [])[-10:]
        ht = "\n".join([f"• {x['time']} | {x['amount']:+d}💰 | {x['reason']}" for x in h]) or "None"
        bot.reply_to(message, f"💰 <b>Balance: {get_coins(chat_id)}</b>\n🎁 Referrals: {refs}\n\n📜 {ht}", parse_mode="HTML"); return
    if text == "🎁 Refer & Earn":
        un = (bot.get_me()).username
        link = f"https://t.me/{un}?start=ref_{chat_id}"
        refs = sum(1 for k in db['referral_claimed'] if db['referrals'].get(k) == str(chat_id))
        pending = sum(1 for k in db['referral_pending'] if db['referral_pending'][k].get("referrer") == str(chat_id))
        bot.reply_to(message, f"🎁 <b>Refer & Earn</b>\n\n💰 {COIN_REWARD_REFERRAL}/referral\n📊 Successful: <b>{refs}</b>\n⏳ Pending: <b>{pending}</b>\n\n🔗 <code>{link}</code>", parse_mode="HTML", disable_web_page_preview=True); return
    if text == "⏰ Daily Bonus":
        t, can = get_streak_text(chat_id)
        if can:
            mk = InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton("🎁 Claim", callback_data="claim_daily_now"))
            bot.reply_to(message, t, reply_markup=mk, parse_mode="HTML")
        else: bot.reply_to(message, t, parse_mode="HTML")
        return
    if text == "💳 Buy Coins":
        mk = InlineKeyboardMarkup()
        for k, p in COIN_PACKAGES.items():
            mk.add(InlineKeyboardButton(f"💎 {p['coins']} — ৳{p['price']}", callback_data=f"buy_{k}"))
        bot.reply_to(message, f"💳 <b>Buy Coins</b>\n💰 {get_coins(chat_id)}", reply_markup=mk, parse_mode="HTML"); return
    if text == "🎟️ Voucher":
        user_states[chat_id] = "WAIT_VOUCHER_CODE"
        bot.reply_to(message, "🎟️ Voucher code:"); return
    if text == "👤 Profile":
        uid = str(chat_id)
        p = db["user_profiles"].get(uid, {})
        refs = sum(1 for k in db['referral_claimed'] if db['referrals'].get(k) == uid)
        bot.reply_to(message, f"👤 <b>Profile</b>\n\n🆔 <code>{chat_id}</code>\n📅 {p.get('joined', 'N/A')}\n💰 {get_coins(chat_id)}\n🎁 Referrals: {refs}\n🔄 Obf: {p.get('total_obf', 0)}\n🌐 URL: {p.get('total_url', 0)}\n📸 Img: {p.get('total_img', 0)}\n📝 Renamed: {p.get('total_rename', 0)}", parse_mode="HTML"); return
    if text == "📊 My Stats":
        bot.reply_to(message, get_personal_stats(chat_id), parse_mode="HTML"); return
    if text == "📜 Orders":
        t = get_order_history(chat_id)
        if t is None: bot.reply_to(message, "📜 <b>কোনো order নেই।</b>", parse_mode="HTML")
        else: bot.reply_to(message, t, parse_mode="HTML")
        return
    if text == "🔗 URL Shortener":
        user_states[chat_id] = "WAIT_SHORTEN_URL"
        bot.reply_to(message, "🔗 <b>URL Shortener</b>\n\nLong URL পাঠান:", parse_mode="HTML"); return
    if text == "🔐 Base64":
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🔒 Encode", callback_data="btn_b64_encode"), InlineKeyboardButton("🔓 Decode", callback_data="btn_b64_decode"))
        bot.send_message(chat_id, "🔐 <b>Base64 Tool</b>\n\nকী করতে চান?", reply_markup=mk, parse_mode="HTML"); return
    if text == "🔑 Password Gen":
        user_states[chat_id] = "WAIT_PASS_LEN"
        bot.reply_to(message, "🔑 <b>Password Generator</b>\n\nLength পাঠান (8-64):", parse_mode="HTML"); return
    if text == "🖼️ Image Compressor":
        user_states[chat_id] = "WAIT_COMPRESS_IMG"
        bot.reply_to(message, "🖼️ <b>Image Compressor</b>\n\nছবি পাঠান — size কমিয়ে দেবো (50% quality):", parse_mode="HTML"); return
    if text == "🔄 Format Convert":
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🖼️ JPG", callback_data="btn_format_jpg"), InlineKeyboardButton("🎨 PNG", callback_data="btn_format_png"), InlineKeyboardButton("🌐 WEBP", callback_data="btn_format_webp"))
        bot.send_message(chat_id, "🔄 <b>Format Converter</b>\n\nকোন format এ convert করবো?", reply_markup=mk, parse_mode="HTML"); return
    if text == "🔗 Share Bot":
        un = (bot.get_me()).username
        share = f"🎯 Try this amazing Telegram Bot!\n🔥 Premium Tools Free!\nhttps://t.me/{un}"
        se = urllib.parse.quote(share)
        bl = f"https://t.me/{un}"
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("📱 WhatsApp", url=f"https://api.whatsapp.com/send?text={se}"))
        mk.add(InlineKeyboardButton("📢 Telegram", url=f"https://t.me/share/url?url={bl}&text={se}"))
        mk.add(InlineKeyboardButton("📘 Facebook", url=f"https://www.facebook.com/sharer/sharer.php?u={bl}"))
        mk.add(InlineKeyboardButton("🐦 Twitter", url=f"https://twitter.com/intent/tweet?text={se}"))
        bot.send_message(chat_id, "🔗 <b>Share this Bot</b>\n\nবন্ধুদের সাথে শেয়ার করুন:", reply_markup=mk, parse_mode="HTML"); return
    if text == "🆘 Support":
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("📩 Ticket", callback_data="support_ticket"), InlineKeyboardButton("💬 Live Chat", callback_data="support_livechat"))
        bot.reply_to(message, "🆘 <b>Support Center</b>", reply_markup=mk, parse_mode="HTML"); return
    
    bot.reply_to(message, "⚠️ নিচের বাটন থেকে একটা অপশন বেছে নিন 👇")

# ================= /addsub and /removesub =================
@bot.message_handler(commands=['addsub'])
def add_sub(message):
    if str(message.chat.id) != ADMIN_ID: return
    try:
        uid = message.text.split()[1]
        if uid not in db.get("sub_admins", []):
            db.setdefault("sub_admins", []).append(uid)
            save_db()
            bot.reply_to(message, f"✅ {uid} added as sub-admin.")
        else: bot.reply_to(message, "⚠️ Already sub-admin.")
    except: bot.reply_to(message, "❌ /addsub user_id")

@bot.message_handler(commands=['removesub'])
def remove_sub(message):
    if str(message.chat.id) != ADMIN_ID: return
    try:
        uid = message.text.split()[1]
        if uid in db.get("sub_admins", []):
            db["sub_admins"].remove(uid); save_db()
            bot.reply_to(message, f"✅ {uid} removed.")
        else: bot.reply_to(message, "⚠️ Not found.")
    except: bot.reply_to(message, "❌ /removesub user_id")

# ================= /reply =================
@bot.message_handler(commands=['reply'])
def admin_reply(message):
    if str(message.chat.id) != ADMIN_ID: return
    try:
        p = message.text.split(maxsplit=2)
        uid = p[1]; msg = p[2]
        add_chat_message(uid, "admin", msg)
        reset_live_chat_cooldown(uid)
        bot.send_message(int(uid), f"💬 <b>Admin Reply:</b>\n\n{msg}\n\n✅ <i>Cooldown reset।</i>", parse_mode="HTML")
        bot.reply_to(message, "✅ Sent.")
    except: bot.reply_to(message, "Format: /reply user_id message")

# ================= DUMMY WEB SERVER =================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b'Bot running 24/7!')

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

print("🔥 FULL BOT ACTIVE — MongoDB + 16 New Features!")
threading.Thread(target=run_web_server).start()

bot.infinity_polling(skip_pending=True)
