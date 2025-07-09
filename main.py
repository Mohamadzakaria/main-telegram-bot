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

DB_PATH = 'data.db'
MAX_FREE_ATTEMPTS = 3

# تحديث جدول المحاولات ليشمل الاشتراك
def setup_user_attempts_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_attempts (
            user_id INTEGER PRIMARY KEY,
            attempts_left INTEGER DEFAULT 3,
            last_reset TEXT,
            is_premium INTEGER DEFAULT 0,
            premium_until TEXT
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
    except Exception as e:
        print(f"خطأ في التحقق من الاشتراك: {e}")
        return False

# جلب بيانات المستخدم من قاعدة البيانات
def get_user_record(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT attempts_left, last_reset, is_premium, premium_until FROM user_attempts WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# إنشاء سجل جديد للمستخدم إن لم يكن موجود
def create_user_record(user_id: int):
    now = datetime.datetime.now().date().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO user_attempts (user_id, attempts_left, last_reset, is_premium, premium_until) VALUES (?, ?, ?, 0, NULL)",
                   (user_id, MAX_FREE_ATTEMPTS, now))
    conn.commit()
    conn.close()

# تحديث سجل المستخدم
def update_user_record(user_id: int, attempts_left=None, last_reset=None, is_premium=None, premium_until=None):
    conn = sqlite3.connect(DB_PATH)
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
    params.append(user_id)
    sql = f"UPDATE user_attempts SET {', '.join(fields)} WHERE user_id = ?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()

# إدارة المحاولات
def reset_attempts_if_needed(user_id: int):
    record = get_user_record(user_id)
    today = datetime.datetime.now().date()
    if not record:
        create_user_record(user_id)
        return MAX_FREE_ATTEMPTS, False

    attempts_left, last_reset_str, is_premium, premium_until_str = record
    is_premium = bool(is_premium)

    # تحقق انتهاء الاشتراك
    if is_premium and premium_until_str:
        premium_until = datetime.datetime.fromisoformat(premium_until_str).date()
        if premium_until < today:
            # انتهى الاشتراك
            is_premium = False
            update_user_record(user_id, is_premium=0, premium_until=None)

    # إعادة تعيين المحاولات يومياً للمستخدمين غير المشتركين
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
        "🆓 لديك <b>3 محاولات مجانية يومياً</b> إذا لم تكن مشتركاً.\n"
        "📉 تُخصم المحاولة فقط إذا تم العثور على بيانات.",
        parse_mode="HTML"
    )

async def subscribe_command(update: Update, context: CallbackContext):
    message = (
        "💎 <b>اشترك للحصول على محاولات غير محدودة</b>\n\n"
        "💰 <b>السعر:</b> 3$ (شهريًا)\n"
        "🔗 <b>الدفع عبر USDT (TRC20):</b>\n"
        "<code>TKQcYbR5Bzxk7EmQMyNXA8xfSL8N7p5ivQ</code>\n\n"
        "📩 بعد الدفع، تواصل معنا لتفعيل اشتراكك:\n"
        f"<a href=\"{CONTACT_BOT_LINK}\">اضغط هنا للتواصل مع الدعم</a>\n\n"
        "⏱️ سيتم التفعيل خلال دقائق قليلة."
    )
    await update.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)

async def status_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    record = get_user_record(user_id)
    if not record:
        await update.message.reply_text("👤 أنت مستخدم جديد. لديك 3 محاولات مجانية اليوم.")
        return
    attempts_left, _, is_premium, premium_until = record
    if is_premium:
        await update.message.reply_text(f"✅ أنت <b>مشترك</b> حتى: <b>{premium_until}</b>\n🔄 المحاولات: <b>غير محدودة</b>", parse_mode="HTML")
    else:
        await update.message.reply_text(f"🔢 محاولاتك المتبقية اليوم: <b>{attempts_left}</b> من أصل 3", parse_mode="HTML")


async def get_car_details(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(f"يجب الاشتراك في القناة أولاً:\n{CHANNEL_LINK}")
        return

    plate = update.message.text.strip().upper()
    if len(plate) < 2 or not plate[0].isalpha() or not plate[1:].isdigit():
        await update.message.reply_text("تنسيق خاطئ! مثال صحيح: A123456")
        return

    attempts_left, is_premium = reset_attempts_if_needed(user_id)
    if not is_premium and attempts_left <= 0:
        await update.message.reply_text("لقد استنفدت محاولاتك المجانية لهذا اليوم. اشترك للمحاولات غير المحدودة: /subscribe")
        return

    code_char = plate[0]
    number_part = plate[1:]
    details = await fetch_car_plate_data(code_char, number_part)

    if details:
        await update.message.reply_text(
            f"🚗 <b>تفاصيل لوحة {plate}:</b>\n\n"
            f"👤 <b>المالك:</b> {details.get('owner_name')}\n"
            f"📞 <b>الهاتف:</b> {details.get('owner_tel')}\n"
            f"🚘 <b>نوع السيارة:</b> {details.get('car_type_full')}\n"
            f"🎨 <b>اللون:</b> {details.get('color')}\n"
            f"🛠️ <b>الاستخدام:</b> {details.get('usage')}\n"
            f"🆔 <b>الشاسيه:</b> {details.get('chassis_number')}\n"
            f"🔧 <b>المحرك:</b> {details.get('engine_details')}\n\n"
            f"📊 المحاولات المتبقية: <b>{'∞' if is_premium else attempts_left - 1}/{'∞' if is_premium else MAX_FREE_ATTEMPTS}</b>",
            parse_mode="HTML"
)

        if not is_premium:
            decrement_attempt(user_id)
    else:
        await update.message.reply_text(
           "❌ <b>لم يتم العثور على معلومات لهذه اللوحة.</b>\n"
           "✅ لم تُخصم المحاولة من رصيدك.",
           parse_mode="HTML"
)

async def fetch_car_plate_data(code_char: str, number_part: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        actual_nb_int = int(number_part)
        query = """
            SELECT 
                Nom, Prenom, TelProp, MarqueDesc, CouleurDesc, UtilisDesc,
                Chassis, Moteur, TypeDesc
            FROM CARMDI 
            WHERE ActualNB = ? AND CodeDesc = ?
        """
        cursor.execute(query, (actual_nb_int, code_char))
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
            }
    except Exception as e:
        print(f"خطأ جلب بيانات اللوحة: {e}")
        return None
    finally:
        conn.close()

def main():
    setup_user_attempts_table()
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_car_details))

    print("Ready...")
    application.run_polling()

if __name__ == '__main__':
    main()
