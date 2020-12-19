import telebot
from config import token
from K_user_data import *

bot = telebot.TeleBot(token)


@bot.message_handler(commands=["editdata"])
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


def column_naming(message, init=False):
    column_title = str(message.text)
    bot.send_message(message.from_user.id,
                     'Now enter the values for that column.')
    bot.register_next_step_handler(message, table_content_change, column_title, init)


def table_content_change(message, column_title, init=False):
    val = message.text
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


@bot.message_handler(commands=["showdata"])
def data_show(message):
    data = get_dataframe(message.chat.id)
    bot.send_message(message.from_user.id,
                     "The data you have saved is:\n" + str(data))


bot.polling(none_stop=True)
