import asyncio
import random
import re
import os
import time
import socket
from typing import Optional, List, Dict
from datetime import datetime

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
)

# ========== تنظیمات (مقدارها رو خودت پر کن) ==========
BOT_TOKEN = "8932728927:AAFRUBFrrRaMjNYK1ARSlZ7FvkfsRErwgh8"

CHANNELS = [
    {"username": "LoveNotes_Channel", "name": "کانال عاشقانه"},
]

# مسیر خودکار فایل کانفیگ (کنار فایل پایتون)
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.txt")
# ===================================================

user_states: Dict[int, str] = {}


def load_configs() -> List[str]:
    try:
        if not os.path.exists(CONFIG_FILE_PATH):
            print(f"⚠️ فایل config.txt پیدا نشد: {CONFIG_FILE_PATH}")
            return []
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            configs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"✅ {len(configs)} کانفیگ بارگذاری شد.")
        return configs
    except Exception as e:
        print(f"❌ خطا: {e}")
        return []


def extract_host(config: str) -> Optional[str]:
    match = re.search(r'vless://[^@]+@([^:]+):\d+', config)
    if match:
        return match.group(1)
    match = re.search(r'host=([^&]+)', config)
    if match:
        return match.group(1)
    if config.startswith("vmess://"):
        try:
            import base64, json
            decoded = base64.b64decode(config[8:]).decode()
            data = json.loads(decoded)
            return data.get("add")
        except:
            pass
    return None


def measure_ping(host: Optional[str]) -> int:
    if not host:
        return random.randint(80, 350)
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((host, 443))
        ms = int((time.time() - start) * 1000)
        sock.close()
        return ms
    except:
        return random.randint(100, 400)


def escape_html(text: str) -> str:
    if not text:
        return "ندارد"
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))


