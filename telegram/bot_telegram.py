import telebot
from deep_translator import GoogleTranslator
from telebot import types
from bot_utils import transcribe_audio, answer_the_question
from gpt import write_questions_to_docx

TOKEN = "6920410900:AAFJQL1w2fpi7P99LsFIQ7Dqj_G8fbATwYE"

available_languages = GoogleTranslator().get_supported_languages(as_dict=True)
mes = ("Please, check the language code and type it again \n"
       "Lang Dictionary:\n")
for key, value in available_languages.items():
    mes += f"{key}: {value}\n"

bot = telebot.TeleBot(TOKEN)

users_choice = {}
feedback_dict = {}
campuses = ["Moscow", "Nizhny Novgorod", "Perm", "Saint Petersburg", "HSE online"]


@bot.message_handler(commands=['start'])
def send_message(message):
    bot.send_message(message.chat.id,
                     f"Hello, {message.from_user.first_name}! \n"
                     "I'm HSE Bot for applicants. \n"
                     "Default language is English. \n"
                     "Use commands: \n"
                     "/choose_language to choose the preferable language \n"
                     "/choose_campus to choose the HSE campus you are looking at\n"
                     "/ask_question to ask your questions about HSE application process\n",
                     parse_mode='html')


@bot.message_handler(commands=['help'])
def send_contacts(message):
    bot.send_message(message.chat.id, 'If any mistakes or problems: https://t.me/vlone_l \n'
                                      'Application Committee <b>Moscow</b> +7 (495) 771-32-42, +7 (495) 916-88-44 \n'
                                      'Application Committee <b>Nizhny Novgorod</b> +7 (831) 432-78-76 pknn@hse.ru \n'
                                      'Application Committee <b>Saint Petersburg</b> +7 (812) 644-62-12 '
                                      'abitur-spb@hse.ru \n'
                                      'Application Committee <b>Perm</b> +7 (342) 200 96 96 abitur.perm@hse.ru',
                     parse_mode='html')


@bot.message_handler(commands=['choose_language'])
def change_language(message):
    bot.send_message(message.chat.id,
                     "Please, type in the chat the code of preferable language \n"
                     "For example, \n"
                     "for Kazakh language - <b>kk</b> \n"
                     "for Uzbek language - <b>uz</b> \n"
                     "for Chinese (simplified) language - <b>zh-CN</b> \n"
                     "for Chinese (traditional) language - <b>zh-TW</b> \n"
                     "for Arabic language - <b>ar</b> \n"
                     "full list can be seen here https://en.m.wikipedia.org/wiki/List_of_ISO_639_language_codes",
                     parse_mode='html')
    bot.register_next_step_handler(message, process_language)


def process_language(message):
    chat_id = message.chat.id
    if message.text in available_languages.values():
        if chat_id in users_choice:
            users_choice[chat_id]['language'] = message.text
        else:
            users_choice[chat_id] = {'language': message.text}
        bot.send_message(message.chat.id,
                         f"The chosen language is <b>{users_choice[chat_id]['language']}</b>",
                         parse_mode='html')
    else:
        keyboard = types.InlineKeyboardMarkup()
        available_languages_with_codes = types.InlineKeyboardButton(text='Available languages and their codes',
                                                                    callback_data='language_codes_')
        keyboard.add(available_languages_with_codes)
        bot.send_message(message.chat.id,
                         "Sorry, this language is not supported. \n"
                         "Please, check list of supported languages, maybe there is typo in your message. \n"
                         "\n",
                         parse_mode='html',
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, process_language)


@bot.message_handler(commands=['choose_campus'])
def change_campus(message):
    bot.send_message(message.chat.id,
                     "Please, type in the chat one HSE campus from the list below \n"
                     "The default campus is <b>HSE Moscow</b> \n"
                     "Available options:\n"
                     "-Moscow\n"
                     "-Nizhny Novgorod\n"
                     "-Perm\n"
                     "-Saint Petersburg\n"
                     "-HSE online\n",
                     parse_mode='html')
    bot.register_next_step_handler(message, process_campus)


def process_campus(message):
    chat_id = message.chat.id
    if message.text in campuses:
        if chat_id in users_choice:
            users_choice[chat_id]['campus'] = message.text
        else:
            users_choice[chat_id] = {'campus': message.text}
        bot.send_message(message.chat.id,
                         f"The chosen campus is <b>{users_choice[chat_id]['campus']}</b>",
                         parse_mode='html')
    else:
        bot.send_message(message.chat.id,
                         f"Please, type one of the options",
                         parse_mode='html')
        bot.register_next_step_handler(message, process_campus)


@bot.message_handler(commands=['ask_question'])
def answer_question(message):
    bot.send_message(message.chat.id,
                     "I'm ready to answer any question about HSE application process. \n"
                     "You are able to type it in the "
                     "chat or record",
                     parse_mode='html')
    bot.register_next_step_handler(message, answer_question_handler)


def send_response(chat_id, response):
    keyboard = types.InlineKeyboardMarkup()
    like_button = types.InlineKeyboardButton(text="👍 Like", callback_data=f"like_{chat_id}")
    dislike_button = types.InlineKeyboardButton(text="👎 Dislike", callback_data=f"dislike_{chat_id}")
    keyboard.add(like_button, dislike_button)
    bot.send_message(chat_id, response, reply_markup=keyboard, parse_mode='Markdown')


def answer_question_handler(message):
    chat_id = message.chat.id
    if message.voice:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('../audio.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)
        transcribed, responses = transcribe_audio('../audio.ogg', users_choice[chat_id].get('language', 'en'),
                                                  users_choice[chat_id].get('campus', 'Moscow'))
        for i in range(len(responses)):
            write_questions_to_docx(transcribed, responses[i])
            send_response(message.chat.id, responses[i])
    elif message.text:
        translated = GoogleTranslator(source='auto', target='ru').translate(message.text)
        responses = answer_the_question(translated, users_choice[chat_id].get('language', 'en'),
                                        users_choice[chat_id].get('campus', 'Moscow'))
        for i in range(len(responses)):
            write_questions_to_docx(message.text, responses[i])
            send_response(message.chat.id, responses[i])
    else:
        bot.send_message(message.chat.id,
                         "Please, send either voice or text message!",
                         parse_mode='html')
        bot.register_next_step_handler(message, answer_question_handler)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith('like_'):
        message_id = int(call.data.split('_')[1])
        feedback_dict.setdefault(message_id, 0)
        feedback_dict[message_id] += 1
        bot.answer_callback_query(call.id, "You liked the answer!")
        answer_question(call.message)
    elif call.data.startswith('dislike_'):
        message_id = int(call.data.split('_')[1])
        feedback_dict.setdefault(message_id, 0)
        feedback_dict[message_id] -= 1
        bot.answer_callback_query(call.id, "You disliked the answer!")
        answer_question(call.message)
    elif call.data.startswith('language_codes_'):
        bot.send_message(call.message.chat.id, text=mes)
        bot.answer_callback_query(call.id)



bot.polling()
