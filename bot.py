import base64,telebot,io,random,string,requests,json,os,urllib.parse,re,time,threading
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardMarkup,KeyboardButton
from datetime import datetime,timedelta
from http.server import HTTPServer,BaseHTTPRequestHandler
from pymongo import MongoClient

TOKEN=os.getenv('8485929330:AAG8t3n4yE1OMuhdJsbgFxi5z1WsoNDbuuk')
ADMIN_ID=os.getenv('ADMIN_ID','8691419913')
MONGO_URI=os.getenv('MONGO_URI')
MONGO_DB_NAME=os.getenv('MONGO_DB_NAME','telegram_bot')
IMGBB_API_KEY=os.getenv('IMGBB_API_KEY','')

if not TOKEN:
    print("ERROR: TOKEN not set!")
    exit(1)

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
COIN_COST_OBFUSCATE=0
COIN_COST_URL=5
COIN_COST_IMAGE=10
COIN_DAILY_BONUS=5
STREAK_REWARDS={1:5,2:5,3:5,4:5,5:5,6:5,7:25}

DEFAULT_TEXTS={
    "welcome":"═══════════════════════════\n🎉𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗧𝗢𝗟𝗟 𝗕𝗢𝗧🎉\n═══════════════════════════\n👑𝐀𝐋𝐋 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐓𝐎𝐋𝐋𝐒 𝐅𝐑𝐄𝐄👑\n\n☠️𝐀𝐋𝐋 𝐇𝐀𝐂𝐊'𝐒 𝐓𝐎𝐋𝐋 𝐅𝐑𝐄𝐄☠️\n\n🎁𝗔𝗟𝗟 𝗚𝗜𝗩𝗘𝗔𝗪𝗔𝗬 𝗢𝗡 𝗧𝗛𝗘 𝗕𝗢𝗧🎁\n\n⚠️𝗩𝗘𝗥𝗬 𝗜𝗠𝗣𝗢𝗥𝗧𝗔𝗡𝗧 𝗙𝗢𝗥 '𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘' 𝗩𝗜𝗗𝗘𝗢⚠️\n\n⬇️𝐂𝐋𝐈𝐂𝐊 𝐓𝐇𝐈𝐒 𝐁𝐔𝐓𝐓𝐎𝐍 𝐀𝐍𝐃 𝐖𝐀𝐓𝐂𝐇 𝐓𝐇𝐄 𝐕𝗜𝗗𝗘𝗢⬇️",
    "obf_prompt":"⚠️ <b>HTML Obfuscate</b>\n\n📄 <b>Send your .html file!</b>\n\n🆓 <i>FREE!</i>",
    "url_prompt":"📍 <b>URL to HTML</b>\n\n💰 Cost: 5 coins\n\n🎁 <b>Send a URL!</b>",
    "img_prompt":"📸 <b>Image to URL</b>\n\n💰 Cost: 10 coins\n\n<b>Send Your Image!</b>",
    "rename_prompt":"📝 <b>File Renamer</b>\n\n<b>Step 1:</b> ফাইল পাঠান"
}

def get_default_db():
    return {"_id":"main","users":[],"activities":[],"bot_active":True,"saved_urls":[],"saved_files":[],"texts":DEFAULT_TEXTS,"stats":{"obf":0,"url":0,"img":0,"rename":0},"coins":{},"banned_users":[],"referrals":{},"referral_claimed":[],"referral_pending":{},"coin_history":{},"daily_streak":{},"user_profiles":{},"ban_reasons":{},"how_to_use_link":"https://t.me/+ERxRWjTD_HYyNmVl","recent_activity":{},"sub_admins":[],"coin_settings":{"welcome_bonus":5,"referral_reward":10,"daily_bonus":5,"daily_milestone_7":25,"cost_obfuscate":0,"cost_url":5,"cost_image":10},"settings_updated":""}

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
user_states={}

def get_page1_keyboard():
    kb=ReplyKeyboardMarkup(resize_keyboard=True,is_persistent=False,input_field_placeholder="একটা অপশন বেছে নিন...")
    kb.row(KeyboardButton("🌐 Render URL (5💰)"),KeyboardButton("🔒 Obfuscate 🆓"))
    kb.row(KeyboardButton("📸 Image to URL (10💰)"),KeyboardButton("💰 My Coins"))
    kb.row(KeyboardButton("🎁 Refer & Earn"),KeyboardButton("⏰ Daily Bonus"))
    kb.row(KeyboardButton("➡️ More Options"))
    return kb