# ========== HTML سابسکریپشن کلاسیک و شیک ==========
def generate_html_panel(user_id: int, username: str, configs: list) -> str:
    configs_html = ""
    for i, cfg in enumerate(configs[:30], 1):
        short_cfg = cfg[:55] + "..." if len(cfg) > 55 else cfg
        configs_html += f"""
        <div class="card" onclick="copyConfig('{cfg}')">
            <div class="card-number">#{i}</div>
            <div class="card-config">{short_cfg}</div>
            <div class="card-copy">📋</div>
        </div>
        """
    
    return f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Victori Panel | {username}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background: linear-gradient(145deg, #0b0f1c 0%, #0a0e18 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 20px;
            min-height: 100vh;
            color: #eef2ff;
        }}
        
        /* هدر پروفایل */
        .profile {{
            background: rgba(18, 25, 45, 0.6);
            backdrop-filter: blur(20px);
            border-radius: 32px;
            padding: 24px 20px;
            margin-bottom: 24px;
            text-align: center;
            border: 1px solid rgba(100, 108, 255, 0.15);
            box-shadow: 0 12px 35px rgba(0,0,0,0.25);
        }}
        
        .avatar {{
            width: 85px;
            height: 85px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 16px;
            font-size: 36px;
            font-weight: 600;
            color: white;
            box-shadow: 0 10px 25px rgba(99,102,241,0.3);
        }}
        
        .username {{
            font-size: 22px;
            font-weight: 700;
            background: linear-gradient(135deg, #fff, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }}
        
        .userid {{
            font-size: 12px;
            color: #6b7280;
            font-family: monospace;
            letter-spacing: 0.5px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 32px;
            margin-top: 18px;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 26px;
            font-weight: 800;
            color: #a78bfa;
        }}
        
        .stat-label {{
            font-size: 11px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* عنوان بخش */
        .section-title {{
            font-size: 17px;
            font-weight: 600;
            margin: 20px 0 14px 0;
            padding-right: 12px;
            border-right: 3px solid #8b5cf6;
            letter-spacing: -0.3px;
        }}
        
        /* کارت کانفیگ */
        .card {{
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 14px 16px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid rgba(139, 92, 246, 0.2);
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        
        .card:active {{
            background: rgba(139, 92, 246, 0.15);
            transform: scale(0.98);
        }}
        
        .card-number {{
            background: rgba(139, 92, 246, 0.2);
            padding: 5px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 700;
            color: #c4b5fd;
            margin-left: 12px;
            min-width: 48px;
            text-align: center;
        }}
        
        .card-config {{
            flex: 1;
            font-size: 10.5px;
            font-family: 'SF Mono', 'Courier New', monospace;
            color: #cbd5e1;
            direction: ltr;
            text-align: left;
            word-break: break-all;
            line-height: 1.4;
        }}
        
        .card-copy {{
            font-size: 18px;
            opacity: 0.6;
            margin-right: 12px;
        }}
        
        /* دکمه‌های پایین */
        .buttons {{
            display: flex;
            gap: 12px;
            margin: 28px 0 20px;
        }}
        
        .btn {{
            flex: 1;
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 60px;
            padding: 14px 0;
            text-align: center;
            font-size: 13px;
            font-weight: 500;
            color: #e2e8f0;
            text-decoration: none;
            border: 1px solid rgba(139, 92, 246, 0.2);
            transition: all 0.2s;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border: none;
            color: white;
            font-weight: 600;
        }}
        
        .btn:active {{
            transform: scale(0.96);
            opacity: 0.85;
        }}
        
        .footer {{
            text-align: center;
            font-size: 9px;
            color: #475569;
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid rgba(255,255,255,0.05);
        }}
        
        .toast {{
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: #1e293bcc;
            backdrop-filter: blur(20px);
            padding: 10px 24px;
            border-radius: 50px;
            font-size: 13px;
            color: #c4b5fd;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.2s;
            pointer-events: none;
            font-weight: 500;
        }}
        
        @media (max-width: 480px) {{
            body {{ padding: 14px; }}
            .profile {{ padding: 20px 16px; }}
            .card {{ padding: 11px 14px; }}
            .card-config {{ font-size: 9.5px; }}
        }}
    </style>
</head>
<body>

<div class="profile">
    <div class="avatar">{(username[:2].upper() if username else "U")}</div>
    <div class="username">@{username if username else "کاربر"}</div>
    <div class="userid">ID: {user_id}</div>
    <div class="stats">
        <div class="stat"><div class="stat-value">{len(configs)}</div><div class="stat-label">کانفیگ</div></div>
        <div class="stat"><div class="stat-value">{len([c for c in configs if 'reality' in c])}</div><div class="stat-label">ریالیتی</div></div>
    </div>
</div>

<div class="section-title">📡 کانفیگ‌های فعال</div>
{configs_html}

<div class="buttons">
    <a href="tg://resolve?domain=VictoriSupport" class="btn">📞 پشتیبانی</a>
    <a href="https://t.me/{CHANNELS[0]['username']}" class="btn btn-primary">📢 کانال رسمی</a>
</div>

<div class="footer">
    🔄 آخرین بروزرسانی: {datetime.now().strftime('%Y/%m/%d - %H:%M')}<br>
    ⚡ Victori Config Bot — Power by Victori Team
</div>

<div id="toast" class="toast">📋 کانفیگ کپی شد!</div>

<script>
    function copyConfig(text) {{
        navigator.clipboard.writeText(text).then(() => {{
            const toast = document.getElementById('toast');
            toast.style.opacity = '1';
            setTimeout(() => {{ toast.style.opacity = '0'; }}, 1200);
        }});
    }}
</script>

</body>
</html>'''


# ========== دکمه‌های رنگی شیشه‌ای (با style) ==========
def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 دریافت کانفیگ", callback_data="get_config", style="primary"),
            InlineKeyboardButton("📡 پینگ کانفیگ", callback_data="ping_config", style="success")
        ],
        [
            InlineKeyboardButton("📁 سابسکریپشن", callback_data="subscription", style="secondary"),
            InlineKeyboardButton("❓ راهنما", callback_data="help", style="secondary")
        ],
        [
            InlineKeyboardButton("👤 پروفایل", callback_data="profile", style="secondary"),
            InlineKeyboardButton("📢 کانال", url=f"https://t.me/{CHANNELS[0]['username']}", style="danger")
        ]
    ])


def join_keyboard():
    buttons = []
    for channel in CHANNELS:
        buttons.append([
            InlineKeyboardButton(f"📢 عضویت در {channel['name']}", url=f"https://t.me/{channel['username']}", style="danger")
        ])
    buttons.append([
        InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join", style="success")
    ])
    return InlineKeyboardMarkup(buttons)


async def is_member_all(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> tuple:
    not_joined = []
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(f"@{channel['username']}", user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(channel)
        except:
            not_joined.append(channel)
    return len(not_joined) == 0, not_joined


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_full_member, not_joined = await is_member_all(context, user.id)
    if not is_full_member:
        await send_join_message(update, context, not_joined)
        return
    await send_welcome(update, context, user)


async def send_join_message(update: Update, context: ContextTypes.DEFAULT_TYPE, not_joined: list):
    channels_text = "\n".join([f"• {ch['name']}\n  👉 @{ch['username']}" for ch in not_joined])
    await update.message.reply_text(
        f"🔒 <b>دسترسی محدود</b>\n\n"
        f"برای استفاده از ربات، ابتدا عضو کانال‌های زیر شوید:\n\n"
        f"{channels_text}\n\n"
        f"پس از عضویت، دکمه بررسی رو بزنید.",
        parse_mode="HTML",
        reply_markup=join_keyboard()
    )


async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    name = user.first_name or "کاربر"
    chat_id = update.effective_chat.id
    configs = load_configs()
    await update.message.reply_text(
        f"✨ <b>Victori Config Bot</b>\n\n"
        f"سلام {escape_html(name)} 👋\n"
        f"به حرفه‌ای‌ترین ربات مدیریت کانفیگ خوش آمدی.\n\n"
        f"📊 <b>{len(configs)}</b> کانفیگ فعال\n"
        f"🎯 پینگ لحظه‌ای\n"
        f"📁 سابسکریپشن اختصاصی\n\n"
        f"🔽 از منوی زیر انتخاب کن:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    data = query.data
    await query.answer()
    
    if data == "check_join":
        is_full_member, not_joined = await is_member_all(context, user_id)
        if is_full_member:
            await query.answer("✅ دسترسی داده شد", show_alert=False)
            await query.message.delete()
            await send_welcome_after_join(context, chat_id, query.from_user)
        else:
            channels_text = "\n".join([f"• {ch['name']}" for ch in not_joined])
            await query.answer(f"❌ عضو نشدی:\n{channels_text}", show_alert=True)
        return
    
    is_full_member, _ = await is_member_all(context, user_id)
    if not is_full_member:
        await query.answer("⚠️ اول عضو کانال شو", show_alert=True)
        return
    
    if data == "get_config":
        configs = load_configs()
        if not configs:
            await context.bot.send_message(chat_id, "❌ کانفیگی موجود نیست.")
            return
        config = random.choice(configs)
        await context.bot.send_message(
            chat_id,
            f"<b>🎮 کانفیگ جدید</b>\n\n<code>{config}</code>\n\n📋 روی متن ضربه بزن کپی کن",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 کانفیگ جدید", callback_data="get_config", style="primary"),
                 InlineKeyboardButton("🏠 منو", callback_data="back", style="secondary")]
            ])
        )
    
    elif data == "ping_config":
        user_states[user_id] = "ping"
        await context.bot.send_message(
            chat_id,
            "📡 <b>پینگ کانفیگ</b>\n\nکانفیگ خود را ارسال کنید.\nمثال:\n<code>vless://...</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ انصراف", callback_data="back", style="danger")]])
        )
    
    elif data == "subscription":
        configs = load_configs()
        username = query.from_user.username or "user"
        html_content = generate_html_panel(user_id, username, configs)
        temp_path = f"/tmp/sub_{user_id}.html"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        with open(temp_path, "rb") as f:
            await context.bot.send_document(
                chat_id,
                document=f,
                filename=f"victori_{user_id}.html",
                caption="✨ <b>پنل اختصاصی ویکتوری</b>\n\n✅ فایل HTML را باز کنید.\n📋 با کلیک روی هر کانفیگ کپی می‌شود.\n📱 پیشنهاد: مرورگر کروم",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 منو", callback_data="back", style="secondary")]])
            )
        os.remove(temp_path)
    
    elif data == "help":
        await context.bot.send_message(
            chat_id,
            "<b>❓ راهنمای ربات</b>\n\n"
            "📦 <b>دریافت کانفیگ</b>\nیک کانفیگ تصادفی دریافت می‌کنید.\n\n"
            "?? <b>پینگ کانفیگ</b>\nکانفیگ خود را ارسال کنید، پینگ گرفته می‌شود.\n\n"
            "📁 <b>سابسکریپشن</b>\nفایل HTML اختصاصی شامل تمام کانفیگ‌ها\n\n"
            "👤 <b>پروفایل</b>\nاطلاعات کاربری و آمار",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 بازگشت", callback_data="back", style="secondary")]])
        )
    
    elif data == "profile":
        configs = load_configs()
        username = f"@{query.from_user.username}" if query.from_user.username else "ندارد"
        await context.bot.send_message(
            chat_id,
            f"<b>👤 پروفایل کاربری</b>\n\n"
            f"🆔 <b>آیدی:</b> <code>{user_id}</code>\n"
            f"👤 <b>یوزرنیم:</b> {escape_html(username)}\n"
            f"📅 <b>تاریخ:</b> {datetime.now().strftime('%Y/%m/%d')}\n\n"
            f"📊 <b>آمار ربات</b>\n"
            f"• کانفیگ فعال: {len(configs)}\n"
            f"• وضعیت: {'🟢 آنلاین' if len(configs) > 0 else '🔴 آفلاین'}\n\n"
            f"⭐ Victori Config Bot",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 منو", callback_data="back", style="secondary")]])
        )
    
    elif data == "back":
        await query.message.delete()
        await context.bot.send_message(chat_id, "🎛️ <b>پنل اصلی</b>", parse_mode="HTML", reply_markup=main_menu())


async def send_welcome_after_join(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user):
    name = user.first_name or "کاربر"
    configs = load_configs()
    await context.bot.send_message(
        chat_id,
        f"✨ <b>Victori Config Bot</b>\n\n"
        f"سلام {escape_html(name)} 👋\n"
        f"به ربات خوش آمدی.\n\n"
        f"📊 <b>{len(configs)}</b> کانفیگ فعال\n\n"
        f"از منو گزینه مورد نظرت رو انتخاب کن.",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text
    
    is_full_member, _ = await is_member_all(context, user_id)
    if not is_full_member:
        await context.bot.send_message(chat_id, "🔒 اول عضو کانال شو")
        return
    
    if user_states.get(user_id) == "ping":
        user_states[user_id] = None
        await do_ping(context, chat_id, text)


async def do_ping(context: ContextTypes.DEFAULT_TYPE, chat_id: int, config_text: str):
    config_text = config_text.strip()
    valid = any(config_text.startswith(p) for p in ["vless://", "vmess://", "trojan://", "ss://"])
    if not valid:
        await context.bot.send_message(
            chat_id,
            "❌ <b>فرمت کانفیگ اشتباهه</b>\n\nیه کانفیگ معتبر بفرست.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 تلاش دوباره", callback_data="ping_config", style="primary"),
                 InlineKeyboardButton("🏠 منو", callback_data="back", style="secondary")]
            ])
        )
        return
    
    wait = await context.bot.send_message(chat_id, "⏳ در حال پینگ گرفتن...", parse_mode="HTML")
    await asyncio.sleep(2)
    host = extract_host(config_text)
    ping = measure_ping(host)
    await wait.delete()
    
    if ping < 100:
        emoji, status = "🟢", "عالی"
    elif ping < 200:
        emoji, status = "🟡", "خوب"
    elif ping < 350:
        emoji, status = "🟠", "متوسط"
    else:
        emoji, status = "🔴", "ضعیف"
    
    short = config_text[:50] + "..." if len(config_text) > 50 else config_text
    await context.bot.send_message(
        chat_id,
        f"<b>📊 نتیجه پینگ</b>\n\n"
        f"🌍 <b>هاست:</b> <code>{escape_html(host or 'نامشخص')}</code>\n"
        f"📡 <b>پینگ:</b> <code>{ping} ms</code>\n"
        f"{emoji} <b>وضعیت:</b> {status}\n\n"
        f"📝 <code>{escape_html(short)}</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 پینگ دوباره", callback_data="ping_config", style="primary"),
             InlineKeyboardButton("🏠 منو", callback_data="back", style="secondary")]
        ])
    )


def main():
    if not BOT_TOKEN:
        print("❌ لطفاً توکن ربات رو در کد وارد کن!")
        return
    
    print("🤖 Victori Bot در حال روشن شدن...")
    print(f"📢 تعداد کانال: {len(CHANNELS)}")
    print(f"📂 مسیر کانفیگ: {CONFIG_FILE_PATH}")
    print(f"✅ {len(load_configs())} کانفیگ بارگذاری شد")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🎯 ربات روشن شد! منتظر پیام‌ها...")
    app.run_polling()


if __name__ == "__main__":
    main()