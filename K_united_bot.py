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
                     "Type /doc, to send plot an excel document, type /reg to enter your values manually.\n"
                     "Use /set to change your plot settings.\n"
                     "Use /docs to save a datasheet for advanced plotting.\n"
                     "Use /datacheck to see what data you have saved")


# function for checking data
@bot.message_handler(commands=['datacheck'])
def data_check(message):
    dataframe = get_dataframe(message.chat.id)
    bot.send_message(message.chat.id,
                     "Your data is:\n" + str(dataframe))

# function for reading excel files
@bot.message_handler(commands=['doc'])
def doc_command(message):
    bot.send_message(message.chat.id,
                     "Please send an excel file with two columns named 'x' and 'y' "
                     "containing the data you want to plot.")
    bot.register_next_step_handler(message, doc_read)


# function for saving user's data
@bot.message_handler(commands=['docs'])
def docs_command(message):
    bot.send_message(message.chat.id,
                     "Please send an excel file with your data.")
    bot.register_next_step_handler(message, doc_save)


# function for reading manual input
@bot.message_handler(commands=['reg'])
def reg_command(message, x=None, y=None):
    if message.text == '/reg':
        bot.send_message(message.chat.id,
                         "Enter x values separated by spaces:")
        bot.register_next_step_handler(message, reg_command)
    else:
        if isinstance(x, type(None)):
            x = np.array(list(map(float, message.text.split())))
            bot.send_message(message.chat.id,
                             "Enter y values separated by spaces:")
            bot.register_next_step_handler(message, reg_command, x)
        elif isinstance(y, type(None)):
            y = np.array(list(map(float, message.text.split())))
            if len(x) != len(y):
                bot.send_message(message.chat.id, 'Some of the data is missing. Do not play with me, human!')
                bot.send_message(message.chat.id, "Give it a try. Enter the x values separated by spaces one more time:")
                bot.register_next_step_handler(message, reg_command, None, None)
            else:
                bot.send_message(message.chat.id,
                                 'Your values are: \nx: ' + str(x) + '\ny: ' + str(y))
                bot_plot(message, x, y, init=True)


# settings command
@bot.message_handler(commands=['set'])
def set_command(message, setting=None):
    settings_text = "Here are the settings you can change:\n" \
                    "0. Reset all settings to default\n" \
                    "1. Figure size (two numbers, the dimensions of the plot in inches)\n" \
                    "2. DPI (one number, the dpi of the plot)\n" \
                    "3. Use the least squares approximation (Y/N)\n" \
                    "4. Dot color (color name)\n" \
                    "5. Line color (color name)\n" \
                    "6. Line style (line styles supported by pyplot)\n" \
                    "7. Line label (string)\n" \
                    "8. Dot label (string)\n" \
                    "9. Title (string)\n" \
                    "10. X axis name (string)\n" \
                    "11. Y axis name (string)\n" \
                    "Type the number of the setting you'd like to change."
    settings_paths = (None, ["other", "figsize"], ["other", "dpi"], ["other", "approx"],
                      ["visual", "line_color"], ["visual", "dot_color"], ["visual", "lineslyle"],
                      ["text", "line_label"], ["text", "dot_label"], ["text", "title"],
                      ["text", "x_axis_name"], ["text", "y_axis_name"])
    # 1 is str, 2 is Y/N to boolean, 3 is int, 4 is list
    settings_types = (None, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1)
    if isinstance(setting, type(None)):
        bot.send_message(message.chat.id, settings_text)
        bot.register_next_step_handler(message, set_command, 'pending')
    elif setting == 'pending':
        try:
            setting = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id,
                             "Sorry, I did not get that...")
        if setting == 0:
            new_user(message.chat.id)
            bot.send_message(message.chat.id,
                             "Your settings have been reset.")
        elif setting <= 11:
            bot.send_message(message.chat.id,
                             "Enter the value you's like to change that setting to.")
            bot.register_next_step_handler(message, set_command, setting)
        else:
            bot.send_message(message.chat.id,
                             "Sadly, there is no such setting...")
    else:
        if settings_types[setting] == 1:
            output = message.text
        elif settings_types[setting] == 2:
            if 'N' in message.text:
                output = True
            elif 'Y' in message.text:
                output = False
            else:
                bot.send_message(message.chat.id,
                                 "Sorry, I did not get that...")
                return
        elif settings_types[setting] == 3:
            try:
                output = int(message.text)
            except ValueError:
                bot.send_message(message.chat.id,
                                 "Sorry, I did not get that...")
                return
        elif settings_types[setting] == 4:
            try:
                output = list(map(float, message.text.split()))
            except ValueError:
                bot.send_message(message.chat.id,
                                 "Sorry, I did not get that...")
                return
        modify_user_data(message.chat.id, output, *settings_paths[setting])
        bot.send_message(message.chat.id,
                         "Your settings have successfully been changed!")