def get_page2_keyboard():
    kb=ReplyKeyboardMarkup(resize_keyboard=True,is_persistent=False,input_field_placeholder="একটা অপশন বেছে নিন...")
    kb.row(KeyboardButton("📝 File Renamer"),KeyboardButton("📊 My Stats"))
    kb.row(KeyboardButton("⬅️ Back"))
    return kb

def get_coin_setting(k,d=0): return db.get("coin_settings",{}).get(k,d)

def set_coin_setting(k,v):
    if "coin_settings" not in db: db["coin_settings"]={}
    db["coin_settings"][k]=v
    db["settings_updated"]=datetime.now().strftime("%Y-%m-%d %H:%M")
    save_db()

def refresh_coin_constants():
    global COIN_REWARD_REFERRAL,COIN_REWARD_NEW_USER,COIN_COST_OBFUSCATE,COIN_COST_URL,COIN_COST_IMAGE,COIN_DAILY_BONUS,STREAK_REWARDS
    COIN_REWARD_NEW_USER=get_coin_setting("welcome_bonus",5)
    COIN_REWARD_REFERRAL=get_coin_setting("referral_reward",10)
    COIN_DAILY_BONUS=get_coin_setting("daily_bonus",5)
    COIN_COST_OBFUSCATE=get_coin_setting("cost_obfuscate",0)
    COIN_COST_URL=get_coin_setting("cost_url",5)
    COIN_COST_IMAGE=get_coin_setting("cost_image",10)
    dbn=get_coin_setting("daily_bonus",5)
    ms=get_coin_setting("daily_milestone_7",25)
    STREAK_REWARDS={1:dbn,2:dbn,3:dbn,4:dbn,5:dbn,6:dbn,7:ms}

refresh_coin_constants()

def add_user(uid):
    if str(uid) not in db['users']:
        db['users'].append(str(uid))
        if str(uid) not in db["user_profiles"]:
            db["user_profiles"][str(uid)]={"joined":datetime.now().strftime("%Y-%m-%d %H:%M"),"total_obf":0,"total_url":0,"total_img":0,"total_rename":0,"total_referrals":0}
        save_db()

def log_activity(uid,act):
    tn=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db['activities'].append(f"[{tn}] UID: {uid} -> {act}")
    if len(db['activities'])>50: db['activities']=db['activities'][-50:]
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

def format_file_size(b):
    if b<1024: return f"{b} B"
    if b<1024*1024: return f"{b/1024:.2f} KB"
    if b<1024*1024*1024: return f"{b/(1024*1024):.2f} MB"
    return f"{b/(1024*1024*1024):.2f} GB"

def upload_image_multiple(image_bytes,filename="image.jpg"):
    """ImgBB + Catbox Only"""
    # Try 1: ImgBB
    try:
        if IMGBB_API_KEY and IMGBB_API_KEY not in ["YOUR_IMGBB_API_KEY_HERE",""]:
            image_bytes.seek(0)
            r=requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}",files={"image":image_bytes},timeout=30)
            if r.status_code==200:
                rd=r.json()
                if rd.get("success"):
                    print("[ImgBB] Success")
                    return rd["data"]["url"]
    except Exception as e:
        print(f"[ImgBB Failed] {e}")
    
    # Try 2: Catbox
    try:
        image_bytes.seek(0)
        r=requests.post("https://catbox.moe/user/api.php",data={"reqtype":"fileupload"},files={"fileToUpload":(filename,image_bytes,"image/jpeg")},timeout=60)
        if r.status_code==200 and r.text.strip().startswith("http"):
            print("[Catbox] Success")
            return r.text.strip()
    except Exception as e:
        print(f"[Catbox Failed] {e}")
    
    print("[All Failed]")
    return None

