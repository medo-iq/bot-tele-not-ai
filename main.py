import telebot
import json
from telebot import types
import os

# إعداد التوكن الخاص بالبوت
bot_token = '6586202989:AAFM-rVbnG0Z_HQQ1uLLpFx5Vjc8pXfMZcQ'
bot = telebot.TeleBot(bot_token)

# معرف المستخدم الذي يعتبر مديرًا
admin_user_id = 839473400  # استبدل بمعرف المستخدم الفعلي

# تحميل ملف الأسئلة والأجوبة
questions_and_answers_file = 'questions_and_answers.json'
unanswered_questions_file = 'unanswered_questions.json'

# التأكد من وجود ملف الأسئلة والأجوبة
try:
    with open(questions_and_answers_file, 'r', encoding='utf-8') as file:
        qa_data = json.load(file)
except (json.decoder.JSONDecodeError, FileNotFoundError):
    qa_data = {}

# التأكد من وجود ملف الأسئلة غير المجابة
try:
    with open(unanswered_questions_file, 'r', encoding='utf-8') as file:
        unanswered_questions = json.load(file)
except (json.decoder.JSONDecodeError, FileNotFoundError):
    unanswered_questions = []

# معالجة الأمر /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "   /keyboard     مرحبًا! أنا هنا للرد على أسئلتك. يمكنك استخدام الأمر لعرض لوحة المفاتيح.")

# معالجة الأمر /keyboard
@bot.message_handler(commands=['keyboard'])
def handle_keyboard(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    types_of_questions = ["python", "tool", "kali" ,"ww"]
    buttons = [types.KeyboardButton(question_type) for question_type in types_of_questions]
    keyboard.add(*buttons)

    bot.send_message(message.chat.id, "اختر نوع السؤال:", reply_markup=keyboard)

# معالجة الأمر /ask
@bot.message_handler(commands=['ask'])
def handle_ask(message):
    bot.send_message(message.chat.id, "أرسل سؤالك.")

# معالجة الأمر /list
@bot.message_handler(commands=['list'])
def handle_list(message):
    if qa_data:
        response = "الأسئلة المتوفرة:\n\n"
        response += "\n".join(qa_data.keys())
    else:
        response = "لا توجد أسئلة متوفرة حالياً."

    bot.send_message(message.chat.id, response)

# معالجة الأمر /add_question
@bot.message_handler(commands=['add_question'])
def handle_add_question(message):
    if message.from_user.id == admin_user_id:
        bot.send_message(message.chat.id, "أرسل السؤال الجديد:")
        bot.register_next_step_handler(message, process_new_question)
    else:
        bot.send_message(message.chat.id, "أنت لا تمتلك صلاحيات الإدارة.")

# معالجة السؤال الجديد
def process_new_question(message):
    if message.from_user.id == admin_user_id:
        new_question = message.text
        bot.send_message(message.chat.id, "أرسل الجواب على السؤال:")
        bot.register_next_step_handler(message, lambda msg: process_new_answer(msg, new_question))
    else:
        bot.send_message(message.chat.id, "أنت لا تمتلك صلاحيات الإدارة.")

# معالجة الجواب على السؤال الجديد
def process_new_answer(message, new_question):
    new_answer = message.text
    bot.send_message(message.chat.id, "أرسل تفاصيل السؤال:")
    bot.register_next_step_handler(message, lambda msg: save_new_question(msg, new_question, new_answer))

# حفظ السؤال الجديد في ملف الأسئلة والأجوبة
def save_new_question(message, new_question, new_answer):
    new_details = message.text
    qa_data[new_question] = {'answer': new_answer, 'details': new_details}

    with open(questions_and_answers_file, 'w', encoding='utf-8') as file:
        json.dump(qa_data, file, ensure_ascii=False)

    bot.send_message(message.chat.id, "تم إضافة السؤال بنجاح.")

# معالجة الأوامر الخاصة بالمدير
@bot.message_handler(commands=['medo'])
def handle_admin_commands(message):
    if message.from_user.id == admin_user_id:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        admin_commands = ["/add_question", "/list_unanswered", "/qa_details"]
        buttons = [types.KeyboardButton(command) for command in admin_commands]
        keyboard.add(*buttons)

        bot.send_message(message.chat.id, "اختر الأمر الإداري:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "أنت لا تمتلك صلاحيات الإدارة.")

# معالجة الأمر /list_unanswered
@bot.message_handler(commands=['list_unanswered'])
def handle_list_unanswered(message):
    if message.from_user.id == admin_user_id:
        if unanswered_questions:
            response = "الأسئلة غير المجابة:\n\n"
            response += "\n".join(unanswered_questions)
        else:
            response = "لا توجد أسئلة غير مجابة حالياً."

        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "أنت لا تمتلك صلاحيات الإدارة.")

# معالجة الأمر /qa_details
@bot.message_handler(commands=['qa_details'])
def handle_qa_details(message):
    if message.from_user.id == admin_user_id:
        with open(questions_and_answers_file, 'rb') as file:
            bot.send_document(message.chat.id, file)
    else:
        bot.send_message(message.chat.id, "أنت لا تمتلك صلاحيات الإدارة.")

# معالجة الرسائل الواردة
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.lower()

    # إذا كتب المستخدم "نوع السؤال"، قم بإرسال أزرار الاقتراح
    if "نوع السؤال" in user_input:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        types_of_questions = ["python", "tool", "kali" ,"ww"]
        buttons = [types.KeyboardButton(question_type) for question_type in types_of_questions]
        keyboard.add(*buttons)

        bot.send_message(message.chat.id, "اختر نوع السؤال:", reply_markup=keyboard)
    else:
        # البحث عن الكلمة المفتاحية في الأسئلة
        matching_questions = [question for question in qa_data.keys() if user_input in question.lower()]

        if matching_questions:
            response = ""
            for matched_question in matching_questions:
                answer = qa_data[matched_question]['answer']
                details = qa_data[matched_question]['details']
                response += f"السؤال: {matched_question}\nالجواب: {answer}\nتفاصيل السؤال: {details}\n\n"
            bot.send_message(message.chat.id, response)
        else:
            # إذا لم يكن هناك جواب، قم بتخزين السؤال في ملف الأسئلة غير المجابة
            unanswered_questions.append(user_input)

            with open(unanswered_questions_file, 'w', encoding='utf-8') as file:
                json.dump(unanswered_questions, file, ensure_ascii=False)

            response = "آسف، لا يوجد جواب على هذه الكلمة. تم تسجيل السؤال للرد عليه لاحقًا."
            bot.send_message(message.chat.id, response)

# تشغيل البوت
if __name__ == "__main__":
    bot.polling(none_stop=True)
