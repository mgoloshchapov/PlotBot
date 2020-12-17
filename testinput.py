import telebot
import pandas as pd
from config import token

bot = telebot.TeleBot(token, parse_mode=None)

data = pd.DataFrame({'x': [], 'y': []})
datax = []
datay = []


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Введите массивы")


# плохая релизаия команд
@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/reg':
        bot.send_message(message.from_user.id, "Введите х")
        bot.register_next_step_handler(message, data_x)
    else:
        bot.send_message(message.from_user.id, 'Напиши /reg')


def data_x(message):  # получаем x
    global data
    global datax
    datax = message.text.split()
    data['x'] = datax
    bot.send_message(message.from_user.id, 'Введите y')
    bot.register_next_step_handler(message, data_y)


def data_y(message):  # получаем y
    global data
    global datay
    datay = message.text.split()
    data['y'] = datay
    result = ' '.join(data.columns) + '\n'
    a = data.values
    for i in range(len(datax)):
        temp_string = ' '.join((a[i]))
        result += temp_string
        result += "\n"
    bot.send_message(message.from_user.id, ' '.join(datax))
    bot.send_message(message.from_user.id, ' '.join(datay))
    bot.send_message(message.from_user.id, result)


bot.polling()
