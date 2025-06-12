import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ChatMemberStatus 
import os


# 1. مفتاح API الخاص بالبوت (استبدل هذا بالمفتاح الفعلي الخاص بك)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7844820429:AAFu63mk6zkI6F0d7RneAYOeNXhJ1Yxwwy0") # من معلوماتك السابقة

# 2. معرف قناتك على تيليجرام (استبدل هذا بالمعرف الذي حصلت عليه)
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002546660006")) # من معلوماتك السابقة

# 3. رابط قناتك (للعرض على المستخدم)
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/PlateNumberLB") # من معلوماتك السابقة

# 4. رابط بوت التواصل الخاص بك (الجديد)
# استبدل YourContactBotUsername باسم المستخدم الخاص ببوت التواصل الجديد
CONTACT_BOT_LINK = os.environ.get("CONTACT_BOT_LINK", "https://t.me/splatenumberlb_bot") 

# دالة للتحقق من اشتراك المستخدم في القناة
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

# دالة بدء البوت عند تشغيله (سيبقى فيها التحقق من الاشتراك)
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(
            f"مرحباً بك! لاستخدام هذا البوت، يرجى الاشتراك في قناتنا أولاً:\n"
            f"{CHANNEL_LINK}\n"
            f"بعد الاشتراك، أرسل /start مرة أخرى."
        )
        return

    await update.message.reply_text(
        'مرحباً بك! أنا بوت البحث عن تفاصيل لوحات السيارات.\n'
        'فقط أرسل رقم لوحة السيارة بالتنسيق الصحيح (مثال: A123456).\n'
        'للمساعدة، أرسل /help.'
    )

# 5. دالة الأمر /help
async def help_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(
            f"مرحباً بك! لاستخدام هذا البوت، يرجى الاشتراك في قناتنا أولاً:\n"
            f"{CHANNEL_LINK}\n"
            f"بعد الاشتراك، أرسل /start مرة أخرى."
        )
        return

    await update.message.reply_text(
        "أهلاً بك في قسم المساعدة!\n\n"
        "إليك كيفية استخدام البوت:\n"
        "1.  **أرسل رقم لوحة السيارة:** يجب أن يكون بالتنسيق `حرف + أرقام` (مثال: `A123456`).\n"
        "    سأقوم بجلب جميع التفاصيل المتاحة عن اللوحة.\n\n"
        "**الأوامر المتاحة:**\n"
        "•   /start - لبدء المحادثة أو إعادة تشغيل البوت.\n"
        "•   /help - لعرض هذه الرسالة.\n"
        "•   /about - لمعرفة المزيد عن البوت والمطور.\n"
        "•   /channel - للانتقال إلى قناتنا الرسمية.\n"
        "•   /contact - للتواصل المباشر مع المطور."
    )

# 6. دالة الأمر /about
async def about_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(
            f"مرحباً بك! لاستخدام هذا البوت، يرجى الاشتراك في قناتنا أولاً:\n"
            f"{CHANNEL_LINK}\n"
            f"بعد الاشتراك، أرسل /start مرة أخرى."
        )
        return

    await update.message.reply_text(
        "**حول بوت تفاصيل لوحات السيارات**\n\n"
        "هذا البوت تم تطويره لمساعدتكم في الحصول على معلومات سريعة وموثوقة حول لوحات السيارات في لبنان.\n"
        "نحن نسعى لتقديم أفضل تجربة بحث ممكنة لكم.\n"
        "نسخة البوت: 1.0\n"
    )

# 7. دالة الأمر /channel
async def channel_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(
            f"مرحباً بك! لاستخدام هذا البوت، يرجى الاشتراك في قناتنا أولاً:\n"
            f"{CHANNEL_LINK}\n"
            f"بعد الاشتراك، أرسل /start مرة أخرى."
        )
        return

    await update.message.reply_text(
        f"يمكنكم متابعة قناتنا الرسمية للبوت للحصول على آخر التحديثات والأخبار والميزات الجديدة:\n"
        f"{CHANNEL_LINK}"
    )

# 8. دالة الأمر /contact
async def contact_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(
            f"مرحباً بك! لاستخدام هذا البوت، يرجى الاشتراك في قناتنا أولاً:\n"
            f"{CHANNEL_LINK}\n"
            f"بعد الاشتراك، أرسل /start مرة أخرى."
        )
        return
        
    await update.message.reply_text(
        f"إذا كان لديك أي استفسارات أو ملاحظات أو مشاكل، يمكنك التواصل مباشرةً مع المطور عبر بوت الدعم الخاص بنا:\n"
        f"{CONTACT_BOT_LINK}"
    )