def get_personal_stats(uid):
    u=str(uid)
    p=db["user_profiles"].get(u,{})
    tr=sum(1 for k in db['referral_claimed'] if db['referrals'].get(k)==u)
    pr=sum(1 for k in db['referral_pending'] if db['referral_pending'][k].get("referrer")==u)
    return (f"📊 <b>Your Statistics</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>ID:</b> <code>{uid}</code>\n"
            f"📅 <b>Joined:</b> {p.get('joined','N/A')}\n\n"
            f"💰 <b>Balance:</b> {get_coins(uid)} coins\n\n"
            f"🎁 <b>Referrals:</b>\n   ✅ Successful: <b>{tr}</b>\n   ⏳ Pending: <b>{pr}</b>\n\n"
            f"🔄 <b>Operations:</b>\n"
            f"   Obfuscate: <b>{p.get('total_obf',0)}</b>\n"
            f"   URL Fetch: <b>{p.get('total_url',0)}</b>\n"
            f"   Image to URL: <b>{p.get('total_img',0)}</b>\n"
            f"   File Renamed: <b>{p.get('total_rename',0)}</b>")

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

@bot.message_handler(commands=['sethowtouse'])
def set_how_cmd(message):
    if str(message.chat.id)!=ADMIN_ID: return
    try:
        parts=message.text.split(maxsplit=1)
        if len(parts)<2:
            bot.reply_to(message,"❌ /sethowtouse [link]"); return
        nl=parts[1].strip()
        if not nl.startswith("http"): nl="https://"+nl
        old=db.get("how_to_use_link","")
        db["how_to_use_link"]=nl; save_db()
        bot.reply_to(message,f"✅ Updated!\n❌ Old: <code>{old}</code>\n✅ New: <code>{nl}</code>",parse_mode="HTML")
    except: bot.reply_to(message,"❌ Error")

