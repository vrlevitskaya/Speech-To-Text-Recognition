import telebot
from deep_translator import GoogleTranslator
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from bot_utils import transcribe_audio, answer_the_question

TOKEN = ""

available_languages = GoogleTranslator().get_supported_languages()

bot = telebot.TeleBot(TOKEN)

users_choice = {'language': 'en'}


@bot.message_handler(commands=['start'])
def send_message(message):
    bot.send_message(message.chat.id,
                     f"Hello, {message.from_user.first_name}! \n"
                     "I'm HSE Bot for applicants. \n"
                     "Default language is English. \n"
                     "Use command /choose_language to choose the preferable language or \n"
                     "/ask_question to ask your questions about HSE application process",
                     parse_mode='html')


@bot.message_handler(commands=['help'])
def send_contacts(message):
    bot.send_message(message.chat.id, 'If any mistakes or problems: https://t.me/vlone_l \n'
                                      'Application Committee <b>Moscow</b> +7 (495) 771-32-42, +7 (495) 916-88-44 \n'
                                      'Application Committee <b>Nizhny Novgorod</b> +7 (831) 432-78-76 pknn@hse.ru \n'
                                      'Application Committee <b>Saint Petersburg</b> +7 (812) 644-62-12 '
                                      'abitur-spb@hse.ru \n'
                                      'Application Committee <b>Perm</b> +7 (342) 200 96 96 abitur.perm@hse.ru' , parse_mode='html')


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


@bot.message_handler(commands=['ask_question'])
def answer_question(message):
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("Record question"))
    markup.add(KeyboardButton("Type question"))
    msg = bot.send_message(message.chat.id,
                           f"I'm ready to answer any question about HSE application process",
                           parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(msg, process_question)


def process_question(message):
    if message.text == "Record question":
        bot.send_message(message.chat.id, "Please record your question and send it.")
        bot.register_next_step_handler(message, record_audio)
    elif message.text == "Type question":
        bot.send_message(message.chat.id, "Please type your question.")
        bot.register_next_step_handler(message, type_question)
    else:
        msg = bot.send_message(message.chat.id,
                         f"Please, choose one of the available options")
        bot.register_next_step_handler(msg, process_question)


def record_audio(message):
    if message.voice:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('../audio.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)
        response = transcribe_audio('../audio.ogg', users_choice['language'])
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Please send a voice message.")


def type_question(message):
    response = answer_the_question(message.text, users_choice['language'])
    bot.send_message(message.chat.id, response)


bot.polling()