# 9. دالة معالجة رسائل لوحة السيارة
async def get_car_details(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await update.message.reply_text(
            f"عذراً، يجب أن تكون مشتركاً في قناتنا لاستخدام هذه الميزة:\n"
            f"{CHANNEL_LINK}\n"
            f"بعد الاشتراك، يرجى المحاولة مرة أخرى."
        )
        return

    car_plate_input = update.message.text.strip().upper() 
    print(f"المستخدم أرسل: {car_plate_input}") 

    # التحقق من تنسيق اللوحة المدخلة (حرف واحد ثم أرقام)
    if len(car_plate_input) < 2 or not car_plate_input[0].isalpha() or not car_plate_input[1:].isdigit():
        await update.message.reply_text("عذراً، يرجى إدخال رقم اللوحة بالتنسيق الصحيح (مثال: A123456).")
        return 

    # فصل الحرف والرقم من مدخل المستخدم
    code_char = car_plate_input[0] 
    number_part = car_plate_input[1:] 

    details = await fetch_car_plate_data(code_char, number_part) 

    if details:
        response_message = (
            f"**تفاصيل لوحة السيارة: {car_plate_input}**\n"
            f"-----------------------------------\n"
            f"المالك: {details.get('owner_name', 'غير متوفر')}\n"
            f"رقم المالك: {details.get('owner_tel', 'غير متوفر')}\n"
            f"عنوان المالك: {details.get('owner_address', 'غير متوفر')}\n"
            f"نوع السيارة: {details.get('car_type_full', 'غير متوفر')}\n" # تم التعديل هنا ل car_type_full
            f"اللون: {details.get('color', 'غير متوفر')}\n"
            f"الاستخدام: {details.get('usage', 'غير متوفر')}\n"
            f"رقم الشاسيه: {details.get('chassis_number', 'غير متوفر')}\n"
            f"المحرك: {details.get('engine_details', 'غير متوفر')}"
        )
        await update.message.reply_text(response_message, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"عذراً، لم أتمكن من العثور على تفاصيل للوحة: {car_plate_input}. يرجى التحقق من الرقم والمحاولة مرة أخرى.")

# 10. دالة لجلب البيانات من قاعدة بيانات SQLite (كما هي)
async def fetch_car_plate_data(code_char: str, number_part: str):
    conn = None
    details = None
    try:
        db_path = '17-05-2022.db' 
        print(f"محاولة الاتصال بقاعدة البيانات: {db_path}") 
        conn = sqlite3.connect(db_path) 
        cursor = conn.cursor()

        try:
            actual_nb_int = int(number_part) 
            print(f"جزء الكود: '{code_char}', الجزء الرقمي للبحث: {actual_nb_int}") 
        except ValueError:
            print(f"الجزء الرقمي '{number_part}' ليس رقماً صحيحاً.")
            return None 

        query = """
            SELECT 
                Nom,            -- 0
                Prenom,         -- 1
                TelProp,        -- 2
                MarqueDesc,     -- 3
                CouleurDesc,    -- 4
                UtilisDesc,     -- 5
                Chassis,        -- 6
                Moteur,         -- 7
                Addresse,       -- 8
                TypeDesc        -- 9  <--- تم إضافة هذا
            FROM CARMDI 
            WHERE ActualNB = ? AND CodeDesc = ?
        """
        
        cursor.execute(query, (actual_nb_int, code_char)) 
        row = cursor.fetchone() 

        if row:
            owner_name = f"{row[1] or ''} {row[0] or ''}".strip() 
            if not owner_name: 
                owner_name = "غير متوفر"
            
            # **التعديل هنا:** دمج MarqueDesc و TypeDesc لإنشاء car_type_full
            # row[3] هو MarqueDesc، و row[9] هو TypeDesc
            car_type_full = f"{row[3] or ''} {row[9] or ''}".strip()
            if not car_type_full:
                car_type_full = "غير متوفر"

            details = {
                "owner_name": owner_name,
                "owner_tel": row[2] if row[2] else "غير متوفر",         
                "color": row[4] if row[4] else "غير متوفر",             
                "usage": row[5] if row[5] else "غير متوفر",             
                "chassis_number": row[6] if row[6] else "غير متوفر",    
                "engine_details": row[7] if row[7] else "غير متوفر",    
                "owner_address": row[8] if row[8] else "غير متوفر",
                "car_type_full": car_type_full # تم إضافة هذا
            }
            print(f"تم العثور على بيانات: {details}") 
        else:
            print(f"لم يتم العثور على بيانات للوحة: {code_char}{number_part}") 
        
    except sqlite3.Error as e:
        print(f"خطأ في قاعدة البيانات (sqlite3.Error): {e}")
        details = None
    except Exception as e:
        print(f"حدث خطأ غير متوقع (General Error): {e}")
        details = None
    finally:
        if conn:
            conn.close()
    return details

# 11. الدالة الرئيسية لتشغيل البوت
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # إضافة معالجات الأوامر الجديدة
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("channel", channel_command))
    application.add_handler(CommandHandler("contact", contact_command))
    
    # معالج الرسائل النصية (بعد الأوامر)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_car_details))

    print("Ready...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