# get saved settings
@bot.message_handler(commands=['getset'])
def getset_command(message):
    data = read_user_data(message.chat.id)
    settings = dict()
    settings.update(data["other"])
    settings.update(data["visual"])
    settings.update(data["text"])
    output = ''
    for key in settings.keys():
        output += key + ': ' + str(settings[key]) + '\n'
    bot.send_message(message.chat.id,
                     "Your settings are:\n" + output)


# function that asks for axis names, and sends plot to user
def bot_plot(message, x, y,
             grid=None,
             x_label=None,
             x_tick=None,
             y_label=None,
             y_tick=None,
             title=None,
             cdots=None,
             mnk=None,
             init=False):
    data = read_user_data(message.chat.id)

    if init:
        bot.send_message(message.chat.id,
                         'Do you need grid?(y/n)')
        bot.register_next_step_handler(message, bot_plot, x, y)
    elif isinstance(grid, type(None)):
        grid = message.text.lower()
        if 'y' in grid:
            grid = 'yes'
        bot.send_message(message.chat.id,
                         "Come up with a name for the x axis:")
        bot.register_next_step_handler(message, bot_plot, x, y, grid)
    elif isinstance(x_label, type(None)):
        x_label = message.text
        bot.send_message(message.chat.id,
                         "Come up with a tick for the x axis")
        bot.register_next_step_handler(message, bot_plot, x, y, grid, x_label)
    elif isinstance(x_tick, type(None)):
        try:
            x_tick = message.text
            x_tick = x_tick.replace(',', '.')
            x_tick = float(x_tick)
            bot.send_message(message.chat.id, "Come up with a name for the y axis:")
            bot.register_next_step_handler(message, bot_plot, x, y, grid, x_label, x_tick)
        except ValueError:
            bot.send_message(message.chat.id, "Please be serious. I'm kind of bored by that old trick")
            bot.send_message(message.chat.id, "Please enter x tick once again.")
            bot.register_next_step_handler(message, bot_plot, x, y, grid,  x_label)
    elif isinstance(y_label, type(None)):
        y_label = message.text
        bot.send_message(message.chat.id,
                         "Come up with a tick for the y axis")
        bot.register_next_step_handler(message, bot_plot, x, y, grid, x_label, x_tick, y_label)
    elif isinstance(y_tick, type(None)):
        try:
            y_tick = message.text
            y_tick = y_tick.replace(',', '.')
            y_tick = float(y_tick)
            bot.send_message(message.chat.id, "Come up with a plot title")
            bot.register_next_step_handler(message, bot_plot, x, y, grid, x_label, x_tick, y_label, y_tick)
        except ValueError:
            bot.send_message(message.chat.id, "Is that some human inside joke?")
            bot.send_message(message.chat.id, "Please enter y tick once again.")
            bot.register_next_step_handler(message, bot_plot, x, y, grid, x_label, x_tick, y_label)
    elif isinstance(title, type(None)):
        title = message.text
        bot.send_message(message.chat.id, 'Would you like to connect the dots?(y/n)')
        bot.register_next_step_handler(message, bot_plot, x, y, grid, x_label, x_tick, y_label, y_tick, title)
    elif isinstance(cdots, type(None)):
        cdots = message.text.lower()
        if 'y' in cdots:
            cdots = 'yes'
        bot.send_message(message.chat.id, 'Would you like to plot the best fit line(least squares)?(y/n)')
        bot.register_next_step_handler(message, bot_plot, x, y, grid, x_label, x_tick, y_label, y_tick, title, cdots)
    elif isinstance(mnk, type(None)):
        mnk = message.text.lower()
        if 'y' in mnk:
            mnk = 'yes'
        plot(x, y, grid, x_label, x_tick, y_label, y_tick, title, cdots, mnk, **data['visual'])
        photo = open('plot.png', 'rb')
        bot.send_photo(message.chat.id, photo)


# function that reads excel file
def doc_read(message):
    data = bot.get_file(message.document.file_id)
    url = 'https://api.telegram.org/file/bot{}/{}'.format(token, data.file_path)
    x, y = excel_x_y(url)
    bot.send_message(message.chat.id,
                     'Your values are: \nx: ' + str(x) + '\ny: ' + str(y))
    bot_plot(message, x, y, init=True)


# function for saving dataframes
def doc_save(message, dataframe=None):
    if isinstance(dataframe, type(None)):
        data = bot.get_file(message.document.file_id)
        url = 'https://api.telegram.org/file/bot{}/{}'.format(token, data.file_path)
        dataframe = excel_dataframe(url)
        bot.send_message(message.chat.id,
                         "You data is:\n" + str(dataframe) + "\nDo you with to save it? [Y/N]")
        bot.register_next_step_handler(message, doc_save, dataframe)
    else:
        if 'Y' in message.text:
            print(dataframe)
            update_dataframe(message.chat.id, dataframe)
            bot.send_message(message.chat.id,
                             "Your data has been saved.")
        elif 'N' in message.text:
            bot.send_message(message.chat.id,
                             "Your data has been discarded")
        else:
            bot.send_message(message.chat.id,
                             "Sorry, I did not get that...\nYour data has been discarded.")


bot.polling(none_stop=True)
