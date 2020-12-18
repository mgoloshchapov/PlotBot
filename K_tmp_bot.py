#  A temporary bot for testing purposes

from config import token
import telebot
from K_ecxel_array import *

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     "I am a robot. I have no heart. My only job is to take your excel files "
                     "and to convert them to arrays.")


@bot.message_handler(content_types=['text'])
def text_handler(message):
    pass


@bot.message_handler(content_types=['document'])
def file_handler(message):
    data = bot.get_file(message.document.file_id)
    print(data)
    url = 'https://api.telegram.org/file/bot{}/{}'.format(token, data.file_path)
    x, y = excel_x_y(url)

    bot.send_message(message.chat.id,
                     'Your values are: \nx: ' + str(x) + '\ny: ' + str(y))


bot.polling(none_stop=True)
