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

    kb = telebot.types.ReplyKeyboardMarkup()
    kb.row('/doc', '/reg', '/set', 'docs', 'datacheck')

    bot.send_message(message.chat.id,
                     "I am a robot. I have no heart. My only job is to take your data "
                     "and to convert them to arrays.\n"
                     "\n"
                     "Type /doc, to send plot an excel document.\n"
                     "Type /reg to enter your values manually.\n"
                     "Use /set to change your plot settings.\n"
                     "Use /docs to save a datasheet for advanced plotting.\n"
                     "Use /datacheck to see what data you have saved", reply_markup=kb)


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
def editdata_command(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
    keyboard.row('New', 'Edit')
    bot.send_message(message.chat.id,
                     "Shall I create a new data table, or edit yours?",
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, decision_new)


def decision_new(message):
    if message.text == 'New':
        bot.send_message(message.from_user.id,
                         'Come up with a name for your first variable.')
        bot.register_next_step_handler(message, column_naming, True)
    elif message.text == 'Edit':
        keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
        keyboard.row('Add', 'Delete')
        bot.send_message(message.from_user.id,
                         'Would you like to add or delete a new column?',
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, decision_add_del)


def decision_add_del(message):
    if message.text == 'Add':
        bot.send_message(message.from_user.id,
                         'Come up with a name for your variable.')
        bot.register_next_step_handler(message, column_naming)
    elif message.text == 'Delete':
        bot.send_message(message.from_user.id,
                         'Which variable would you like to delete?')
        bot.register_next_step_handler(message, column_delete)


def column_delete(message):
    val = message.text
    data = get_dataframe(message.chat.id)
    try:
        del data[val]
        bot.send_message(message.chat.id,
                         'I have successfully deleted that column.')
        update_dataframe(message.chat.id, data)
    except KeyError:
        bot.send_message(message.chat.id,
                         "I did not manage to delete that column. But you don't have to worry, "
                         "there never was such a column...")
    keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
    keyboard.row('Yes', 'No')
    bot.send_message(message.chat.id,
                     "Should wee keep going?",
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, decision_return)


def decision_return(message):
    if message.text == 'Yes':
        keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
        keyboard.row('Add', 'Delete')
        bot.send_message(message.from_user.id,
                         'Would you like to add or delete a new column?',
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, decision_add_del)
    else:
        bot.send_message(message.chat.id, 'Here is your data:')
        data = get_dataframe(message.chat.id)
        bot.send_message(message.from_user.id, data.to_string(index=False))
        bot.send_message(message.chat.id, "Please enter two columns that you would like to plot")
        bot.register_next_step_handler(message, trans_to_plot)


def trans_to_plot(message):
    col = message.text.split()
    data = get_dataframe(message.chat.id)
    names = list(data)
    if len(col) != 2 or col[0] not in names or col[1] not in names:
        bot.send_message(message.chat.id, "Oops... Please enter two correct columns:")
        bot.register_next_step_handler(message, trans_to_plot)
    else:
        x = list(data[col[0]])
        y = list(data[col[1]])
        bot_plot(message, x, y, col[0], col[1])


def column_naming(message, init=False):
    column_title = str(message.text)
    bot.send_message(message.from_user.id,
                     'Now enter the values for that column.')
    bot.register_next_step_handler(message, table_content_change, column_title, init)


def table_content_change(message, column_title, init=False):
    val = message.text
    val = val.replace(',', '.')
    try:
        if init:
            data = reset_user_dataframe(message.chat.id)
        else:
            data = get_dataframe(message.chat.id)
        new_column = list(map(float, val.split()))
        if len(new_column) != len(data) and not init:
            bot.send_message(message.chat.id,
                             "Unfortunately, a column must have the same length as your table.")
        else:
            data[column_title] = new_column
            update_dataframe(message.chat.id, data)
            bot.send_message(message.chat.id,
                             "Successfully added a new column!")
        keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
        keyboard.row('Yes', 'No')
        bot.send_message(message.chat.id,
                         "Should wee keep going?",
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, decision_return)
    except ValueError:
        bot.send_message(message.chat.id, "I'm used to those old man tricks. "
                                          "We are not close enough yet to plot strings.\n"
                                          " Please enter valid data:")
        bot.register_next_step_handler(message, table_content_change, column_title, init)


@bot.message_handler(commands=["showdata"])
def data_show(message):
    data = get_dataframe(message.chat.id)
    bot.send_message(message.from_user.id, str(data))


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
             x_label,
             y_label,
             init=True,
             grid=None,
             x_tick=None,
             y_tick=None,
             title=None,
             cdots=None,
             mnk=None,
             ):
    data = read_user_data(message.chat.id)

    if init:
        kb = telebot.types.ReplyKeyboardMarkup(True, True)
        kb.row('Yes', 'No')
        bot.send_message(message.chat.id,
                         'Do you need grid?', reply_markup=kb)
        bot.register_next_step_handler(message, bot_plot, x, y, x_label, y_label, False)
    elif isinstance(grid, type(None)):
        grid = message.text.lower()
        bot.send_message(message.chat.id,
                         "Come up with a tick for the x axis")
        bot.register_next_step_handler(message, bot_plot, x, y, x_label, y_label, False, grid)
    elif isinstance(x_tick, type(None)):
        try:
            x_tick = message.text
            x_tick = x_tick.replace(',', '.')
            x_tick = float(x_tick)
            bot.send_message(message.chat.id, "Come up with a tick for the y axis:")
            bot.register_next_step_handler(message, bot_plot, x, y, x_label, y_label, False, grid, x_tick)
        except ValueError:
            bot.send_message(message.chat.id, "Please be serious. I'm kind of bored by that old trick")
            bot.send_message(message.chat.id, "Please enter x tick once again.")
            bot.register_next_step_handler(message, bot_plot, x, y, x_label, y_label, False, grid)
    elif isinstance(y_tick, type(None)):
        try:
            y_tick = message.text
            y_tick = y_tick.replace(',', '.')
            y_tick = float(y_tick)
            bot.send_message(message.chat.id, "Come up with a plot title")
            bot.register_next_step_handler(message, bot_plot, x, y, x_label, y_label, False, grid, x_tick, y_tick)
        except ValueError:
            bot.send_message(message.chat.id, "Is that some human inside joke?")
            bot.send_message(message.chat.id, "Please enter y tick once again.")
            bot.register_next_step_handler(message, bot_plot, x, y, x_label, y_label, False, grid, x_tick)
    elif isinstance(title, type(None)):
        kb = telebot.types.ReplyKeyboardMarkup(True, True)
        kb.row('Yes', 'No')
        title = message.text
        bot.send_message(message.chat.id, 'Would you like to connect the dots?', reply_markup=kb)
        bot.register_next_step_handler(message, bot_plot, x, y, x_label, y_label, False, grid, x_tick, y_tick, title)
    elif isinstance(cdots, type(None)):
        cdots = message.text.lower()
        kb = telebot.types.ReplyKeyboardMarkup(True, True)
        kb.row('Yes', 'No')
        bot.send_message(message.chat.id, 'Would you like to plot the best fit line(least squares)?', reply_markup=kb)
        bot.register_next_step_handler(message, bot_plot, x, y, x_label, y_label, False, grid, x_tick, y_tick, title,
                                       cdots)
    elif isinstance(mnk, type(None)):
        mnk = message.text.lower()
        plot(x, y, grid, x_tick, y_tick, title, cdots, mnk, x_label, y_label, **data['visual'])
        photo = open('plot.png', 'rb')
        bot.send_photo(message.chat.id, photo)
        increment_plot_count(message.chat.id)
        kb = telebot.types.ReplyKeyboardMarkup(True, True)
        kb.row('Yes', 'No')
        bot.send_message(message.chat.id, 'Would you like to plot something else?', reply_markup=kb)
        bot.register_next_step_handler(message, bot_plot, x, y, x_label, y_label, False, grid, x_tick, y_tick, title,
                                       cdots, mnk)
    else:
        if message.text == 'Yes':
            bot.send_message(message.chat.id,
                             "Enter x values separated by spaces:")
            bot.register_next_step_handler(message, editdata_command)
        else:
            bot.send_message(message.chat.id,
                             "It's nice to work with you human! If you want to plot something again, just press /start")


