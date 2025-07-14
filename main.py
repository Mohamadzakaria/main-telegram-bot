import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ChatMemberStatus
import os
import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN", "7844820429:AAFu63mk6zkI6F0d7RneAYOeNXhJ1Yxwwy0")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002546660006"))
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/PlateNumberLB")
CONTACT_BOT_LINK = os.environ.get("CONTACT_BOT_LINK", "https://t.me/splatenumberlb_bot")

DB_PATH = 'new_main_bot_data.db'
MAX_FREE_ATTEMPTS = 1

def setup_user_attempts_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_attempts (
            user_id INTEGER PRIMARY KEY,
            attempts_left INTEGER DEFAULT 3,
            last_reset TEXT,
            is_premium INTEGER DEFAULT 0,
            premium_until TEXT,
            subscription_type TEXT DEFAULT NULL
        )
    ''')
    conn.commit()
    conn.close()

async def is_subscribed(user_id: int, context: CallbackContext) -> bool:
    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return chat_member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR
        ]
    except:
        return False

def get_user_record(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT attempts_left, last_reset, is_premium, premium_until, subscription_type 
            FROM user_attempts WHERE user_id = ?
        """, (user_id,))
        return cursor.fetchone()

def create_user_record(user_id: int):
    now = datetime.datetime.now().date().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO user_attempts (user_id, attempts_left, last_reset, is_premium, premium_until, subscription_type) "
            "VALUES (?, ?, ?, 0, NULL, NULL)",
            (user_id, MAX_FREE_ATTEMPTS, now)
        )

def update_user_record(user_id: int, attempts_left=None, last_reset=None, is_premium=None, premium_until=None, subscription_type=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        fields = []
        params = []

        if attempts_left is not None:
            fields.append("attempts_left = ?")
            params.append(attempts_left)
        if last_reset is not None:
            fields.append("last_reset = ?")
            params.append(last_reset)
        if is_premium is not None:
            fields.append("is_premium = ?")
            params.append(is_premium)
        if premium_until is not None:
            fields.append("premium_until = ?")
            params.append(premium_until)
        if subscription_type is not None:
            fields.append("subscription_type = ?")
            params.append(subscription_type)

        params.append(user_id)
        sql = f"UPDATE user_attempts SET {', '.join(fields)} WHERE user_id = ?"
        cursor.execute(sql, params)

def reset_attempts_if_needed(user_id: int):
    record = get_user_record(user_id)
    today = datetime.datetime.now().date()
    if not record:
        create_user_record(user_id)
        return MAX_FREE_ATTEMPTS, False

    attempts_left, last_reset_str, is_premium, premium_until_str, _ = record
    is_premium = bool(is_premium)

    if is_premium and premium_until_str:
        try:
            premium_until = datetime.datetime.fromisoformat(premium_until_str).date()
            if premium_until < today:
                is_premium = False
                update_user_record(user_id, is_premium=0, premium_until=None, subscription_type=None)
        except ValueError:
            pass

    if not is_premium:
        if not last_reset_str or datetime.datetime.fromisoformat(last_reset_str).date() < today:
            attempts_left = MAX_FREE_ATTEMPTS
            update_user_record(user_id, attempts_left=attempts_left, last_reset=today.isoformat())

    return attempts_left, is_premium

def decrement_attempt(user_id: int):
    record = get_user_record(user_id)
    if record:
        attempts_left = record[0]
        if attempts_left > 0:
            update_user_record(user_id, attempts_left=attempts_left - 1)

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(
            f"📢 يرجى الاشتراك أولاً في القناة:\n👉 <a href=\"{CHANNEL_LINK}\">{CHANNEL_LINK}</a>\n\nثم أرسل /start مجددًا.",
            parse_mode="HTML"
        )
        return
    await update.message.reply_text(
        "👋 <b>مرحباً بك!</b>\n\n"
        "أرسل رقم لوحة السيارة بالتنسيق التالي:\n"
        "🔹 <code>حرف + أرقام</code> (مثال: <b>A123456</b>)\n\n"
        "❓ للمزيد من المساعدة أرسل الأمر /help",
        parse_mode="HTML"
    )

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "ℹ️ <b>طريقة الاستخدام:</b>\n\n"
        "✅ أرسل رقم اللوحة بالتنسيق التالي: <b>حرف + أرقام</b>\n"
        "📌 مثال: <code>A123456</code>\n\n"
        "🆓 لديك <b>محاوله مجانية يومياً</b> إذا لم تكن مشتركاً.\n"
        "📉 تُخصم المحاولة فقط إذا تم العثور على بيانات.",
        parse_mode="HTML"
    )

async def subscribe_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "💎 <b>خطط الاشتراك:</b>\n\n"
        "📅 شهري: <b>3$</b>\n"
        "📆 سنوي: <b>20$</b>\n"
        "♾️ دائم: <b>30$</b>\n\n"
        "💠 مميزات الاشتراك:\n"
        "✅ معلومات موسعة\n"
        "🔓 ميزات إضافية للمشتركين\n"
        "🛡️ <b>الدائم</b>: إمكانية حذف بياناتك\n\n"
        "💰 الدفع USDT (TRC20):\n"
        "<code>TKQcYbR5Bzxk7EmQMyNXA8xfSL8N7p5ivQ</code>\n\n"
        f"📩 تواصل للتفعيل: <a href=\"{CONTACT_BOT_LINK}\">اضغط هنا</a>",
        parse_mode="HTML"
    )

async def status_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    record = get_user_record(user_id)

    if not record:
        await update.message.reply_text(
            "👤 أنت مستخدم جديد. لديك محاوله مجانية اليوم.\n📦 نوع الاشتراك: لا يوجد",
            parse_mode="HTML"
        )
        return

    attempts_left, _, is_premium, premium_until, subscription_type = record
    subscription_type = subscription_type or "لا يوجد"

    if is_premium:
        await update.message.reply_text(
            f"✅ <b>أنت مشترك</b> حتى: <b>{premium_until}</b>\n"
            f"📦 <b>نوع الاشتراك:</b> {subscription_type}\n"
            f"🔄 <b>المحاولات:</b> غير محدودة",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            f"🔢 <b>محاولاتك المتبقية:</b> {attempts_left} من {MAX_FREE_ATTEMPTS}\n"
            f"📦 <b>نوع الاشتراك:</b> {subscription_type}",
            parse_mode="HTML"
        )

async def get_car_details(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(f"يجب الاشتراك في القناة أولاً:\n{CHANNEL_LINK}")
        return

    plate = update.message.text.strip().upper()
    if len(plate) < 2 or not plate[0].isalpha() or not plate[1:].isdigit():
        await update.message.reply_text("تنسيق خاطئ! مثال: A123456")
        return

    attempts_left, is_premium = reset_attempts_if_needed(user_id)
    if not is_premium and attempts_left <= 0:
        await update.message.reply_text("❌ انتهت محاولاتك المجانية. للاشتراك: /subscribe")
        return

    code_char = plate[0]
    number_part = plate[1:]
    details = await fetch_car_plate_data(code_char, number_part)

    if details:
        msg = (
            f"🚗 <b>تفاصيل لوحة {plate}:</b>\n\n"
            f"👤 <b>المالك:</b> {details['owner_name']}\n"
            f"📞 <b>الهاتف:</b> {details['owner_tel']}\n"
            f"🚘 <b>النوع:</b> {details['car_type_full']}\n"
            f"🎨 <b>اللون:</b> {details['color']}\n"
            f"🛠️ <b>الاستخدام:</b> {details['usage']}\n"
            f"🆔 <b>الشاسيه:</b> {details['chassis_number']}\n"
            f"🔧 <b>المحرك:</b> {details['engine_details']}\n"
        )

        if is_premium:
            msg += (
                f"📅 <b>موديل السيارة:</b> {details['prod_date']}\n"
                f"📆 <b>تاريخ التسجيل:</b> {details['acquisition_date']}\n"
            )
        else:
            msg += (
                f"🔒 <b>موديل السيارة:</b> للمشتركين فقط\n"
                f"🔒 <b>تاريخ التسجيل:</b> للمشتركين فقط\n"
                f"\n💎 للاشتراك: /subscribe"
            )

        msg += f"\n\n📊 المحاولات المتبقية: {'∞' if is_premium else attempts_left - 1}"

        await update.message.reply_text(msg, parse_mode="HTML")

        if not is_premium:
            decrement_attempt(user_id)
    else:
        await update.message.reply_text("❌ لم يتم العثور على معلومات.\n✅ لم تُخصم محاولة.", parse_mode="HTML")

async def fetch_car_plate_data(code_char, number_part):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Nom, Prenom, TelProp, MarqueDesc, CouleurDesc, UtilisDesc,
                       Chassis, Moteur, TypeDesc, PRODDATE, dateaquisition
                FROM CARMDI WHERE ActualNB = ? AND CodeDesc = ?
            """, (int(number_part), code_char))
            row = cursor.fetchone()
            if row:
                return {
                    "owner_name": f"{row[1] or ''} {row[0] or ''}".strip() or "غير متوفر",
                    "owner_tel": row[2] or "غير متوفر",
                    "car_type_full": f"{row[3] or ''} {row[8] or ''}".strip() or "غير متوفر",
                    "color": row[4] or "غير متوفر",
                    "usage": row[5] or "غير متوفر",
                    "chassis_number": row[6] or "غير متوفر",
                    "engine_details": row[7] or "غير متوفر",
                    "prod_date": row[9] or "غير متوفر",
                    "acquisition_date": row[10] or "غير متوفر"
                }
    except Exception as e:
        print(f"خطأ: {e}")
        return None

async def set_premium(update: Update, context: CallbackContext):
    admin_id = update.effective_user.id
    allowed_admins = [7266015804]  # ← ضع هنا معرفك فقط
    if admin_id not in allowed_admins:
        await update.message.reply_text("❌ ليس لديك صلاحية تنفيذ هذا الأمر.")
        return

    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("❗ الاستخدام:\n/set_premium [USER_ID] [نوع الاشتراك: شهري/سنوي/دائم]")
            return

        target_user_id = int(args[0])
        sub_type = args[1].strip().lower()

        if sub_type not in ["شهري", "سنوي", "دائم"]:
            await update.message.reply_text("❗ النوع يجب أن يكون: شهري، سنوي، أو دائم فقط.")
            return

        today = datetime.datetime.now().date()
        if sub_type == "شهري":
            premium_until = (today + datetime.timedelta(days=30)).isoformat()
        elif sub_type == "سنوي":
            premium_until = (today + datetime.timedelta(days=365)).isoformat()
        else:
            premium_until = "دائم"

        create_user_record(target_user_id)
        update_user_record(
            target_user_id,
            is_premium=1,
            premium_until=premium_until,
            subscription_type=sub_type
        )

        await update.message.reply_text(f"✅ تم تفعيل اشتراك {sub_type} للمستخدم {target_user_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")


def main():
    setup_user_attempts_table()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_car_details))
    app.add_handler(CommandHandler("set_premium", set_premium))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
