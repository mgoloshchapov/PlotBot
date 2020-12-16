# the main body of the bot

from config import token
import telebot
from K_ecxel_array import *
from M_plot import *

bot = telebot.TeleBot(token)


# starting command
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     "I am a robot. I have no heart. My only job is to take your data "
                     "and to convert them to arrays.\n"
                     "Type /doc, to send me a excel document, type /reg to enter your values manually.")


@bot.message_handler(commands=['doc'])
def doc_command(message):
    bot.send_message(message.chat.id,
                     "Please send an excel file with two columns named 'x' and 'y' "
                     "containing the data you want to plot.")
    bot.register_next_step_handler(message, doc_read)


def bot_plot(message, x, y, x_label=None, y_label=None, init=False):
    if init:
        bot.send_message(message.chat.id, "Come up with a name for the x axis:")
        bot.register_next_step_handler(message, bot_plot, x, y)
    elif isinstance(x_label, type(None)):
        x_label = message.text
        bot.send_message(message.chat.id, "Come up with a name for the y axis:")
        bot.register_next_step_handler(message, bot_plot, x, y, x_label)
    else:
        y_label = message.text
        plot(x, y, x_axis_name=x_label, y_axis_name=y_label)
        photo = open('plot.png', 'rb')
        bot.send_photo(message.chat.id, photo)



def doc_read(message):
    print(message)
    data = bot.get_file(message.document.file_id)
    print(data)
    url = 'https://api.telegram.org/file/bot{}/{}'.format(token, data.file_path)
    x, y = excel_array_url(url)
    bot.send_message(message.chat.id,
                     'Your values are: \nx: ' + str(x) + '\ny: ' + str(y))
    bot_plot(message, x, y, init=True)


@bot.message_handler(commands=['reg'])
def reg_command(message, x=None, y=None):
    print(message.text)
    if message.text == '/reg':
        bot.send_message(message.chat.id, "Enter x values separated by spaces:")
        print(x, y)
        bot.register_next_step_handler(message, reg_command)
    else:
        if isinstance(x, type(None)):
            x = np.array(list(map(float, message.text.split())))
            bot.send_message(message.chat.id, "Enter y values separated by spaces:")
            print(x, y)
            bot.register_next_step_handler(message, reg_command, x)
        elif isinstance(y, type(None)):
            y = np.array(list(map(float, message.text.split())))
            bot.send_message(message.chat.id,
                             'Your values are: \nx: ' + str(x) + '\ny: ' + str(y))
            bot_plot(message, x, y, init=True)


bot.polling(none_stop=True)
