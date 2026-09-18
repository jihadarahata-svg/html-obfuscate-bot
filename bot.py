import base64,telebot,io,random,string,requests,json,os,urllib.parse,re,time,threading
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardMarkup,KeyboardButton
from datetime import datetime,timedelta
from http.server import HTTPServer,BaseHTTPRequestHandler
from pymongo import MongoClient
from PIL import Image

TOKEN='8800996502:AAG3jcKM94hCPC1iwY3o5pV2puS5-Wm8VyI'
ADMIN_ID="8691419913"
IMGBB_API_KEY="YOUR_IMGBB_API_KEY_HERE"
MONGO_URI="mongodb+srv://jihadarahata_db_user:jihadarahata_db_user@cluster0.yqzqslh.mongodb.net/?appName=Cluster0"
MONGO_DB_NAME="telegram_bot"

try:
    mongo_client=MongoClient(MONGO_URI,serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    mongo_db=mongo_client[MONGO_DB_NAME]
    mongo_collection=mongo_db["bot_data"]
    print("MongoDB Connected")
except Exception as e:
    print(f"MongoDB Error: {e}")
    mongo_collection=None

FORCE_CHANNELS=[
    {"id":"-1004328566497","link":"https://t.me/+ERxRWjTD_HYyNmVl","name":"📢 Official"},
    {"id":"-1003855006043","link":"https://t.me/+d-S6E1EUrBUwOTY1","name":"📢 Backup"},
]
BACKUP_CHANNEL_ID="-1003913034867"
BACKUP_CHANNEL_LINK="https://t.me/+7hqmxlrvp7kyOTFl"
bot=telebot.TeleBot(TOKEN)

COIN_REWARD_REFERRAL=10
COIN_REWARD_NEW_USER=5
COIN_COST_OBFUSCATE=5
COIN_COST_URL=5
COIN_COST_IMAGE=5
COIN_DAILY_BONUS=5
LIVE_CHAT_COOLDOWN_SECONDS=3600
PURCHASE_COOLDOWN_SECONDS=3600
STREAK_REWARDS={1:5,2:5,3:5,4:5,5:5,6:5,7:25}

COIN_PACKAGES={"50":{"coins":50,"price":20},"100":{"coins":100,"price":35},"250":{"coins":250,"price":80},"500":{"coins":500,"price":150},"1000":{"coins":1000,"price":280}}

DEFAULT_TEXTS={
    "welcome":"═══════════════════════════\n🎉𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗧𝗢𝗟𝗟 𝗕𝗢𝗧🎉\n═══════════════════════════\n👑𝐀𝐋𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐓𝐎𝐋𝐋𝐒 𝐅𝐑𝐄𝐄👑\n\n☠️𝐀𝐋𝐋 𝐇𝐀𝐂𝐊'𝐒 𝐓𝐎𝐋𝐋 𝐅𝐑𝐄𝐄☠️\n\n🎁𝗔𝗟𝗟 𝗚𝗜𝗩𝗘𝗔𝗪𝗔𝗬 𝗢𝗡 𝗧𝗛𝗘 𝗕𝗢𝗧🎁\n\n⚠️𝗩𝗘𝗥𝗬 𝗜𝗠𝗣𝗢𝗥𝗧𝗔𝗡𝗧 𝗙𝗢𝗥 '𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘' 𝗩𝗜𝗗𝗘𝗢⚠️\n\n⬇️𝐂𝐋𝐈𝐂𝐊 𝐓𝐇𝐈𝐒 𝐁𝐔𝐓𝐓𝐎𝐍 𝐀𝐍𝐃 𝐖𝐀𝐓𝐂𝐇 𝐓𝐇𝐄 𝐕𝗜𝗗𝗘𝗢⬇️",
    "obf_prompt":"⚠️ <b>HTML Obfuscate</b>\n\n📄 <b>Send your .html file!</b>",
    "url_prompt":"📍 <b>URL to HTML</b>\n\n🎁 <b>Send a URL!</b>",
    "img_prompt":"📸 <b>Image to URL</b>\n\n<b>Send Your Image!</b>",
    "rename_prompt":"📝 <b>File Renamer</b>\n\n<b>Step 1:</b> ফাইল পাঠান"
}

def get_default_db():
    return {"_id":"main","users":[],"activities":[],"bot_active":True,"saved_urls":[],"saved_files":[],"texts":DEFAULT_TEXTS,"stats":{"obf":0,"url":0,"img":0,"rename":0,"shorten":0,"b64":0,"passgen":0,"imgcomp":0,"conv":0},"coins":{},"banned_users":[],"referrals":{},"referral_claimed":[],"referral_pending":{},"coin_history":{},"daily_bonus":{},"pending_orders":{},"order_counter":1000,"coin_packages":COIN_PACKAGES.copy(),"daily_streak":{},"vouchers":{},"voucher_history":{},"order_history":{},"support_tickets":{},"ticket_counter":5000,"live_chat":{},"user_profiles":{},"user_notes":{},"ban_reasons":{},"live_chat_cooldown":{},"purchase_cooldown":{},"how_to_use_link":"https://t.me/+ERxRWjTD_HYyNmVl","bkash_number":"01631628306","user_language":{},"user_notifications":{},"recent_activity":{},"sub_admins":[],"milestone_sent":[],"promo_last_sent":"","coin_settings":{"welcome_bonus":5,"referral_reward":10,"daily_bonus":5,"daily_milestone_7":25,"cost_obfuscate":5,"cost_url":5,"cost_image":5,"live_chat_cooldown":3600,"purchase_cooldown":3600},"settings_updated":""}

def load_db():
    if mongo_collection is None: return get_default_db()
    try:
        data=mongo_collection.find_one({"_id":"main"})
        if not data:
            d=get_default_db()
            mongo_collection.insert_one(d)
            return d
        d=get_default_db()
        for k in d:
            if k not in data: data[k]=d[k]
        return data
    except Exception as e:
        print(f"Load Error: {e}")
        return get_default_db()

def save_db(data=None):
    global db
    if mongo_collection is None: return
    try:
        s={k:v for k,v in (data or db).items() if k!="_id"}
        mongo_collection.update_one({"_id":"main"},{"$set":s},upsert=True)
    except Exception as e:
        print(f"Save Error: {e}")

db=load_db()
if "coin_packages" in db and db["coin_packages"]:
    try:
        COIN_PACKAGES.clear()
        COIN_PACKAGES.update(db["coin_packages"])
    except: pass

user_states={}

def get_live_chat_cooldown_seconds():
    return db.get("coin_settings",{}).get("live_chat_cooldown",LIVE_CHAT_COOLDOWN_SECONDS)

def check_live_chat_cooldown(uid):
    u=str(uid)
    cu=db.get("live_chat_cooldown",{}).get(u)
    if not cu: return (True,0)
    n=time.time()
    if n>=cu:
        if u in db["live_chat_cooldown"]: del db["live_chat_cooldown"][u]; save_db()
        return (True,0)
    return (False,int(cu-n))

def set_live_chat_cooldown(uid):
    u=str(uid); cs=get_live_chat_cooldown_seconds()
    if cs<=0: return
    db["live_chat_cooldown"][u]=time.time()+cs; save_db()

def reset_live_chat_cooldown(uid):
    u=str(uid)
    if u in db["live_chat_cooldown"]: del db["live_chat_cooldown"][u]; save_db()

def get_purchase_cooldown_seconds():
    return db.get("coin_settings",{}).get("purchase_cooldown",PURCHASE_COOLDOWN_SECONDS)

def check_purchase_cooldown(uid):
    u=str(uid)
    cu=db.get("purchase_cooldown",{}).get(u)
    if not cu: return (True,0)
    n=time.time()
    if n>=cu:
        if u in db["purchase_cooldown"]: del db["purchase_cooldown"][u]; save_db()
        return (True,0)
    return (False,int(cu-n))

def set_purchase_cooldown(uid):
    u=str(uid); cs=get_purchase_cooldown_seconds()
    if cs<=0: return
    db["purchase_cooldown"][u]=time.time()+cs; save_db()

def reset_purchase_cooldown(uid):
    u=str(uid)
    if u in db["purchase_cooldown"]: del db["purchase_cooldown"][u]; save_db()

def fmt_time(s):
    if s<60: return f"{s} সেকেন্ড"
    elif s<3600: return f"{s//60} মিনিট {s%60} সেকেন্ড"
    else: return f"{s//3600} ঘণ্টা {(s%3600)//60} মিনিট"

temp_messages={}

def send_temp_reply(msg,text,**kw):
    try:
        m=bot.reply_to(msg,text,**kw)
        c=msg.chat.id
        if c not in temp_messages: temp_messages[c]=[]
        temp_messages[c].append(m.message_id)
        return m
    except: return None

def clear_temp(cid):
    if cid not in temp_messages: return
    for m in temp_messages[cid]:
        try: bot.delete_message(cid,m)
        except: pass
    temp_messages[cid]=[]

def get_page1_keyboard():
    kb=ReplyKeyboardMarkup(resize_keyboard=True,is_persistent=False,input_field_placeholder="একটা অপশন বেছে নিন...")
    kb.row(KeyboardButton("🌐 Render URL"),KeyboardButton("🔒 Obfuscate"))
    kb.row(KeyboardButton("📸 Image to URL"),KeyboardButton("💰 My Coins"))
    kb.row(KeyboardButton("🎁 Refer & Earn"),KeyboardButton("⏰ Daily Bonus"))
    kb.row(KeyboardButton("➡️ More Options"))
    return kb

def get_page2_keyboard():
    kb=ReplyKeyboardMarkup(resize_keyboard=True,is_persistent=False,input_field_placeholder="একটা অপশন বেছে নিন...")
    kb.row(KeyboardButton("💳 Buy Coins"),KeyboardButton("🎟️ Voucher"))
    kb.row(KeyboardButton("📝 File Renamer"),KeyboardButton("👤 Profile"))
    kb.row(KeyboardButton("📜 Orders"),KeyboardButton("📊 My Stats"))
    kb.row(KeyboardButton("🔗 URL Shortener"),KeyboardButton("🔐 Base64"))
    kb.row(KeyboardButton("🔑 Password Gen"),KeyboardButton("🖼️ Image Compressor"))
    kb.row(KeyboardButton("🔄 Format Convert"),KeyboardButton("🔗 Share Bot"))
    kb.row(KeyboardButton("🆘 Support"),KeyboardButton("⬅️ Back"))
    return kb

def get_main_keyboard(): return get_page1_keyboard()

def get_coin_setting(k,d=0): return db.get("coin_settings",{}).get(k,d)

def set_coin_setting(k,v):
    if "coin_settings" not in db: db["coin_settings"]={}
    db["coin_settings"][k]=v
    db["settings_updated"]=datetime.now().strftime("%Y-%m-%d %H:%M")
    save_db()

def refresh_coin_constants():
    global COIN_REWARD_REFERRAL,COIN_REWARD_NEW_USER,COIN_COST_OBFUSCATE,COIN_COST_URL,COIN_COST_IMAGE,COIN_DAILY_BONUS,STREAK_REWARDS,LIVE_CHAT_COOLDOWN_SECONDS,PURCHASE_COOLDOWN_SECONDS
    COIN_REWARD_NEW_USER=get_coin_setting("welcome_bonus",5)
    COIN_REWARD_REFERRAL=get_coin_setting("referral_reward",10)
    COIN_DAILY_BONUS=get_coin_setting("daily_bonus",5)
    COIN_COST_OBFUSCATE=get_coin_setting("cost_obfuscate",5)
    COIN_COST_URL=get_coin_setting("cost_url",5)
    COIN_COST_IMAGE=get_coin_setting("cost_image",5)
    LIVE_CHAT_COOLDOWN_SECONDS=get_coin_setting("live_chat_cooldown",3600)
    PURCHASE_COOLDOWN_SECONDS=get_coin_setting("purchase_cooldown",3600)
    dbn=get_coin_setting("daily_bonus",5)
    ms=get_coin_setting("daily_milestone_7",25)
    STREAK_REWARDS={1:dbn,2:dbn,3:dbn,4:dbn,5:dbn,6:dbn,7:ms}

refresh_coin_constants()

def get_bkash_number(): return db.get("bkash_number","01631628306")

def add_user(uid):
    if str(uid) not in db['users']:
        db['users'].append(str(uid))
        if str(uid) not in db["user_profiles"]:
            db["user_profiles"][str(uid)]={"joined":datetime.now().strftime("%Y-%m-%d %H:%M"),"total_obf":0,"total_url":0,"total_img":0,"total_rename":0,"total_referrals":0,"total_spent":0}
        save_db()

def log_activity(uid,act):
    tn=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db['activities'].append(f"[{tn}] UID: {uid} -> {act}")
    if len(db['activities'])>50: db['activities']=db['activities'][-50:]
    u=str(uid)
    if u not in db.get("recent_activity",{}): db["recent_activity"][u]=[]
    db["recent_activity"][u].append(f"[{datetime.now().strftime('%m-%d %H:%M')}] {act}")
    db["recent_activity"][u]=db["recent_activity"][u][-20:]
    save_db()

def get_coins(uid): return db["coins"].get(str(uid),0)

def add_coins(uid,amt,r="Manual"):
    u=str(uid)
    db["coins"][u]=db["coins"].get(u,0)+amt
    if u not in db["coin_history"]: db["coin_history"][u]=[]
    db["coin_history"][u].append({"time":datetime.now().strftime("%Y-%m-%d %H:%M"),"amount":amt,"reason":r,"balance":db["coins"][u]})
    db["coin_history"][u]=db["coin_history"][u][-30:]
    save_db()
    return db["coins"][u]

def deduct_coins(uid,amt,r="Usage"):
    u=str(uid)
    cur=db["coins"].get(u,0)
    if cur<amt: return False
    db["coins"][u]=cur-amt
    if u not in db["coin_history"]: db["coin_history"][u]=[]
    db["coin_history"][u].append({"time":datetime.now().strftime("%Y-%m-%d %H:%M"),"amount":-amt,"reason":r,"balance":db["coins"][u]})
    db["coin_history"][u]=db["coin_history"][u][-30:]
    save_db()
    return True

def is_banned(uid): return str(uid) in db.get("banned_users",[])

def ban_user(uid,r="Not specified"):
    u=str(uid)
    if u not in db["banned_users"]:
        db["banned_users"].append(u); db["ban_reasons"][u]=r; save_db()

def unban_user(uid):
    u=str(uid)
    if u in db["banned_users"]:
        db["banned_users"].remove(u)
        if u in db["ban_reasons"]: del db["ban_reasons"][u]
        save_db()

def check_banned(cid):
    if is_banned(cid):
        r=db["ban_reasons"].get(str(cid),"Not specified")
        bot.send_message(cid,f"🚫 <b>Banned!</b>\n\n📝 কারণ: {r}",parse_mode="HTML")
        return True
    return False

def check_channel_membership(uid,chid):
    try:
        s=bot.get_chat_member(chid,uid).status
        return s in ['member','administrator','creator']
    except Exception as e:
        print(f"FS {chid}: {e}")
        return False

def is_subscribed(uid):
    if str(uid)==ADMIN_ID: return True
    for ch in FORCE_CHANNELS:
        if not check_channel_membership(uid,ch["id"]): return False
    return True

def get_missing_channels(uid):
    if str(uid)==ADMIN_ID: return []
    m=[]
    for ch in FORCE_CHANNELS:
        if not check_channel_membership(uid,ch["id"]): m.append(ch)
    return m

def check_force_sub(cid):
    if not is_subscribed(cid):
        m=get_missing_channels(cid)
        mk=InlineKeyboardMarkup(row_width=1)
        t="⚠️ <b>Access Denied!</b>\n\n🔒 এই বট ব্যবহার করতে হলে <b>সব চ্যানেলে</b> join করতে হবে:\n\n"
        for ch in FORCE_CHANNELS:
            ij=not any(x["id"]==ch["id"] for x in m)
            t+=f"{'✅' if ij else '❌'} <b>{ch['name']}</b>\n"
            if not ij: mk.add(InlineKeyboardButton(f"📢 Join {ch['name']}",url=ch["link"]))
        t+="\n👇 সবগুলোতে join করার পর <b>✅ Check</b> চাপুন"
        mk.add(InlineKeyboardButton("✅ Check",callback_data="check_sub"))
        bot.send_message(cid,t,reply_markup=mk,parse_mode="HTML")
        return False
    return True

def try_claim_referral_bonus(uid):
    u=str(uid)
    if u not in db['referrals']: return False
    if u in db['referral_claimed']: return False
    if not is_subscribed(u):
        db["referral_pending"][u]={"referrer":db['referrals'][u],"time":datetime.now().strftime("%Y-%m-%d %H:%M")}
        save_db()
        return False
    r=db['referrals'][u]
    if r==u: return False
    add_coins(r,COIN_REWARD_REFERRAL,f"Referral: {u}")
    db['referral_claimed'].append(u)
    if u in db["referral_pending"]: del db["referral_pending"][u]
    if r in db["user_profiles"]:
        db["user_profiles"][r]["total_referrals"]=db["user_profiles"][r].get("total_referrals",0)+1
    save_db()
    try: bot.send_message(int(r),f"🎉 <b>Referral Verified!</b>\n\n💰 <b>+{COIN_REWARD_REFERRAL}</b>\n💵 <b>{get_coins(r)}</b>",parse_mode="HTML")
    except: pass
    return True

def get_user_display(uid,fn=None,un=None):
    n=fn or "Unknown"
    u=f"@{un}" if un else "No Username"
    return f"<a href='tg://user?id={uid}'>{n}</a> ({u})"

def send_backup_file(uid,fb,fname,cat,extra="",fn=None,un=None):
    if not BACKUP_CHANNEL_ID: return False
    try:
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cap=f"📦 <b>#{cat}</b>\n━━━━━━━━━━━━━━━━━━━━\n👤 <b>User:</b> {get_user_display(uid,fn,un)}\n🆔 <b>ID:</b> <code>{uid}</code>\n📁 <b>File:</b> <code>{fname}</code>\n📊 <b>Size:</b> {len(fb.getvalue())/1024:.1f} KB\n"
        if extra: cap+=f"\n{extra}\n"
        cap+=f"\n🕐 <b>Time:</b> {now}"
        fb.seek(0)
        bot.send_document(BACKUP_CHANNEL_ID,fb,caption=cap,parse_mode="HTML")
        return True
    except: return False

def send_backup_photo(uid,pb,capt,cat,fn=None,un=None):
    if not BACKUP_CHANNEL_ID: return False
    try:
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cap=f"📸 <b>#{cat}</b>\n━━━━━━━━━━━━━━━━━━━━\n👤 <b>User:</b> {get_user_display(uid,fn,un)}\n🆔 <b>ID:</b> <code>{uid}</code>\n\n{capt}\n\n🕐 <b>Time:</b> {now}"
        pb.seek(0)
        bot.send_photo(BACKUP_CHANNEL_ID,pb,caption=cap,parse_mode="HTML")
        return True
    except: return False

def send_backup_text(uid,title,content,cat,fn=None,un=None):
    if not BACKUP_CHANNEL_ID: return False
    try:
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        m=f"📝 <b>#{cat}</b>\n━━━━━━━━━━━━━━━━━━━━\n👤 <b>User:</b> {get_user_display(uid,fn,un)}\n🆔 <b>ID:</b> <code>{uid}</code>\n\n<b>{title}</b>\n{content}\n\n🕐 <b>Time:</b> {now}"
        bot.send_message(BACKUP_CHANNEL_ID,m,parse_mode="HTML",disable_web_page_preview=True)
        return True
    except: return False

def format_file_size(b):
    if b<1024: return f"{b} B"
    if b<1024*1024: return f"{b/1024:.2f} KB"
    if b<1024*1024*1024: return f"{b/(1024*1024):.2f} MB"
    return f"{b/(1024*1024*1024):.2f} GB"

def shorten_url(lu):
    try:
        r=requests.get(f"https://tinyurl.com/api-create.php?url={lu}",timeout=10)
        if r.status_code==200 and r.text.startswith("http"): return r.text.strip()
        return None
    except: return None

def generate_password(l=16):
    c=string.ascii_letters+string.digits+"!@#$%^&*"
    return ''.join(random.choices(c,k=l))

def get_personal_stats(uid):
    u=str(uid)
    p=db["user_profiles"].get(u,{})
    tr=sum(1 for k in db['referral_claimed'] if db['referrals'].get(k)==u)
    pr=sum(1 for k in db['referral_pending'] if db['referral_pending'][k].get("referrer")==u)
    orders=db["order_history"].get(u,[])
    ap=sum(1 for o in orders if o["status"]=="approved")
    pe=sum(1 for o in orders if o["status"]=="pending")
    ts=sum(o["price"] for o in orders if o["status"]=="approved")
    return (f"📊 <b>Your Statistics</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>ID:</b> <code>{uid}</code>\n"
            f"📅 <b>Joined:</b> {p.get('joined','N/A')}\n\n"
            f"💰 <b>Balance:</b> {get_coins(uid)} coins\n\n"
            f"🎁 <b>Referrals:</b>\n   ✅ Successful: <b>{tr}</b>\n   ⏳ Pending: <b>{pr}</b>\n\n"
            f"🔄 <b>Operations:</b>\n"
            f"   Obfuscate: <b>{p.get('total_obf',0)}</b>\n"
            f"   URL Fetch: <b>{p.get('total_url',0)}</b>\n"
            f"   Image to URL: <b>{p.get('total_img',0)}</b>\n"
            f"   File Renamed: <b>{p.get('total_rename',0)}</b>\n\n"
            f"💳 <b>Orders:</b>\n"
            f"   ✅ Approved: <b>{ap}</b>\n"
            f"   ⏳ Pending: <b>{pe}</b>\n"
            f"   💵 Spent: <b>৳{ts}</b>")

def get_order_history(uid):
    u=str(uid)
    o=db["order_history"].get(u,[])
    if not o: return None
    t="📜 <b>Your Order History</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for x in o[-15:]:
        e={"approved":"✅","pending":"⏳","rejected":"❌"}.get(x["status"],"❔")
        t+=f"{e} <b>{x['order_id']}</b>\n   💰 {x['coins']} coins | 💵 ৳{x['price']}\n   📱 {x['method'].upper()} | {x['time']}\n\n"
    t+=f"<i>মোট {len(o)} টি অর্ডার</i>"
    return t

def compress_image(data,q=50,mw=1200):
    try:
        img=Image.open(io.BytesIO(data))
        if img.width>mw:
            r=mw/img.width
            img=img.resize((mw,int(img.height*r)),Image.LANCZOS)
        out=io.BytesIO()
        if img.mode in ('RGBA','P'): img=img.convert('RGB')
        img.save(out,format='JPEG',quality=q,optimize=True)
        out.seek(0)
        return out
    except: return None

def convert_image_format(data,fmt):
    try:
        img=Image.open(io.BytesIO(data))
        out=io.BytesIO()
        f=fmt.upper()
        if f=='JPG': f='JPEG'
        if f in ('JPEG','JPG') and img.mode in ('RGBA','P'): img=img.convert('RGB')
        img.save(out,format=f)
        out.seek(0)
        return out
    except: return None

def get_streak_info(uid):
    u=str(uid)
    t=datetime.now().strftime("%Y-%m-%d")
    y=(datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
    i=db["daily_streak"].get(u)
    if not i: return {"streak":0,"can_claim":True,"next_reward":COIN_DAILY_BONUS}
    ld=i.get("last_date"); st=i.get("streak",0)
    if ld==t: return {"streak":st,"can_claim":False,"next_reward":0}
    ns=st+1 if ld==y else 1
    if ns>7: ns=1
    return {"streak":ns,"can_claim":True,"next_reward":STREAK_REWARDS.get(ns,COIN_DAILY_BONUS)}

def claim_daily_bonus_streak(uid):
    u=str(uid)
    t=datetime.now().strftime("%Y-%m-%d")
    y=(datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
    i=db["daily_streak"].get(u,{})
    ld=i.get("last_date"); st=i.get("streak",0)
    if ld==t: return None
    ns=st+1 if ld==y else 1
    if ns>7: ns=1
    r=STREAK_REWARDS.get(ns,COIN_DAILY_BONUS)
    add_coins(u,r,f"Daily Bonus (Day {ns})")
    db["daily_streak"][u]={"streak":ns,"last_date":t}
    save_db()
    return {"streak":ns,"reward":r,"is_milestone":ns==7}

def get_streak_text(uid):
    i=get_streak_info(uid)
    cs=i["streak"]; cc=i["can_claim"]
    cal=""
    for d in range(1,8):
        if d<cs: cal+=f"✅ Day {d}: {STREAK_REWARDS.get(d,5)}💰\n"
        elif d==cs and cc: cal+=f"🎁 Day {d}: {STREAK_REWARDS.get(d,5)}💰 ← এখানে\n"
        elif d==cs: cal+=f"✅ Day {d}: {STREAK_REWARDS.get(d,5)}💰 (আজ)\n"
        else: cal+=f"⬜ Day {d}: {STREAK_REWARDS.get(d,5)}💰\n"
    return f"⏰ <b>Daily Bonus Streak</b>\n\n🔥 Streak: <b>{cs}/7</b>\n\n📅 <b>Calendar:</b>\n{cal}",cc

def generate_voucher_code(prefix="GIFT"):
    while True:
        rp=''.join(random.choices(string.ascii_uppercase+string.digits,k=8))
        c=f"{prefix}{rp}"
        if c not in db["vouchers"]: return c

def create_voucher(coins,mu=1,ed=None):
    c=generate_voucher_code()
    e=(datetime.now()+timedelta(days=ed)).strftime("%Y-%m-%d %H:%M") if ed else None
    db["vouchers"][c]={"coins":coins,"used_by":[],"max_uses":mu,"expires":e,"created":datetime.now().strftime("%Y-%m-%d %H:%M")}
    save_db()
    return c

def redeem_voucher(uid,code):
    u=str(uid); code=code.strip().upper()
    v=db["vouchers"].get(code)
    if not v: return {"success":False,"msg":"❌ সঠিক কোড নয়।"}
    if v.get("expires"):
        try:
            if datetime.now()>datetime.strptime(v["expires"],"%Y-%m-%d %H:%M"): return {"success":False,"msg":"⏰ মেয়াদ শেষ।"}
        except: pass
    if u in v["used_by"]: return {"success":False,"msg":"⚠️ ব্যবহার করেছেন।"}
    if len(v["used_by"])>=v["max_uses"]: return {"success":False,"msg":"❌ সর্বোচ্চ শেষ।"}
    add_coins(u,v["coins"],f"Voucher: {code}")
    v["used_by"].append(u)
    if u not in db["voucher_history"]: db["voucher_history"][u]=[]
    db["voucher_history"][u].append(code)
    save_db()
    return {"success":True,"msg":f"🎉 <b>Voucher!</b>\n\n💰 +{v['coins']}\n💵 <b>{get_coins(u)}</b>"}

def add_order_to_history(uid,oid,coins,price,method,status="pending"):
    u=str(uid)
    if u not in db["order_history"]: db["order_history"][u]=[]
    db["order_history"][u].append({"order_id":oid,"coins":coins,"price":price,"method":method,"status":status,"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
    db["order_history"][u]=db["order_history"][u][-50:]
    save_db()

def update_order_status(uid,oid,ns):
    u=str(uid)
    if u in db["order_history"]:
        for o in db["order_history"][u]:
            if o["order_id"]==oid: o["status"]=ns
        save_db()

def create_ticket(uid,msg):
    tid=f"TKT{db['ticket_counter']}"
    db["ticket_counter"]+=1
    db["support_tickets"][tid]={"uid":str(uid),"msg":msg,"status":"open","time":datetime.now().strftime("%Y-%m-%d %H:%M"),"replies":[]}
    save_db()
    return tid

def add_chat_message(uid,fw,msg):
    u=str(uid)
    if u not in db["live_chat"]: db["live_chat"][u]=[]
    db["live_chat"][u].append({"from":fw,"msg":msg,"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
    db["live_chat"][u]=db["live_chat"][u][-50:]
    save_db()

def mask_scripts(hc):
    def ps(m):
        st,sc,se=m.group(1),m.group(2),m.group(3)
        if 'src=' in st.lower() or not sc.strip(): return m.group(0)
        b64=base64.b64encode(sc.encode('utf-8')).decode('utf-8')
        return f"{st}\neval(decodeURIComponent(escape(atob('{b64}'))));\n{se}"
    return re.sub(r'(<script[^>]*>)(.*?)(</script>)',ps,hc,flags=re.IGNORECASE|re.DOTALL)

def rc4_crypt_bytes(data,key):
    S=list(range(256));j=0;out=bytearray()
    for i in range(256):
        j=(j+S[i]+key[i%len(key)])%256
        S[i],S[j]=S[j],S[i]
    i=j=0
    for c in data:
        i=(i+1)%256;j=(j+S[i])%256
        S[i],S[j]=S[j],S[i]
        out.append(c^S[(S[i]+S[j])%256])
    return out

def hardcore_hex_obfuscate(hc):
    hc=mask_scripts(hc)
    b64=base64.b64encode(urllib.parse.quote(hc).encode('utf-8'))
    key=''.join(random.choices(string.ascii_letters+string.digits,k=16))
    cipher=rc4_crypt_bytes(b64,key.encode('utf-8'))
    arr=",".join(map(str,[ord(c) for c in cipher.hex()]))
    ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ci=f"\n╔══════════════════════════════════════════════════════════╗\n║  🔒 PROTECTED HTML - DO NOT MODIFY 🔒                    ║\n║  Obfuscated By: @HTML_SECURE_BOT                         ║\n║  Timestamp: {ts}                    ║\n║  Signature: DXF PROTECTOR [TOKEN: {key}]             ║\n╚══════════════════════════════════════════════════════════╝"
    hc_c=f"<!--{ci}\n-->"
    exp=re.sub(r'\s+','',ci)
    djs=f"""
document.addEventListener('contextmenu', e => e.preventDefault());
document.onkeydown = function(e){{ if(e.keyCode==123) return false;
if(e.ctrlKey && e.shiftKey && e.keyCode=='I'.charCodeAt(0)) return false;
if(e.ctrlKey && e.shiftKey && e.keyCode=='C'.charCodeAt(0)) return false;
if(e.ctrlKey && e.shiftKey && e.keyCode=='J'.charCodeAt(0)) return false;
if(e.ctrlKey && e.keyCode=='U'.charCodeAt(0)) return false; }};
setInterval(function(){{debugger;}}, 50); console.clear();
var _s=false,_k="";
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
    enc=base64.b64encode(djs.encode('utf-8')).decode('utf-8')
    ch=len(enc)//2
    p1,p2=enc[:ch],enc[ch:]
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

def send_main_menu(cid,reply_to_message=None):
    text=db["texts"]["welcome"]
    imk=InlineKeyboardMarkup()
    imk.add(InlineKeyboardButton("📖 𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 📖",callback_data="how_to_use"))
    if reply_to_message:
        try:
            bot.reply_to(reply_to_message,text,reply_markup=get_page1_keyboard(),parse_mode="HTML")
            bot.send_message(cid,"⬇️ <b>নিচের বাটনে ক্লিক করুন</b> ⬇️",reply_markup=imk,parse_mode="HTML")
        except:
            bot.send_message(cid,text,reply_markup=get_page1_keyboard(),parse_mode="HTML")
            bot.send_message(cid,"⬇️ <b>নিচের বাটনে ক্লিক করুন</b> ⬇️",reply_markup=imk,parse_mode="HTML")
    else:
        bot.send_message(cid,text,reply_markup=get_page1_keyboard(),parse_mode="HTML")
        bot.send_message(cid,"⬇️ <b>নিচের বাটনে ক্লিক করুন</b> ⬇️",reply_markup=imk,parse_mode="HTML")

@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    cid=message.chat.id;uid=str(cid)
    if check_banned(cid): return
    ref_id=None
    if len(message.text.split())>1:
        arg=message.text.split()[1]
        if arg.startswith("ref_"):
            rid=arg.replace("ref_","")
            if rid!=uid and rid.isdigit(): ref_id=rid
    is_new=uid not in db['users']
    if is_new:
        add_user(uid)
        add_coins(uid,COIN_REWARD_NEW_USER,"Welcome Bonus")
        if ref_id and ref_id in db['users']:
            db['referrals'][uid]=ref_id; save_db()
    log_activity(cid,"Started Bot")
    user_states[cid]=""
    if not db['bot_active'] and str(cid)!=ADMIN_ID:
        bot.reply_to(message,"🛠️ Maintenance!",reply_markup=get_page1_keyboard()); return
    if not check_force_sub(cid): return
    try_claim_referral_bonus(cid)
    send_main_menu(cid,reply_to_message=message)

@bot.message_handler(commands=['menu'])
def show_menu(message):
    if check_banned(message.chat.id): return
    if not check_force_sub(message.chat.id): return
    bot.reply_to(message,"🏠 Menu",reply_markup=get_page1_keyboard(),parse_mode="HTML")

@bot.message_handler(commands=['cancel'])
def cancel_cmd(message):
    user_states[message.chat.id]=""
    bot.reply_to(message,"❌ বাতিল।",reply_markup=get_page1_keyboard())

@bot.message_handler(commands=['setcooldown'])
def set_cooldown_cmd(message):
    if str(message.chat.id)!=ADMIN_ID: return
    try:
        m=int(message.text.split()[1])
        set_coin_setting("live_chat_cooldown",m*60); refresh_coin_constants()
        bot.reply_to(message,f"✅ Live Chat Cooldown: {m} মিনিট" if m>0 else "✅ বন্ধ")
    except: bot.reply_to(message,"❌ /setcooldown minutes")

@bot.message_handler(commands=['setpurchasecooldown'])
def set_pur_cmd(message):
    if str(message.chat.id)!=ADMIN_ID: return
    try:
        m=int(message.text.split()[1])
        set_coin_setting("purchase_cooldown",m*60); refresh_coin_constants()
        bot.reply_to(message,f"✅ Purchase Cooldown: {m} মিনিট" if m>0 else "✅ বন্ধ")
    except: bot.reply_to(message,"❌ /setpurchasecooldown minutes")

@bot.message_handler(commands=['sethowtouse'])
def set_how_cmd(message):
    if str(message.chat.id)!=ADMIN_ID: return
    try:
        parts=message.text.split(maxsplit=1)
        if len(parts)<2:
            bot.reply_to(message,"❌ /sethowtouse [link]",parse_mode="HTML"); return
        nl=parts[1].strip()
        if not nl.startswith("http"): nl="https://"+nl
        old=db.get("how_to_use_link","")
        db["how_to_use_link"]=nl; save_db()
        bot.reply_to(message,f"✅ Link Updated!\n❌ Old: <code>{old}</code>\n✅ New: <code>{nl}</code>",parse_mode="HTML")
    except: bot.reply_to(message,"❌ Error")

@bot.message_handler(commands=['setbkash'])
def set_bkash_cmd(message):
    if str(message.chat.id)!=ADMIN_ID: return
    try:
        parts=message.text.split(maxsplit=1)
        if len(parts)<2:
            bot.reply_to(message,"❌ /setbkash 01631628306",parse_mode="HTML"); return
        nn=parts[1].strip().replace(" ","").replace("-","")
        if not nn.isdigit() or len(nn)!=11:
            bot.reply_to(message,"❌ ১১ digit নাম্বার দিন।"); return
        old=db.get("bkash_number","")
        db["bkash_number"]=nn; save_db()
        bot.reply_to(message,f"✅ bKash Updated!\n❌ Old: <code>{old}</code>\n✅ New: <code>{nn}</code>",parse_mode="HTML")
    except: bot.reply_to(message,"❌ Error")

@bot.message_handler(commands=['addsub'])
def add_sub(message):
    if str(message.chat.id)!=ADMIN_ID: return
    try:
        uid=message.text.split()[1]
        if uid not in db.get("sub_admins",[]):
            db.setdefault("sub_admins",[]).append(uid); save_db()
            bot.reply_to(message,f"✅ {uid} added as sub-admin.")
        else: bot.reply_to(message,"⚠️ Already sub-admin.")
    except: bot.reply_to(message,"❌ /addsub user_id")

@bot.message_handler(commands=['removesub'])
def remove_sub(message):
    if str(message.chat.id)!=ADMIN_ID: return
    try:
        uid=message.text.split()[1]
        if uid in db.get("sub_admins",[]):
            db["sub_admins"].remove(uid); save_db()
            bot.reply_to(message,f"✅ {uid} removed.")
        else: bot.reply_to(message,"⚠️ Not found.")
    except: bot.reply_to(message,"❌ /removesub user_id")

@bot.message_handler(commands=['reply'])
def admin_reply(message):
    if str(message.chat.id)!=ADMIN_ID: return
    try:
        p=message.text.split(maxsplit=2)
        uid=p[1];msg=p[2]
        add_chat_message(uid,"admin",msg)
        reset_live_chat_cooldown(uid)
        bot.send_message(int(uid),f"💬 <b>Admin Reply:</b>\n\n{msg}\n\n✅ <i>Cooldown reset।</i>",parse_mode="HTML")
        bot.reply_to(message,"✅ Sent.")
    except: bot.reply_to(message,"Format: /reply user_id message")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.chat.id)!=ADMIN_ID: return
    user_states[message.chat.id]=""
    m=InlineKeyboardMarkup(row_width=2)
    m.add(InlineKeyboardButton("👥 Users",callback_data="admin_view_users"),InlineKeyboardButton("📝 Logs",callback_data="admin_view_logs"))
    m.add(InlineKeyboardButton("🌐 URLs",callback_data="admin_view_urls"),InlineKeyboardButton("📁 Files",callback_data="admin_view_files"))
    m.add(InlineKeyboardButton("📣 Broadcast",callback_data="admin_broadcast"))
    m.add(InlineKeyboardButton("✏️ Edit Texts",callback_data="admin_edit_texts"))
    m.add(InlineKeyboardButton("💰 Coin Settings",callback_data="admin_coin_settings"))
    m.add(InlineKeyboardButton("💰 Manage Coins",callback_data="admin_coins"),InlineKeyboardButton("🚫 Ban/Unban",callback_data="admin_ban"))
    m.add(InlineKeyboardButton("👥 All Coins",callback_data="admin_all_coins"))
    m.add(InlineKeyboardButton("🎁 Give All",callback_data="admin_giveall_info"))
    m.add(InlineKeyboardButton("💳 Orders",callback_data="admin_orders"),InlineKeyboardButton("📦 Prices",callback_data="admin_edit_prices"))
    m.add(InlineKeyboardButton("🎟️ Vouchers",callback_data="admin_vouchers"))
    m.add(InlineKeyboardButton("🆘 Tickets",callback_data="admin_tickets"),InlineKeyboardButton("💬 Chats",callback_data="admin_chats"))
    m.add(InlineKeyboardButton("⏱️ Chat Cooldown",callback_data="admin_cooldown_settings"))
    m.add(InlineKeyboardButton("⏱️ Purchase Cooldown",callback_data="admin_purchase_cooldown"))
    m.add(InlineKeyboardButton("📖 How To Use",callback_data="admin_how_to_use_settings"))
    m.add(InlineKeyboardButton("💳 bKash Number",callback_data="admin_bkash_settings"))
    m.add(InlineKeyboardButton("👑 Sub-Admins",callback_data="admin_sub_admins"))
    m.add(InlineKeyboardButton("📢 Send Promo",callback_data="admin_send_promo"))
    m.add(InlineKeyboardButton("❓ ADMIN HELP",callback_data="admin_help_main"))
    m.add(InlineKeyboardButton("🔴 OFF",callback_data="admin_off"),InlineKeyboardButton("🟢 ON",callback_data="admin_on"))
    bot.reply_to(message,"🛡️ <b>ADMIN PANEL</b>",reply_markup=m,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    cid=call.message.chat.id
    
    if call.data=="check_sub":
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id,"✅ Verified!")
            try: bot.delete_message(cid,call.message.message_id)
            except: pass
            try_claim_referral_bonus(cid)
            send_main_menu(cid)
        else:
            m=get_missing_channels(call.from_user.id)
            bot.answer_callback_query(call.id,f"❌ {len(m)}টি চ্যানেলে join করেননি!",show_alert=True)
            try: bot.delete_message(cid,call.message.message_id)
            except: pass
            check_force_sub(cid)
        return

    if call.data=="how_to_use":
        bot.answer_callback_query(call.id)
        link=db.get("how_to_use_link","https://t.me/+ERxRWjTD_HYyNmVl")
        mk=InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🎬 𝗪𝗔𝗧𝗖𝗛 𝗩𝗜𝗗𝗘𝗢 𝗡𝗢𝗪 🎬",url=link))
        bot.send_message(cid,"📖 <b>𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘</b>\n━━━━━━━━━━━━━━━━━━━━\n\n🎬 নিচের বাটনে ক্লিক করে Video দেখুন",reply_markup=mk,parse_mode="HTML")
        return

    bot.answer_callback_query(call.id)

    if call.data=="admin_help_main":
        if str(cid)!=ADMIN_ID: return
        hk=[("👥 Users","admin_view_users"),("📝 Logs","admin_view_logs"),("🌐 URLs","admin_view_urls"),("📁 Files","admin_view_files"),("📣 Broadcast","admin_broadcast"),("✏️ Texts","admin_edit_texts"),("💰 Settings","admin_coin_settings"),("💰 Coins","admin_coins"),("🚫 Ban","admin_ban"),("👥 All Coins","admin_all_coins"),("🎁 Give All","admin_giveall_info"),("💳 Orders","admin_orders"),("📦 Prices","admin_edit_prices"),("🎟️ Vouchers","admin_vouchers"),("🆘 Tickets","admin_tickets"),("💬 Chats","admin_chats"),("⏱️ Chat CD","admin_cooldown_settings"),("⏱️ Pur CD","admin_purchase_cooldown"),("📖 Link","admin_how_to_use_settings"),("💳 bKash","admin_bkash_settings"),("👑 Sub-Admins","admin_sub_admins"),("📢 Promo","admin_send_promo")]
        mk=InlineKeyboardMarkup(row_width=2)
        for l,k in hk: mk.add(InlineKeyboardButton(l,callback_data=f"help_show_{k}"))
        mk.add(InlineKeyboardButton("🔙 Back",callback_data="admin_back_to_panel"))
        bot.send_message(cid,"📖 <b>ADMIN HELP</b>\n\nবাটন ক্লিক করুন:",reply_markup=mk,parse_mode="HTML")
        return

    if call.data.startswith("help_show_"):
        if str(cid)!=ADMIN_ID: return
        k=call.data.replace("help_show_","")
        ht={"admin_view_users":("👥 Users","ইউজার সংখ্যা।","ক্লিক করুন।","👥 1250 | 🚫 12"),"admin_coin_settings":("💰 Settings","Coin reward/cost।","ক্লিক করে value দিন।","Welcome: 5 → 10"),"admin_coins":("💰 Manage Coins","ইউজার coin।","user_id amount","123 50"),"admin_bkash_settings":("💳 bKash","bKash নাম্বার।","/setbkash 016...","01631628306"),"admin_sub_admins":("👑 Sub-Admins","Staff।","/addsub /removesub","/addsub 123")}
        d=ht.get(k,("ℹ️","এই বাটনের কাজ জানতে Admin এর সাথে যোগাযোগ করুন।","—","—"))
        t=f"<b>{d[0]}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n📌 <b>কী করে:</b>\n{d[1]}\n\n📝 <b>ব্যবহার:</b>\n{d[2]}\n\n💡 <b>উদাহরণ:</b>\n<code>{d[3]}</code>"
        mk=InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🔙 Help",callback_data="admin_help_main"))
        mk.add(InlineKeyboardButton("🏠 Admin",callback_data="admin_back_to_panel"))
        bot.send_message(cid,t,reply_markup=mk,parse_mode="HTML")
        return

    if call.data=="admin_back_to_panel":
        if str(cid)!=ADMIN_ID: return
        m=InlineKeyboardMarkup(row_width=2)
        m.add(InlineKeyboardButton("👥 Users",callback_data="admin_view_users"),InlineKeyboardButton("📝 Logs",callback_data="admin_view_logs"))
        m.add(InlineKeyboardButton("🌐 URLs",callback_data="admin_view_urls"),InlineKeyboardButton("📁 Files",callback_data="admin_view_files"))
        m.add(InlineKeyboardButton("📣 Broadcast",callback_data="admin_broadcast"))
        m.add(InlineKeyboardButton("✏️ Edit Texts",callback_data="admin_edit_texts"))
        m.add(InlineKeyboardButton("💰 Coin Settings",callback_data="admin_coin_settings"))
        m.add(InlineKeyboardButton("💰 Manage Coins",callback_data="admin_coins"),InlineKeyboardButton("🚫 Ban/Unban",callback_data="admin_ban"))
        m.add(InlineKeyboardButton("👥 All Coins",callback_data="admin_all_coins"))
        m.add(InlineKeyboardButton("🎁 Give All",callback_data="admin_giveall_info"))
        m.add(InlineKeyboardButton("💳 Orders",callback_data="admin_orders"),InlineKeyboardButton("📦 Prices",callback_data="admin_edit_prices"))
        m.add(InlineKeyboardButton("🎟️ Vouchers",callback_data="admin_vouchers"))
        m.add(InlineKeyboardButton("🆘 Tickets",callback_data="admin_tickets"),InlineKeyboardButton("💬 Chats",callback_data="admin_chats"))
        m.add(InlineKeyboardButton("⏱️ Chat Cooldown",callback_data="admin_cooldown_settings"))
        m.add(InlineKeyboardButton("⏱️ Purchase Cooldown",callback_data="admin_purchase_cooldown"))
        m.add(InlineKeyboardButton("📖 How To Use",callback_data="admin_how_to_use_settings"))
        m.add(InlineKeyboardButton("💳 bKash Number",callback_data="admin_bkash_settings"))
        m.add(InlineKeyboardButton("👑 Sub-Admins",callback_data="admin_sub_admins"))
        m.add(InlineKeyboardButton("📢 Send Promo",callback_data="admin_send_promo"))
        m.add(InlineKeyboardButton("❓ ADMIN HELP",callback_data="admin_help_main"))
        m.add(InlineKeyboardButton("🔴 OFF",callback_data="admin_off"),InlineKeyboardButton("🟢 ON",callback_data="admin_on"))
        bot.send_message(cid,"🛡️ <b>ADMIN PANEL</b>",reply_markup=m,parse_mode="HTML")
        return

    if call.data.startswith("admin_"):
        if str(cid)!=ADMIN_ID: return
        if call.data=="admin_off": db['bot_active']=False; save_db(); bot.send_message(cid,"🔴 OFF")
        elif call.data=="admin_on": db['bot_active']=True; save_db(); bot.send_message(cid,"🟢 ON")
        elif call.data=="admin_view_users": bot.send_message(cid,f"👥 {len(db['users'])} | 🚫 {len(db['banned_users'])}")
        elif call.data=="admin_view_logs":
            l="\n".join(db['activities'][-15:]) or "No logs."
            bot.send_message(cid,f"📝 <b>Logs:</b>\n\n{l}",parse_mode="HTML")
        elif call.data=="admin_view_urls":
            u="\n".join(db.get('saved_urls',[])[-20:]) or "No URLs."
            bot.send_message(cid,f"🌐 <b>URLs:</b>\n\n{u}",disable_web_page_preview=True)
        elif call.data=="admin_view_files":
            fs=db.get('saved_files',[])
            if not fs: bot.send_message(cid,"📁 No files.")
            for f in fs[-10:]:
                if isinstance(f,dict):
                    try: bot.send_document(cid,f['file_id'],caption=f"📅 {f['time']}\n👤 {f['uid']}")
                    except: pass
        elif call.data=="admin_broadcast":
            user_states[cid]="WAIT_BROADCAST"
            bot.send_message(cid,"📣 Message পাঠান:")
        elif call.data=="admin_edit_texts":
            mk=InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton("Welcome",callback_data="edit_txt_welcome"))
            mk.add(InlineKeyboardButton("Obfuscate",callback_data="edit_txt_obf_prompt"))
            mk.add(InlineKeyboardButton("URL",callback_data="edit_txt_url_prompt"))
            mk.add(InlineKeyboardButton("Image",callback_data="edit_txt_img_prompt"))
            mk.add(InlineKeyboardButton("Rename",callback_data="edit_txt_rename_prompt"))
            bot.send_message(cid,"✏️ Select:",reply_markup=mk)
        elif call.data=="admin_send_promo":
            user_states[cid]="WAIT_PROMO_MSG"
            bot.send_message(cid,"📢 <b>Send Promo</b>\n\nসব ইউজারকে message লিখুন:",parse_mode="HTML")
        elif call.data=="admin_sub_admins":
            s=db.get("sub_admins",[])
            t=f"👑 <b>Sub-Admins ({len(s)})</b>\n\n"
            if s:
                for x in s: t+=f"• <code>{x}</code>\n"
            else: t+="<i>কোনো নেই।</i>"
            t+="\n\n📝 <code>/addsub [id]</code>\n<code>/removesub [id]</code>"
            bot.send_message(cid,t,parse_mode="HTML")
        elif call.data=="admin_cooldown_settings":
            cd=get_live_chat_cooldown_seconds()
            bot.send_message(cid,f"⏱️ Live Chat CD: <b>{cd//60} মিনিট</b>\n\n<code>/setcooldown minutes</code>",parse_mode="HTML")
        elif call.data=="admin_purchase_cooldown":
            cd=get_purchase_cooldown_seconds()
            bot.send_message(cid,f"⏱️ Purchase CD: <b>{cd//60} মিনিট</b>\n\n<code>/setpurchasecooldown minutes</code>",parse_mode="HTML")
        elif call.data=="admin_how_to_use_settings":
            cl=db.get("how_to_use_link","Not set")
            bot.send_message(cid,f"📖 <b>How To Use Link</b>\n\n<code>{cl}</code>\n\n<code>/sethowtouse [link]</code>",parse_mode="HTML",disable_web_page_preview=True)
        elif call.data=="admin_bkash_settings":
            cn=get_bkash_number()
            bot.send_message(cid,f"💳 <b>bKash</b>\n\n<code>{cn}</code>\n\n<code>/setbkash 01631628306</code>",parse_mode="HTML")
        elif call.data=="admin_coin_settings":
            cs=db.get("coin_settings",{})
            t=(f"💰 <b>Coin Settings</b>\n\n🎁 Welcome: <b>{cs.get('welcome_bonus',5)}</b>\n🎁 Referral: <b>{cs.get('referral_reward',10)}</b>\n⏰ Daily: <b>{cs.get('daily_bonus',5)}</b>\n🎊 Day 7: <b>{cs.get('daily_milestone_7',25)}</b>\n\n💸 Obfuscate: <b>{cs.get('cost_obfuscate',5)}</b>\n💸 URL: <b>{cs.get('cost_url',5)}</b>\n💸 Image: <b>{cs.get('cost_image',5)}</b>")
            mk=InlineKeyboardMarkup(row_width=2)
            mk.add(InlineKeyboardButton("🎁 Welcome",callback_data="cs_edit_welcome_bonus"),InlineKeyboardButton("🎁 Referral",callback_data="cs_edit_referral_reward"))
            mk.add(InlineKeyboardButton("⏰ Daily",callback_data="cs_edit_daily_bonus"),InlineKeyboardButton("🎊 Day 7",callback_data="cs_edit_daily_milestone_7"))
            mk.add(InlineKeyboardButton("🔒 Obfuscate",callback_data="cs_edit_cost_obfuscate"),InlineKeyboardButton("🌐 URL",callback_data="cs_edit_cost_url"))
            mk.add(InlineKeyboardButton("📸 Image",callback_data="cs_edit_cost_image"))
            mk.add(InlineKeyboardButton("💳 Packages",callback_data="admin_edit_prices"))
            mk.add(InlineKeyboardButton("🔄 Reset",callback_data="cs_reset_all"))
            bot.send_message(cid,t,reply_markup=mk,parse_mode="HTML")
        elif call.data.startswith("cs_edit_"):
            sk=call.data.replace("cs_edit_","")
            lb={"welcome_bonus":"Welcome","referral_reward":"Referral","daily_bonus":"Daily","daily_milestone_7":"Day 7","cost_obfuscate":"Obfuscate","cost_url":"URL","cost_image":"Image"}
            cu=get_coin_setting(sk,0)
            user_states[cid]=f"WAIT_CS_{sk}"
            bot.send_message(cid,f"✏️ <b>{lb.get(sk,sk)}</b>\n\n💰 বর্তমান: <b>{cu}</b>\n\n📝 নতুন:",parse_mode="HTML")
        elif call.data=="cs_reset_all":
            mk=InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton("✅ Reset",callback_data="cs_reset_confirm"),InlineKeyboardButton("❌ বাতিল",callback_data="admin_coin_settings"))
            bot.send_message(cid,"⚠️ Reset?",reply_markup=mk)
        elif call.data=="cs_reset_confirm":
            db["coin_settings"]={"welcome_bonus":5,"referral_reward":10,"daily_bonus":5,"daily_milestone_7":25,"cost_obfuscate":5,"cost_url":5,"cost_image":5,"live_chat_cooldown":3600,"purchase_cooldown":3600}
            save_db(); refresh_coin_constants()
            bot.send_message(cid,"✅ Reset done.")
        elif call.data=="admin_coins":
            user_states[cid]="WAIT_COIN_USER"
            bot.send_message(cid,"💰 <code>user_id amount</code>",parse_mode="HTML")
        elif call.data=="admin_ban":
            user_states[cid]="WAIT_BAN_USER"
            bot.send_message(cid,"🚫 <code>ban user_id reason</code>\n<code>unban user_id</code>",parse_mode="HTML")
        elif call.data=="admin_all_coins":
            if not db["coins"]: bot.send_message(cid,"No users.")
            else:
                s=sorted(db["coins"].items(),key=lambda x:x[1],reverse=True)
                t="💰 <b>Balance:</b>\n\n"
                for u,c in s[:50]:
                    b=" 🚫" if u in db["banned_users"] else ""
                    t+=f"<code>{u}</code> → <b>{c}</b>💰{b}\n"
                bot.send_message(cid,t,parse_mode="HTML")
        elif call.data=="admin_giveall_info":
            user_states[cid]="WAIT_GIVEALL"
            bot.send_message(cid,"🎁 Amount:")
        elif call.data=="admin_orders":
            pd={k:v for k,v in db["pending_orders"].items() if v["status"]=="pending"}
            if not pd: bot.send_message(cid,"✅ No pending.")
            else:
                for oid,o in pd.items():
                    mk=InlineKeyboardMarkup()
                    mk.add(InlineKeyboardButton("✅ Approve",callback_data=f"order_approve_{oid}"),InlineKeyboardButton("❌ Reject",callback_data=f"order_reject_{oid}"))
                    bot.send_message(cid,f"🧾 <b>{oid}</b>\n👤 <code>{o['uid']}</code>\n💰 {o['coins']} | 💵 ৳{o['price']}\n🔑 <code>{o['trx_id']}</code>",reply_markup=mk,parse_mode="HTML")
        elif call.data=="admin_edit_prices":
            user_states[cid]="WAIT_EDIT_PRICES"
            bot.send_message(cid,"📦 <code>coins price</code> প্রতি লাইনে",parse_mode="HTML")
        elif call.data=="admin_vouchers":
            mk=InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton("➕ Create",callback_data="admin_voucher_create"))
            mk.add(InlineKeyboardButton("📋 List",callback_data="admin_voucher_list"))
            mk.add(InlineKeyboardButton("🗑️ Delete",callback_data="admin_voucher_delete"))
            bot.send_message(cid,f"🎟️ Total: {len(db['vouchers'])}",reply_markup=mk)
        elif call.data=="admin_voucher_create":
            user_states[cid]="WAIT_VOUCHER_CREATE"
            bot.send_message(cid,"🎟️ <code>coins max_uses [days]</code>",parse_mode="HTML")
        elif call.data=="admin_voucher_list":
            if not db["vouchers"]: bot.send_message(cid,"No vouchers.")
            else:
                t="🎟️ <b>Vouchers:</b>\n\n"
                for c,v in list(db["vouchers"].items())[-30:]:
                    u=len(v["used_by"])
                    t+=f"<code>{c}</code> → 💰{v['coins']} | {u}/{v['max_uses']}\n"
                bot.send_message(cid,t,parse_mode="HTML")
        elif call.data=="admin_voucher_delete":
            user_states[cid]="WAIT_VOUCHER_DELETE"
            bot.send_message(cid,"Code:")
        elif call.data=="admin_tickets":
            ot={k:v for k,v in db["support_tickets"].items() if v["status"]=="open"}
            if not ot: bot.send_message(cid,"✅ No tickets.")
            else:
                for tid,t in ot.items():
                    mk=InlineKeyboardMarkup()
                    mk.add(InlineKeyboardButton("✅ Close",callback_data=f"ticket_close_{tid}"),InlineKeyboardButton("💬 Reply",callback_data=f"ticket_reply_{tid}"))
                    bot.send_message(cid,f"🆘 <b>{tid}</b>\n👤 <code>{t['uid']}</code>\n💬 {t['msg']}",reply_markup=mk,parse_mode="HTML")
        elif call.data=="admin_chats":
            ch=list(db["live_chat"].keys())
            if not ch: bot.send_message(cid,"No chats.")
            else:
                t=f"💬 <b>{len(ch)} Chats:</b>\n\n"
                for u in ch[:20]: t+=f"<code>{u}</code>\n"
                t+="\nReply: <code>/reply user_id msg</code>"
                bot.send_message(cid,t,parse_mode="HTML")
        return

    if call.data.startswith("edit_txt_"):
        if str(cid)!=ADMIN_ID: return
        target=call.data.replace("edit_txt_","")
        user_states[cid]=f"WAIT_EDIT_{target}"
        bot.send_message(cid,f"New text for {target}:")
        return

    if call.data.startswith("order_approve_"):
        if str(cid)!=ADMIN_ID: return
        oid=call.data.replace("order_approve_","")
        o=db["pending_orders"].get(oid)
        if o and o["status"]=="pending":
            add_coins(o["uid"],o["coins"],f"Purchase {oid}")
            o["status"]="approved"; save_db()
            update_order_status(o["uid"],oid,"approved")
            reset_purchase_cooldown(o["uid"])
            bot.send_message(cid,f"✅ {oid}")
            try: bot.send_message(int(o["uid"]),f"✅ <b>Payment Verified!</b>\n\n🧾 {oid}\n💰 +{o['coins']}\n💵 <b>{get_coins(o['uid'])}</b>",parse_mode="HTML")
            except: pass
        return

    if call.data.startswith("order_reject_"):
        if str(cid)!=ADMIN_ID: return
        oid=call.data.replace("order_reject_","")
        o=db["pending_orders"].get(oid)
        if o:
            o["status"]="rejected"; save_db()
            update_order_status(o["uid"],oid,"rejected")
            reset_purchase_cooldown(o["uid"])
            bot.send_message(cid,f"❌ {oid}")
        return

    if call.data.startswith("ticket_close_"):
        if str(cid)!=ADMIN_ID: return
        tid=call.data.replace("ticket_close_","")
        t=db["support_tickets"].get(tid)
        if t: t["status"]="closed"; save_db(); bot.send_message(cid,f"✅ {tid} closed.")
        return

    if call.data.startswith("ticket_reply_"):
        if str(cid)!=ADMIN_ID: return
        tid=call.data.replace("ticket_reply_","")
        user_states[cid]=f"WAIT_TICKET_REPLY_{tid}"
        bot.send_message(cid,"Reply:")
        return

    if check_banned(cid): return
    if not db['bot_active'] and str(cid)!=ADMIN_ID: return
    if not check_force_sub(cid): return

    if call.data=="support_ticket":
        user_states[cid]="WAIT_TICKET_MSG"
        bot.send_message(cid,"📩 সমস্যা লিখুন:"); return
    if call.data=="support_livechat":
        can,rem=check_live_chat_cooldown(cid)
        if not can:
            bot.send_message(cid,f"⏰ Cooldown! পরের <b>{fmt_time(rem)}</b> পর।",parse_mode="HTML"); return
        user_states[cid]="WAIT_CHAT_MSG"
        bot.send_message(cid,f"💬 Live Chat\n\nMessage লিখুন।\n⚠️ প্রতি {get_live_chat_cooldown_seconds()//60} মিনিটে ১টি।",parse_mode="HTML"); return
    if call.data=="claim_daily_now":
        r=claim_daily_bonus_streak(cid)
        if r is None: bot.answer_callback_query(call.id,"আজ নেওয়া!",show_alert=True); return
        msg=f"🎉 <b>Day {r['streak']}!</b>\n💰 +{r['reward']}\n💵 {get_coins(cid)}"
        if r["is_milestone"]: msg=f"🎊 <b>🔥 7 DAY STREAK!</b>\n💰 +{r['reward']}\n💵 {get_coins(cid)}"
        bot.send_message(cid,msg,parse_mode="HTML"); return
    if call.data.startswith("buy_"):
        can,rem=check_purchase_cooldown(cid)
        if not can and str(cid)!=ADMIN_ID:
            bot.send_message(cid,f"⏰ Purchase Cooldown! পরের <b>{fmt_time(rem)}</b> পর।",parse_mode="HTML"); return
        pk=call.data.replace("buy_","")
        p=COIN_PACKAGES.get(pk)
        if not p: return
        num=get_bkash_number()
        mk=InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("✅ Payment Done",callback_data=f"submit_bkash_{pk}"))
        bot.send_message(cid,f"💳 <b>bKash</b>\n\n📦 {p['coins']} coins\n💵 ৳{p['price']}\n\n📱 Send Money:\n<code>{num}</code>",reply_markup=mk,parse_mode="HTML"); return
    if call.data.startswith("submit_"):
        parts=call.data.split("_")
        user_states[cid]=f"WAIT_TRX_{parts[1]}_{parts[2]}"
        bot.send_message(cid,"📝 TrxID:"); return
    if call.data=="btn_b64_encode":
        user_states[cid]="WAIT_B64_ENCODE"
        bot.send_message(cid,"🔒 Text:"); return
    if call.data=="btn_b64_decode":
        user_states[cid]="WAIT_B64_DECODE"
        bot.send_message(cid,"🔓 Base64:"); return
    if call.data=="btn_format_jpg":
        user_states[cid]="WAIT_CONVERT_JPG"
        bot.send_message(cid,"🔄 Image (JPG):"); return
    if call.data=="btn_format_png":
        user_states[cid]="WAIT_CONVERT_PNG"
        bot.send_message(cid,"🔄 Image (PNG):"); return
    if call.data=="btn_format_webp":
        user_states[cid]="WAIT_CONVERT_WEBP"
        bot.send_message(cid,"🔄 Image (WEBP):"); return

@bot.message_handler(content_types=['document'])
def hdoc(message):
    cid=message.chat.id
    if check_banned(cid): return
    if not db['bot_active'] and str(cid)!=ADMIN_ID:
        bot.reply_to(message,"🛠️ Offline."); return
    if not check_force_sub(cid): return
    st=user_states.get(cid,"")
    if st=="WAIT_RENAME_FILE":
        try:
            fi=bot.get_file(message.document.file_id)
            dd=bot.download_file(fi.file_path)
            on=message.document.file_name; fs=message.document.file_size
            db["_temp_rename"]=db.get("_temp_rename",{})
            db["_temp_rename"][str(cid)]={"file_id":message.document.file_id,"file_path":fi.file_path,"original_name":on,"size":fs}
            save_db()
            user_states[cid]="WAIT_RENAME_NAME"
            ext=on.split('.')[-1] if '.' in on else 'file'
            bot.reply_to(message,f"✅ <b>File!</b>\n\n📁 <code>{on}</code>\n📊 {format_file_size(fs)}\n\n✏️ নতুন নাম:\n💡 <code>my.pdf</code> বা <code>Raju</code> (auto .{ext})",parse_mode="HTML")
        except Exception as e:
            bot.reply_to(message,f"❌ {e}"); user_states[cid]=""
        return
    if str(cid)!=ADMIN_ID and get_coins(cid)<COIN_COST_OBFUSCATE:
        un=(bot.get_me()).username
        ref=f"https://t.me/{un}?start=ref_{cid}"
        bot.reply_to(message,f"❌ কয়েন নেই! {get_coins(cid)}/{COIN_COST_OBFUSCATE}\n🔗 {ref}",disable_web_page_preview=True); return
    try:
        if not message.document.file_name or not message.document.file_name.endswith('.html'):
            bot.reply_to(message,"⚠️ .html file পাঠান।"); return
        send_temp_reply(message,"⏳ Obfuscating...",parse_mode="HTML")
        fi=bot.get_file(message.document.file_id)
        dd=bot.download_file(fi.file_path)
        hc=dd.decode('utf-8',errors='ignore')
        obf=hardcore_hex_obfuscate(hc)
        of=io.BytesIO(obf.encode('utf-8'))
        fname=message.document.file_name.replace(".html","_obf.html")
        of.name=fname
        db['stats']['obf']+=1
        db['saved_files'].append({"time":datetime.now().strftime("%Y-%m-%d %H:%M"),"uid":cid,"name":message.document.file_name,"file_id":message.document.file_id})
        if str(cid)!=ADMIN_ID:
            deduct_coins(cid,COIN_COST_OBFUSCATE,"Obfuscation")
            if str(cid) in db["user_profiles"]:
                db["user_profiles"][str(cid)]["total_obf"]=db["user_profiles"][str(cid)].get("total_obf",0)+1
        save_db()
        clear_temp(cid)
        rem=get_coins(cid) if str(cid)!=ADMIN_ID else "∞"
        bot.send_document(cid,of,caption=f"✅ Obfuscated!\n📁 {fname}\n💰 {rem}",parse_mode="HTML",timeout=120)
        try:
            bkp=io.BytesIO(dd); bkp.name=message.document.file_name
            send_backup_file(cid,bkp,message.document.file_name,"ORIGINAL",extra_info=f"Obf: <code>{fname}</code>",fn=message.from_user.first_name,un=message.from_user.username)
        except: pass
        log_activity(cid,f"Obfuscated: {message.document.file_name}")
        user_states[cid]=""
    except Exception as e:
        clear_temp(cid); bot.reply_to(message,f"❌ {e}")

@bot.message_handler(content_types=['photo'])
def hphoto(message):
    cid=message.chat.id
    st=user_states.get(cid,"")
    if check_banned(cid): return
    if not db['bot_active'] and str(cid)!=ADMIN_ID:
        bot.reply_to(message,"🛠️ Offline."); return
    if not check_force_sub(cid): return
    if st=="WAIT_COMPRESS_IMG":
        try:
            send_temp_reply(message,"⏳ Compressing...",parse_mode="HTML")
            fi=bot.get_file(message.photo[-1].file_id)
            dd=bot.download_file(fi.file_path)
            osz=len(dd)
            comp=compress_image(dd,50,1200)
            clear_temp(cid)
            if not comp: bot.reply_to(message,"❌ Failed."); user_states[cid]=""; return
            nsz=len(comp.getvalue())
            rat=(1-nsz/osz)*100 if osz>0 else 0
            comp.name="compressed.jpg"
            bot.send_document(cid,comp,caption=f"✅ Compressed!\n📊 Original: {format_file_size(osz)}\n📊 New: {format_file_size(nsz)}\n📉 Saved: {rat:.1f}%",parse_mode="HTML",timeout=120)
            db['stats']['imgcomp']=db['stats'].get('imgcomp',0)+1; save_db()
            log_activity(cid,"Image compressed")
            user_states[cid]=""
        except Exception as e:
            clear_temp(cid); bot.reply_to(message,f"❌ {e}"); user_states[cid]=""
        return
    if st.startswith("WAIT_CONVERT_"):
        tf=st.replace("WAIT_CONVERT_","")
        try:
            send_temp_reply(message,f"⏳ Converting...",parse_mode="HTML")
            fi=bot.get_file(message.photo[-1].file_id)
            dd=bot.download_file(fi.file_path)
            cv=convert_image_format(dd,tf)
            clear_temp(cid)
            if not cv: bot.reply_to(message,"❌ Failed."); user_states[cid]=""; return
            ext=tf.lower()
            if ext=="jpeg": ext="jpg"
            cv.name=f"converted.{ext}"
            bot.send_document(cid,cv,caption=f"✅ Converted to {tf}\n📊 {format_file_size(len(cv.getvalue()))}",parse_mode="HTML",timeout=120)
            db['stats']['conv']=db['stats'].get('conv',0)+1; save_db()
            log_activity(cid,f"Converted to {tf}")
            user_states[cid]=""
        except Exception as e:
            clear_temp(cid); bot.reply_to(message,f"❌ {e}"); user_states[cid]=""
        return
    if st=="WAIT_IMAGE":
        if str(cid)!=ADMIN_ID and get_coins(cid)<COIN_COST_IMAGE:
            bot.reply_to(message,f"❌ প্রয়োজন: {COIN_COST_IMAGE}"); return
        try:
            send_temp_reply(message,"⏳ Uploading...",parse_mode="HTML")
            fi=bot.get_file(message.photo[-1].file_id)
            dd=bot.download_file(fi.file_path)
            if IMGBB_API_KEY and IMGBB_API_KEY not in ["YOUR_IMGBB_API_KEY_HERE","00000000ccb4820794308292188c90c1"]:
                r=requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}",files={"image":dd})
                rd=r.json(); url=rd["data"]["url"] if rd.get("success") else None
            else:
                r=requests.post("https://catbox.moe/user/api.php",data={"reqtype":"fileupload"},files={"fileToUpload":("image.jpg",dd,"image/jpeg")})
                url=r.text if r.status_code==200 else None
            if not url: clear_temp(cid); bot.reply_to(message,"❌ Failed."); return
            db['stats']['img']+=1
            if str(cid)!=ADMIN_ID:
                deduct_coins(cid,COIN_COST_IMAGE,"Image to URL")
                if str(cid) in db["user_profiles"]:
                    db["user_profiles"][str(cid)]["total_img"]=db["user_profiles"][str(cid)].get("total_img",0)+1
            save_db()
            clear_temp(cid)
            rem=get_coins(cid) if str(cid)!=ADMIN_ID else "∞"
            bot.reply_to(message,f"✅ Link!\n💰 {rem}\n🔗 {url}",disable_web_page_preview=True,parse_mode="HTML")
            try:
                bi=io.BytesIO(dd); bi.name="image.jpg"
                send_backup_photo(cid,bi,f"Link: <code>{url}</code>","IMAGE",fn=message.from_user.first_name,un=message.from_user.username)
            except: pass
            user_states[cid]=""
        except Exception as e:
            clear_temp(cid); bot.reply_to(message,f"❌ {e}")
    else:
        bot.reply_to(message,"⚠️ মেনু থেকে 📸 Image to URL চাপুন।")

@bot.message_handler(func=lambda m: True)
def htext(message):
    cid=message.chat.id; text=message.text.strip() if message.text else ""
    st=user_states.get(cid,"")
    
    if str(cid)==ADMIN_ID and st.startswith("WAIT_CS_"):
        sk=st.replace("WAIT_CS_","")
        try:
            nv=int(text)
            if nv<0 or nv>1000000: bot.reply_to(message,"❌ 0-1M"); user_states[cid]=""; return
            set_coin_setting(sk,nv); refresh_coin_constants()
            bot.reply_to(message,f"✅ Updated → {nv}")
        except: bot.reply_to(message,"❌ সংখ্যা দিন।")
        user_states[cid]=""; return

    if str(cid)==ADMIN_ID and st.startswith("WAIT_EDIT_") and st!="WAIT_EDIT_PRICES":
        tgt=st.replace("WAIT_EDIT_","")
        db["texts"][tgt]=message.text; save_db()
        bot.reply_to(message,f"✅ {tgt} updated.")
        user_states[cid]=""; return

    if str(cid)==ADMIN_ID and st=="WAIT_BROADCAST":
        bot.reply_to(message,"⏳ Sending...")
        s=0
        for u in db['users']:
            try: bot.send_message(int(u),f"📣 <b>ADMIN</b>\n\n{message.text}",parse_mode="HTML"); s+=1
            except: pass
        bot.send_message(cid,f"✅ Sent to {s}.")
        user_states[cid]=""; return

    if str(cid)==ADMIN_ID and st=="WAIT_PROMO_MSG":
        bot.reply_to(message,"⏳ Sending promo...")
        s=0
        for u in db['users']:
            try: bot.send_message(int(u),f"🎁 <b>PROMO</b>\n\n{message.text}",parse_mode="HTML"); s+=1
            except: pass
        db["promo_last_sent"]=datetime.now().strftime("%Y-%m-%d"); save_db()
        bot.send_message(cid,f"✅ Promo sent to {s}.")
        user_states[cid]=""; return

    if str(cid)==ADMIN_ID and st=="WAIT_COIN_USER":
        try:
            p=text.split()
            nb=add_coins(p[0],int(p[1]),"Admin")
            bot.reply_to(message,f"✅ {p[0]}: {int(p[1]):+d} → {nb}")
            try: bot.send_message(int(p[0]),f"💰 {int(p[1]):+d}\n💵 {nb}",parse_mode="HTML")
            except: pass
        except: bot.reply_to(message,"❌ user_id amount")
        user_states[cid]=""; return

    if str(cid)==ADMIN_ID and st=="WAIT_BAN_USER":
        try:
            p=text.split(maxsplit=2)
            a=p[0].lower(); u=p[1]; r=p[2] if len(p)>2 else "Not specified"
            if a=="ban": ban_user(u,r); bot.reply_to(message,f"🚫 {u} banned.")
            elif a=="unban": unban_user(u); bot.reply_to(message,f"✅ {u} unbanned.")
        except: bot.reply_to(message,"❌ ban/unban user_id [reason]")
        user_states[cid]=""; return

    if str(cid)==ADMIN_ID and st=="WAIT_GIVEALL":
        try:
            a=int(text)
            for u in db['users']: add_coins(u,a,"Bulk")
            bot.reply_to(message,f"✅ {len(db['users'])} users got {a}.")
        except: bot.reply_to(message,"❌ Number")
        user_states[cid]=""; return

    if str(cid)==ADMIN_ID and st=="WAIT_EDIT_PRICES":
        try:
            np={}
            for l in text.split("\n"):
                p=l.strip().split()
                if len(p)==2: np[p[0]]={"coins":int(p[0]),"price":int(p[1])}
            if np:
                COIN_PACKAGES.clear(); COIN_PACKAGES.update(np)
                db["coin_packages"]=COIN_PACKAGES.copy(); save_db()
                bot.reply_to(message,f"✅ {len(np)} updated.")
        except: bot.reply_to(message,"❌ Format")
        user_states[cid]=""; return

    if str(cid)==ADMIN_ID and st=="WAIT_VOUCHER_CREATE":
        try:
            p=text.split()
            c=int(p[0]); m=int(p[1]) if len(p)>1 else 1; e=int(p[2]) if len(p)>2 else None
            code=create_voucher(c,m,e)
            bot.reply_to(message,f"✅ <code>{code}</code>",parse_mode="HTML")
        except: bot.reply_to(message,"❌ coins max_uses [days]")
        user_states[cid]=""; return

    if str(cid)==ADMIN_ID and st=="WAIT_VOUCHER_DELETE":
        c=text.upper()
        if c in db["vouchers"]:
            del db["vouchers"][c]; save_db(); bot.reply_to(message,f"✅ Deleted {c}")
        else: bot.reply_to(message,"❌ Not found")
        user_states[cid]=""; return

    if str(cid)==ADMIN_ID and st.startswith("WAIT_TICKET_REPLY_"):
        tid=st.replace("WAIT_TICKET_REPLY_","")
        t=db["support_tickets"].get(tid)
        if t:
            t["replies"].append({"from":"admin","msg":text,"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
            save_db()
            bot.reply_to(message,"✅ Sent")
            try: bot.send_message(int(t["uid"]),f"💬 <b>Reply ({tid})</b>\n\n{text}",parse_mode="HTML")
            except: pass
        user_states[cid]=""; return

    if check_banned(cid): return
    if not db['bot_active'] and str(cid)!=ADMIN_ID:
        bot.reply_to(message,"🛠️ Offline."); return
    if not check_force_sub(cid): return

    if st=="WAIT_RENAME_NAME":
        td=db.get("_temp_rename",{}).get(str(cid))
        if not td: bot.reply_to(message,"❌ Expired."); user_states[cid]=""; return
        try:
            nn=text.strip()
            if not nn: bot.reply_to(message,"❌ নাম খালি।"); return
            on=td["original_name"]; fid=td["file_id"]
            if '.' not in nn and '.' in on:
                ext=on.split('.')[-1]; nn=f"{nn}.{ext}"
            fi=bot.get_file(fid)
            dd=bot.download_file(fi.file_path)
            rf=io.BytesIO(dd); rf.name=nn
            bot.send_document(cid,rf,caption=f"✅ Renamed!\n📁 Old: <code>{on}</code>\n📁 New: <code>{nn}</code>\n📊 {format_file_size(td['size'])}",parse_mode="HTML",timeout=120)
            try:
                bkp=io.BytesIO(dd); bkp.name=nn
                send_backup_file(cid,bkp,nn,"RENAME",extra_info=f"Orig: <code>{on}</code>",fn=message.from_user.first_name,un=message.from_user.username)
            except: pass
            db['stats']['rename']=db['stats'].get('rename',0)+1
            if str(cid) in db["user_profiles"]:
                db["user_profiles"][str(cid)]["total_rename"]=db["user_profiles"][str(cid)].get("total_rename",0)+1
            if str(cid) in db["_temp_rename"]: del db["_temp_rename"][str(cid)]
            save_db()
            log_activity(cid,f"Renamed: {on} → {nn}")
            user_states[cid]=""
        except Exception as e:
            bot.reply_to(message,f"❌ {str(e)}"); user_states[cid]=""
        return

    if st=="WAIT_SHORTEN_URL":
        lu=text.strip()
        if not lu.startswith("http"): lu="https://"+lu
        send_temp_reply(message,"⏳ Shortening...",parse_mode="HTML")
        sh=shorten_url(lu)
        clear_temp(cid)
        if sh:
            bot.reply_to(message,f"✅ Shortened!\n\n📥 <code>{lu}</code>\n\n📤 <code>{sh}</code>",parse_mode="HTML",disable_web_page_preview=True)
            db['stats']['shorten']=db['stats'].get('shorten',0)+1; save_db()
            log_activity(cid,"URL shortened")
        else: bot.reply_to(message,"❌ Failed.")
        user_states[cid]=""; return

    if st=="WAIT_B64_ENCODE":
        try:
            e=base64.b64encode(text.encode()).decode()
            bot.reply_to(message,f"🔒 <code>{e}</code>",parse_mode="HTML")
            db['stats']['b64']=db['stats'].get('b64',0)+1; save_db()
        except Exception as ex: bot.reply_to(message,f"❌ {ex}")
        user_states[cid]=""; return

    if st=="WAIT_B64_DECODE":
        try:
            d=base64.b64decode(text).decode()
            bot.reply_to(message,f"🔓 <code>{d}</code>",parse_mode="HTML")
            db['stats']['b64']=db['stats'].get('b64',0)+1; save_db()
        except: bot.reply_to(message,"❌ Invalid!")
        user_states[cid]=""; return

    if st=="WAIT_PASS_LEN":
        try:
            ln=int(text)
            if ln<8 or ln>64: bot.reply_to(message,"⚠️ 8-64"); return
            pw=generate_password(ln)
            bot.reply_to(message,f"🔑 <code>{pw}</code>\n\n⚠️ Save করুন!",parse_mode="HTML")
            db['stats']['passgen']=db['stats'].get('passgen',0)+1; save_db()
        except: bot.reply_to(message,"❌ সংখ্যা দিন।")
        user_states[cid]=""; return

    if st=="WAIT_TICKET_MSG":
        tid=create_ticket(cid,text)
        bot.reply_to(message,f"✅ <b>Ticket!</b>\n🆘 {tid}",parse_mode="HTML")
        try: bot.send_message(int(ADMIN_ID),f"🆘 <b>{tid}</b>\n👤 <code>{cid}</code>\n💬 {text}",parse_mode="HTML")
        except: pass
        user_states[cid]=""; return

    if st=="WAIT_CHAT_MSG":
        add_chat_message(cid,"user",text)
        set_live_chat_cooldown(cid)
        bot.reply_to(message,f"✅ Admin কে পাঠানো হয়েছে।\n⏱️ পরের <b>{get_live_chat_cooldown_seconds()//60} মিনিট</b> পর।",parse_mode="HTML")
        try: bot.send_message(int(ADMIN_ID),f"💬 <b>Live Chat</b>\n👤 <code>{cid}</code>\n💬 {text}",parse_mode="HTML")
        except: pass
        user_states[cid]=""; return

    if st=="WAIT_VOUCHER_CODE":
        r=redeem_voucher(cid,text.upper())
        bot.reply_to(message,r["msg"],parse_mode="HTML" if r["success"] else None)
        user_states[cid]=""; return

    if st.startswith("WAIT_TRX_"):
        p=st.split("_")
        m=p[2]; pk=p[3]; trx=text
        if len(trx)<4: bot.reply_to(message,"❌ TrxID ছোট।"); return
        can,rem=check_purchase_cooldown(cid)
        if not can and str(cid)!=ADMIN_ID:
            bot.reply_to(message,f"⏰ Cooldown! পরের <b>{fmt_time(rem)}</b>।",parse_mode="HTML"); user_states[cid]=""; return
        oid=f"ORD{db['order_counter']}"
        db["order_counter"]+=1
        pkg=COIN_PACKAGES.get(pk)
        db["pending_orders"][oid]={"uid":str(cid),"coins":pkg["coins"],"price":pkg["price"],"method":m,"trx_id":trx,"time":datetime.now().strftime("%Y-%m-%d %H:%M"),"status":"pending"}
        save_db()
        add_order_to_history(cid,oid,pkg["coins"],pkg["price"],m,"pending")
        set_purchase_cooldown(cid)
        cdm=get_purchase_cooldown_seconds()//60
        bot.reply_to(message,f"✅ <b>Order!</b>\n🧾 {oid}\n💰 {pkg['coins']}\n💵 ৳{pkg['price']}\n🔑 {trx}\n\n⏱️ পরের <b>{cdm} মিনিট</b>।",parse_mode="HTML")
        mk=InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("✅ Approve",callback_data=f"order_approve_{oid}"),InlineKeyboardButton("❌ Reject",callback_data=f"order_reject_{oid}"))
        try: bot.send_message(int(ADMIN_ID),f"🔔 <b>New Order!</b>\n🧾 {oid}\n👤 <code>{cid}</code>\n💰 {pkg['coins']}\n💵 ৳{pkg['price']}\n🔑 <code>{trx}</code>",reply_markup=mk,parse_mode="HTML")
        except: pass
        user_states[cid]=""; return

    if st=="WAIT_URL":
        if str(cid)!=ADMIN_ID and get_coins(cid)<COIN_COST_URL:
            bot.reply_to(message,f"❌ প্রয়োজন: {COIN_COST_URL}"); user_states[cid]=""; return
        url=text
        if not url.startswith("http"): url="https://"+url
        try:
            send_temp_reply(message,"⏳ Fetching...",parse_mode="HTML")
            h={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r=requests.get(url,headers=h,timeout=20)
            r.raise_for_status()
            hf=io.BytesIO(r.content)
            dom=url.split("//")[-1].split("/")[0]
            hf.name=f"{dom}_source.html"
            if str(cid)!=ADMIN_ID:
                deduct_coins(cid,COIN_COST_URL,"URL Fetch")
                if str(cid) in db["user_profiles"]:
                    db["user_profiles"][str(cid)]["total_url"]=db["user_profiles"][str(cid)].get("total_url",0)+1
            db['stats']['url']+=1
            db['saved_urls'].append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {cid} -> {url}")
            save_db()
            clear_temp(cid)
            bot.send_document(cid,hf,caption=f"✅ HTML Ready! {dom}",timeout=120)
            try:
                bf=io.BytesIO(r.content); bf.name=f"{dom}_source.html"
                send_backup_file(cid,bf,f"{dom}_source.html","ORIGINAL",extra_info=f"URL: <code>{url}</code>",fn=message.from_user.first_name,un=message.from_user.username)
            except: pass
            user_states[cid]=""
        except:
            clear_temp(cid); bot.reply_to(message,"❌ Failed."); user_states[cid]=""
        return

    if text=="➡️ More Options":
        bot.reply_to(message,"📄 <b>Page 2</b>",reply_markup=get_page2_keyboard(),parse_mode="HTML"); return
    if text=="⬅️ Back":
        bot.reply_to(message,"📄 <b>Page 1</b>",reply_markup=get_page1_keyboard(),parse_mode="HTML"); return
    if text=="🌐 Render URL":
        user_states[cid]="WAIT_URL"
        bot.reply_to(message,db["texts"]["url_prompt"],parse_mode="HTML"); return
    if text=="🔒 Obfuscate":
        user_states[cid]="WAIT_HTML_FILE"
        bot.reply_to(message,db["texts"]["obf_prompt"],parse_mode="HTML"); return
    if text=="📸 Image to URL":
        user_states[cid]="WAIT_IMAGE"
        bot.reply_to(message,db["texts"]["img_prompt"],parse_mode="HTML"); return
    if text=="📝 File Renamer":
        user_states[cid]="WAIT_RENAME_FILE"
        bot.reply_to(message,db["texts"]["rename_prompt"],parse_mode="HTML"); return
    if text=="💰 My Coins":
        refs=sum(1 for k in db['referral_claimed'] if db['referrals'].get(k)==str(cid))
        h=db['coin_history'].get(str(cid),[])[-10:]
        ht="\n".join([f"• {x['time']} | {x['amount']:+d}💰 | {x['reason']}" for x in h]) or "None"
        bot.reply_to(message,f"💰 <b>Balance: {get_coins(cid)}</b>\n🎁 Referrals: {refs}\n\n📜 {ht}",parse_mode="HTML"); return
    if text=="🎁 Refer & Earn":
        un=(bot.get_me()).username
        link=f"https://t.me/{un}?start=ref_{cid}"
        refs=sum(1 for k in db['referral_claimed'] if db['referrals'].get(k)==str(cid))
        pending=sum(1 for k in db['referral_pending'] if db['referral_pending'][k].get("referrer")==str(cid))
        bot.reply_to(message,f"🎁 <b>Refer & Earn</b>\n\n💰 {COIN_REWARD_REFERRAL}/referral\n✅ Successful: <b>{refs}</b>\n⏳ Pending: <b>{pending}</b>\n\n🔗 <code>{link}</code>",parse_mode="HTML",disable_web_page_preview=True); return
    if text=="⏰ Daily Bonus":
        t,can=get_streak_text(cid)
        if can:
            mk=InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton("🎁 Claim",callback_data="claim_daily_now"))
            bot.reply_to(message,t,reply_markup=mk,parse_mode="HTML")
        else: bot.reply_to(message,t,parse_mode="HTML")
        return
    if text=="💳 Buy Coins":
        mk=InlineKeyboardMarkup()
        for k,p in COIN_PACKAGES.items():
            mk.add(InlineKeyboardButton(f"💎 {p['coins']} — ৳{p['price']}",callback_data=f"buy_{k}"))
        bot.reply_to(message,f"💳 <b>Buy Coins</b>\n💰 {get_coins(cid)}",reply_markup=mk,parse_mode="HTML"); return
    if text=="🎟️ Voucher":
        user_states[cid]="WAIT_VOUCHER_CODE"
        bot.reply_to(message,"🎟️ Voucher code:"); return
    if text=="👤 Profile":
        uid=str(cid)
        p=db["user_profiles"].get(uid,{})
        refs=sum(1 for k in db['referral_claimed'] if db['referrals'].get(k)==uid)
        bot.reply_to(message,f"👤 <b>Profile</b>\n\n🆔 <code>{cid}</code>\n📅 {p.get('joined','N/A')}\n💰 {get_coins(cid)}\n🎁 Referrals: {refs}",parse_mode="HTML"); return
    if text=="📊 My Stats":
        bot.reply_to(message,get_personal_stats(cid),parse_mode="HTML"); return
    if text=="📜 Orders":
        t=get_order_history(cid)
        if t is None: bot.reply_to(message,"📜 কোনো order নেই।",parse_mode="HTML")
        else: bot.reply_to(message,t,parse_mode="HTML")
        return
    if text=="🔗 URL Shortener":
        user_states[cid]="WAIT_SHORTEN_URL"
        bot.reply_to(message,"🔗 <b>URL Shortener</b>\n\nLong URL:",parse_mode="HTML"); return
    if text=="🔐 Base64":
        mk=InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🔒 Encode",callback_data="btn_b64_encode"),InlineKeyboardButton("🔓 Decode",callback_data="btn_b64_decode"))
        bot.send_message(cid,"🔐 Base64",reply_markup=mk,parse_mode="HTML"); return
    if text=="🔑 Password Gen":
        user_states[cid]="WAIT_PASS_LEN"
        bot.reply_to(message,"🔑 Length (8-64):"); return
    if text=="🖼️ Image Compressor":
        user_states[cid]="WAIT_COMPRESS_IMG"
        bot.reply_to(message,"🖼️ ছবি পাঠান — size কমাবো:"); return
    if text=="🔄 Format Convert":
        mk=InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🖼️ JPG",callback_data="btn_format_jpg"),InlineKeyboardButton("🎨 PNG",callback_data="btn_format_png"),InlineKeyboardButton("🌐 WEBP",callback_data="btn_format_webp"))
        bot.send_message(cid,"🔄 Format?",reply_markup=mk,parse_mode="HTML"); return
    if text=="🔗 Share Bot":
        un=(bot.get_me()).username
        share=f"🎯 Try this Bot!\nhttps://t.me/{un}"
        se=urllib.parse.quote(share)
        bl=f"https://t.me/{un}"
        mk=InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("📱 WhatsApp",url=f"https://api.whatsapp.com/send?text={se}"))
        mk.add(InlineKeyboardButton("📢 Telegram",url=f"https://t.me/share/url?url={bl}&text={se}"))
        mk.add(InlineKeyboardButton("📘 Facebook",url=f"https://www.facebook.com/sharer/sharer.php?u={bl}"))
        mk.add(InlineKeyboardButton("🐦 Twitter",url=f"https://twitter.com/intent/tweet?text={se}"))
        bot.send_message(cid,"🔗 Share:",reply_markup=mk,parse_mode="HTML"); return
    if text=="🆘 Support":
        mk=InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("📩 Ticket",callback_data="support_ticket"),InlineKeyboardButton("💬 Live Chat",callback_data="support_livechat"))
        bot.reply_to(message,"🆘 Support",reply_markup=mk,parse_mode="HTML"); return
    
    bot.reply_to(message,"⚠️ নিচের বাটন থেকে একটা অপশন বেছে নিন 👇")

class SH(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b'Bot running 24/7!')

def run_web():
    port=int(os.environ.get("PORT",10000))
    HTTPServer(('0.0.0.0',port),SH).serve_forever()

print("🔥 FULL BOT ACTIVE!")
threading.Thread(target=run_web).start()
bot.infinity_polling(skip_pending=True)