@bot.message_handler(commands=['addsub'])
def add_sub(message):
    if str(message.chat.id)!=ADMIN_ID: return
    try:
        uid=message.text.split()[1]
        if uid not in db.get("sub_admins",[]):
            db.setdefault("sub_admins",[]).append(uid); save_db()
            bot.reply_to(message,f"✅ {uid} added.")
        else: bot.reply_to(message,"⚠️ Already added.")
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
    m.add(InlineKeyboardButton("📖 How To Use",callback_data="admin_how_to_use_settings"))
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
        mk=InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🔙 Back",callback_data="admin_back_to_panel"))
        bot.send_message(cid,"📖 <b>ADMIN HELP</b>\n\nসব বাটন Admin Panel এ আছে।",reply_markup=mk,parse_mode="HTML")
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
        m.add(InlineKeyboardButton("📖 How To Use",callback_data="admin_how_to_use_settings"))
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
        elif call.data=="admin_how_to_use_settings":
            cl=db.get("how_to_use_link","Not set")
            bot.send_message(cid,f"📖 <b>How To Use</b>\n\n<code>{cl}</code>\n\n<code>/sethowtouse [link]</code>",parse_mode="HTML",disable_web_page_preview=True)
        elif call.data=="admin_coin_settings":
            cs=db.get("coin_settings",{})
            t=(f"💰 <b>Coin Settings</b>\n\n🎁 Welcome: <b>{cs.get('welcome_bonus',5)}</b>\n🎁 Referral: <b>{cs.get('referral_reward',10)}</b>\n⏰ Daily: <b>{cs.get('daily_bonus',5)}</b>\n🎊 Day 7: <b>{cs.get('daily_milestone_7',25)}</b>\n\n💸 Obfuscate: <b>{cs.get('cost_obfuscate',0)}</b> 🆓\n💸 URL: <b>{cs.get('cost_url',5)}</b>\n💸 Image: <b>{cs.get('cost_image',10)}</b>")
            mk=InlineKeyboardMarkup(row_width=2)
            mk.add(InlineKeyboardButton("🎁 Welcome",callback_data="cs_edit_welcome_bonus"),InlineKeyboardButton("🎁 Referral",callback_data="cs_edit_referral_reward"))
            mk.add(InlineKeyboardButton("⏰ Daily",callback_data="cs_edit_daily_bonus"),InlineKeyboardButton("🎊 Day 7",callback_data="cs_edit_daily_milestone_7"))
            mk.add(InlineKeyboardButton("🔒 Obfuscate",callback_data="cs_edit_cost_obfuscate"),InlineKeyboardButton("🌐 URL",callback_data="cs_edit_cost_url"))
            mk.add(InlineKeyboardButton("📸 Image",callback_data="cs_edit_cost_image"))
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
            db["coin_settings"]={"welcome_bonus":5,"referral_reward":10,"daily_bonus":5,"daily_milestone_7":25,"cost_obfuscate":0,"cost_url":5,"cost_image":10}
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
        return

    if call.data.startswith("edit_txt_"):
        if str(cid)!=ADMIN_ID: return
        target=call.data.replace("edit_txt_","")
        user_states[cid]=f"WAIT_EDIT_{target}"
        bot.send_message(cid,f"New text for {target}:")
        return

    if check_banned(cid): return
    if not db['bot_active'] and str(cid)!=ADMIN_ID: return
    if not check_force_sub(cid): return

    if call.data=="claim_daily_now":
        r=claim_daily_bonus_streak(cid)
        if r is None: bot.answer_callback_query(call.id,"আজ নেওয়া!",show_alert=True); return
        msg=f"🎉 <b>Day {r['streak']}!</b>\n💰 +{r['reward']}\n💵 {get_coins(cid)}"
        if r["is_milestone"]: msg=f"🎊 <b>🔥 7 DAY STREAK!</b>\n💰 +{r['reward']}\n💵 {get_coins(cid)}"
        bot.send_message(cid,msg,parse_mode="HTML"); return

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
            bot.reply_to(message,f"✅ <b>File!</b>\n\n📁 <code>{on}</code>\n📊 {format_file_size(fs)}\n\n✏️ নতুন নাম:\n💡 <code>my.pdf</code> বা <code>Raju</code>",parse_mode="HTML")
        except Exception as e:
            bot.reply_to(message,f"❌ {e}"); user_states[cid]=""
        return
    try:
        if not message.document.file_name or not message.document.file_name.endswith('.html'):
            bot.reply_to(message,"⚠️ .html file পাঠান।"); return
        if str(cid)!=ADMIN_ID and get_coins(cid)<COIN_COST_OBFUSCATE:
            un=(bot.get_me()).username
            ref=f"https://t.me/{un}?start=ref_{cid}"
            bot.reply_to(message,f"❌ কয়েন নেই! {get_coins(cid)}/{COIN_COST_OBFUSCATE}\n🔗 {ref}",disable_web_page_preview=True); return
        bot.reply_to(message,"⏳ Obfuscating...",parse_mode="HTML")
        fi=bot.get_file(message.document.file_id)
        dd=bot.download_file(fi.file_path)
        hc=dd.decode('utf-8',errors='ignore')
        obf=hardcore_hex_obfuscate(hc)
        of=io.BytesIO(obf.encode('utf-8'))
        fname=message.document.file_name.replace(".html","_obf.html")
        of.name=fname
        db['stats']['obf']+=1
        db['saved_files'].append({"time":datetime.now().strftime("%Y-%m-%d %H:%M"),"uid":cid,"name":message.document.file_name,"file_id":message.document.file_id})
        if str(cid)!=ADMIN_ID and COIN_COST_OBFUSCATE>0:
            deduct_coins(cid,COIN_COST_OBFUSCATE,"Obfuscation")
        if str(cid) in db["user_profiles"]:
            db["user_profiles"][str(cid)]["total_obf"]=db["user_profiles"][str(cid)].get("total_obf",0)+1
        save_db()
        rem=get_coins(cid) if str(cid)!=ADMIN_ID else "∞"
        bot.send_document(cid,of,caption=f"✅ Obfuscated!\n📁 {fname}\n💰 {rem}",parse_mode="HTML",timeout=120)
        try:
            bkp=io.BytesIO(dd); bkp.name=message.document.file_name
            send_backup_file(cid,bkp,message.document.file_name,"ORIGINAL",extra_info=f"Obf: <code>{fname}</code>",fn=message.from_user.first_name,un=message.from_user.username)
        except: pass
        log_activity(cid,f"Obfuscated: {message.document.file_name}")
        user_states[cid]=""
    except Exception as e:
        bot.reply_to(message,f"❌ {e}")