# function that reads excel file
def doc_read(message):
    try:
        data = bot.get_file(message.document.file_id)
        url = 'https://api.telegram.org/file/bot{}/{}'.format(token, data.file_path)
        x, y = excel_x_y(url)
        bot.send_message(message.chat.id,
                         'Your values are: \nx: ' + str(x) + '\ny: ' + str(y))
        bot_plot(message, x, y, init=True)
    except AttributeError:
        bot.send_message(message.chat.id, 'Sorry, something is wrong with the format. Please send the file again')
        bot.register_next_step_handler(message, doc_read)


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


# the mighty and allpowerful function command
@bot.message_handler(commands=['function'])
def function_command(message):
    bot.send_message(message.chat.id,
                     "Type an expression. Make sure the variables are single-letter.")
    bot.register_next_step_handler(message, enter_function)


# the first child of the function
def enter_function(message):
    expr = Equation(message.text)
    variables = expr.symbols_sting
    enter_variables(message, variables, expr)


# the second child of the function
def enter_variables(message, variables, expr, result=None):
    if result is None:
        result = []
    if len(variables) != 0:
        bot.send_message(message.chat.id,
                         "What data column would you like to use for variable " + variables[0] + "?")
        bot.register_next_step_handler(message, enter_col_for_var, variables, result, expr)
    else:
        bot.send_message(message.chat.id,
                         "Enter the name of an existing column or a new one.")
        bot.register_next_step_handler(message, save_result_to_column(), result, expr)


# the third child of the funciton
def enter_col_for_var(message, variables, result, expr):
    data = get_dataframe(message.chat.id)
    val = message.text
    try:
        result.append(np.array(data[val]))
        variables.pop(0)
        enter_variables(message, variables, expr, result)
    except KeyError:
        bot.send_message(message.chat.id,
                         "No such column found... Just try again from the very start!")


# the final child of the function
def save_result_to_column(message, result, expr, new=False):
    data = get_dataframe(message.chat.id)
    val = message.text
    f = expr.lambdify()
    try:
        output = list(f(*result))
        data[val] = output
        update_dataframe(message.chat.id, data)
        bot.send_message(message.chat.id,
                         "Your expression has successfully been applied to colum " + val + "!")
    except KeyError:
        bot.send_message(message.chat.id,
                         "No such column found... Just try again from the very very start!")


bot.polling(none_stop=True)
