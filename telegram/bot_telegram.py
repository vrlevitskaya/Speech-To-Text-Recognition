import telebot
from deep_translator import GoogleTranslator
from telebot import types
from bot_utils import transcribe_audio, answer_the_question

TOKEN = ""

available_languages = GoogleTranslator().get_supported_languages()

bot = telebot.TeleBot(TOKEN)

users_choice = {'language': 'en', 'campus':'Moscow'}
feedback_dict = {}
campuses = ["Moscow","Nizhny Novgorod", "Perm", "Saint Petersburg", "HSE online"]


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
                     "for Kazakh language - kk \n"
                     "for French language - fr \n"
                     "full list can be seen here https://en.m.wikipedia.org/wiki/List_of_ISO_639_language_codes",
                     parse_mode='html')
    bot.register_next_step_handler(message, process_language)


def process_language(message):
    users_choice['language'] = message.text.lower()
    bot.send_message(message.chat.id,
                     f"The chosen language is <b>{users_choice['language']}</b>",
                     parse_mode='html')


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
    if message.text in campuses:
        users_choice['campus'] = message.text
        bot.send_message(message.chat.id,
                     f"The chosen campus is <b>{users_choice['campus']}</b>",
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


def answer_question_handler(message):
    if message.voice:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('../audio.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)
        response = transcribe_audio('../audio.ogg', users_choice['language'], users_choice['campus'])
        keyboard = types.InlineKeyboardMarkup()
        like_button = types.InlineKeyboardButton(text="👍 Like", callback_data=f"like_{message.message_id}")
        dislike_button = types.InlineKeyboardButton(text="👎 Dislike", callback_data=f"dislike_{message.message_id}")
        keyboard.add(like_button, dislike_button)
        bot.send_message(message.chat.id, response, reply_markup=keyboard)
        bot.register_next_step_handler(message, answer_question)
    elif message.text:
        translated = GoogleTranslator(source='auto', target='ru').translate(message.text)
        response = answer_the_question(translated, users_choice['language'], users_choice['campus'])
        keyboard = types.InlineKeyboardMarkup()
        like_button = types.InlineKeyboardButton(text="👍 Like", callback_data=f"like_{message.message_id}")
        dislike_button = types.InlineKeyboardButton(text="👎 Dislike", callback_data=f"dislike_{message.message_id}")
        keyboard.add(like_button, dislike_button)
        bot.send_message(message.chat.id, response, reply_markup=keyboard)
        bot.register_next_step_handler(message, answer_question)
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
    elif call.data.startswith('dislike_'):
        message_id = int(call.data.split('_')[1])
        feedback_dict.setdefault(message_id, 0)
        feedback_dict[message_id] -= 1
        bot.answer_callback_query(call.id, "You disliked the answer!")
    answer_question(call.message)


bot.polling()
