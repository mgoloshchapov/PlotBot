# the main body of the bot
from config import token
import telebot
from K_ecxel_array import *
from M_plot import *
from K_user_data import *

bot = telebot.TeleBot(token)


# bot greeting
@bot.message_handler(commands=['start'])
def welcome(message):
    # if a new user is detected this generates a file for them
    try:
        open('user_data/user_{}.json5'.format(message.chat.id))
    except FileNotFoundError:
        new_user(message.chat.id)

    # greeting
    logo = open('Logo.png', 'rb')
    bot.send_photo(message.chat.id, logo)
    bot.send_message(message.chat.id,
                     "I am a robot. I have no heart. My only job is to take your data "
                     "and to convert them to arrays.\n"
                     "\n"
                     "Type /doc, to send me a excel document, type /reg to enter your values manually.\n"
                     "Use /set to change your plot settings")



# function for reading excel files
@bot.message_handler(commands=['doc'])
def doc_command(message):
    bot.send_message(message.chat.id,
                     "Please send an excel file with two columns named 'x' and 'y' "
                     "containing the data you want to plot.")
    bot.register_next_step_handler(message, doc_read)


# function for reading manual input
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


@bot.message_handler(commands=['set'])
def set_command(message, setting=None):
    if isinstance(setting, type(None)):
        bot.send_message(message.chat.id, "What setting would you like to modify: "
                                          "line color or dot color?")
        bot.register_next_step_handler(message, set_command, 'pending')
    elif setting == 'pending':
        if 'dot' in message.text:
            setting = 'dot_color'
        elif 'line' in message.text:
            setting = 'line_color'
        else:
            bot.send_message(message.chat.id, 'Sorry, I did not get that...')
        if setting != 'pending':
            bot.send_message(message.chat.id, 'What color would you like?')
            bot.register_next_step_handler(message, set_command, setting)
    else:
        modify_user_data(message.chat.id, message.text, 'visual', setting)


# function that asks for axis names, and sends plot to user
def bot_plot(message, x, y, x_label=None, x_tick=None, y_label=None, y_tick=None, title=None, init=False):
    data = read_user_data(message.chat.id)

    if init:
        bot.send_message(message.chat.id, "Come up with a name for the x axis:")
        bot.register_next_step_handler(message, bot_plot, x, y)

    elif isinstance(x_label, type(None)):
        x_label = message.text
        bot.send_message(message.chat.id, "Come up with a tick for the x axis")
        bot.register_next_step_handler(message, bot_plot, x, y, x_label)

    elif isinstance(x_tick, type(None)):
        x_tick = float(message.text)
        bot.send_message(message.chat.id, "Come up with a name for the y axis:")
        bot.register_next_step_handler(message, bot_plot, x, y, x_label, x_tick)

    elif isinstance(y_label, type(None)):
        y_label = message.text
        bot.send_message(message.chat.id, "Come up with a tick for the y axis")
        bot.register_next_step_handler(message, bot_plot, x, y, x_label, x_tick, y_label)

    elif isinstance(y_tick, type(None)):
        y_tick = float(message.text)
        bot.send_message(message.chat.id, "Come up with a plot title")
        bot.register_next_step_handler(message, bot_plot, x, y, x_label, x_tick, y_label, y_tick)

    else:
        title = message.text
        plot(x, y, x_label, x_tick, y_label, y_tick, title, **data['visual'])
        photo = open('plot.png', 'rb')
        bot.send_photo(message.chat.id, photo)



# function that reads excel file
def doc_read(message):
    print(message)
    data = bot.get_file(message.document.file_id)
    print(data)
    url = 'https://api.telegram.org/file/bot{}/{}'.format(token, data.file_path)
    x, y = excel_array_url(url)
    bot.send_message(message.chat.id,
                     'Your values are: \nx: ' + str(x) + '\ny: ' + str(y))
    bot_plot(message, x, y, init=True)


bot.polling(none_stop=True)