@bot.message_handler(content_types=['photo'])
def hphoto(message):
    cid=message.chat.id
    st=user_states.get(cid,"")
    if check_banned(cid): return
    if not db['bot_active'] and str(cid)!=ADMIN_ID:
        bot.reply_to(message,"🛠️ Offline."); return
    if not check_force_sub(cid): return
    if st=="WAIT_IMAGE":
        if str(cid)!=ADMIN_ID and get_coins(cid)<COIN_COST_IMAGE:
            bot.reply_to(message,f"❌ প্রয়োজন: {COIN_COST_IMAGE} coins\n💰 আপনার: {get_coins(cid)}"); return
        try:
            bot.reply_to(message,"⏳ Uploading...",parse_mode="HTML")
            fi=bot.get_file(message.photo[-1].file_id)
            dd=bot.download_file(fi.file_path)
            img_buffer = io.BytesIO(dd)
            url = upload_image_multiple(img_buffer, "image.jpg")
            if not url:
                bot.reply_to(message,"❌ Upload failed! আবার চেষ্টা করুন।")
                user_states[cid]=""
                return
            db['stats']['img']+=1
            if str(cid)!=ADMIN_ID:
                deduct_coins(cid,COIN_COST_IMAGE,"Image to URL")
            if str(cid) in db["user_profiles"]:
                db["user_profiles"][str(cid)]["total_img"]=db["user_profiles"][str(cid)].get("total_img",0)+1
            save_db()
            rem=get_coins(cid) if str(cid)!=ADMIN_ID else "∞"
            bot.reply_to(message,f"✅ Link!\n💰 {rem}\n🔗 {url}",disable_web_page_preview=True,parse_mode="HTML")
            try:
                bi=io.BytesIO(dd); bi.name="image.jpg"
                send_backup_photo(cid,bi,f"Link: <code>{url}</code>","IMAGE",fn=message.from_user.first_name,un=message.from_user.username)
            except: pass
            user_states[cid]=""
        except Exception as e:
            bot.reply_to(message,f"❌ {e}")
            user_states[cid]=""
        return
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

    if st=="WAIT_URL":
        if str(cid)!=ADMIN_ID and get_coins(cid)<COIN_COST_URL:
            bot.reply_to(message,f"❌ প্রয়োজন: {COIN_COST_URL} coins\n💰 আপনার: {get_coins(cid)}"); user_states[cid]=""; return
        url=text
        if not url.startswith("http"): url="https://"+url
        try:
            bot.reply_to(message,"⏳ Fetching...",parse_mode="HTML")
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
            bot.send_document(cid,hf,caption=f"✅ HTML Ready! {dom}",timeout=120)
            try:
                bf=io.BytesIO(r.content); bf.name=f"{dom}_source.html"
                send_backup_file(cid,bf,f"{dom}_source.html","ORIGINAL",extra_info=f"URL: <code>{url}</code>",fn=message.from_user.first_name,un=message.from_user.username)
            except: pass
            user_states[cid]=""
        except:
            bot.reply_to(message,"❌ Failed."); user_states[cid]=""
        return

    if text=="➡️ More Options":
        bot.reply_to(message,"📄 <b>Page 2</b>",reply_markup=get_page2_keyboard(),parse_mode="HTML"); return
    if text=="⬅️ Back":
        bot.reply_to(message,"📄 <b>Page 1</b>",reply_markup=get_page1_keyboard(),parse_mode="HTML"); return
    if text=="🌐 Render URL (5💰)":
        user_states[cid]="WAIT_URL"
        bot.reply_to(message,db["texts"]["url_prompt"],parse_mode="HTML"); return
    if text=="🔒 Obfuscate 🆓":
        user_states[cid]="WAIT_HTML_FILE"
        bot.reply_to(message,db["texts"]["obf_prompt"],parse_mode="HTML"); return
    if text=="📸 Image to URL (10💰)":
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
    if text=="📊 My Stats":
        bot.reply_to(message,get_personal_stats(cid),parse_mode="HTML"); return
    
    bot.reply_to(message,"⚠️ নিচের বাটন থেকে একটা অপশন বেছে নিন 👇")

class SH(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b'Bot running 24/7!')

def run_web():
    port=int(os.environ.get("PORT",10000))
    HTTPServer(('0.0.0.0',port),SH).serve_forever()

print("FULL BOT ACTIVE!")
threading.Thread(target=run_web).start()
bot.infinity_polling(skip_pending=True)
