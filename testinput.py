import telebot
import pandas as pd
from Plot import plot
from telebot import types

bot = telebot.TeleBot("1489374378:AAEKhKVW91XaEgRybkOwvXRM2vjmBLInzQc", parse_mode=None)

data = pd.DataFrame({'x': [], 'y': []})
datax = []
datay = []


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Введите массивы")


# @bot.message_handler(content_types=['text','photo'])
# def start(message):
#     if message.text == '/reg':
#         bot.send_message(message.from_user.id, "Введите х")
#         bot.register_next_step_handler(message, data_x)
#     else:
#         bot.send_message(message.from_user.id, 'Напиши /reg')


@bot.message_handler(content_types=['text', 'photo'])
def start(message):
    if message.text == '/plot':
        user = message.chat.id
        # bot.send_message(message.from_user.id, "Введите х")
        bot.send_message(message.from_user.id, 'Отлично , давай начнем')
        table(user)
    else:
        bot.send_message(message.from_user.id, 'Напиши /plot')


def table(user):
    global data
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(user, 'Будем добавлять еще столбец в таблицу?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call : types.CallbackQuery, message):
    global data
    user = call.message.chat.id
    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, 'Введите название переменной(столбца)')
        column_naming(user, message)
    elif call.data == "no":
        bot.register_next_step_handler(call.id, data_show(user))


@bot.message_handler(content_types=['text', 'photo'])
def column_naming(user,message):
    global column_title
    column_title = message.text
    bot.send_message(user, 'Введите данные соответствующие переменной(столбцу)')
    bot.register_next_step_handler(message, table_content_change)


def table_content_change(message):
    data[column_title] = message.text.split()
    bot.register_next_step_handler(message, table_content_change)
    result = ' '.join(data.columns) + '\n'
    a = data.values
    for i in range(len(datax)):
        temp_string = ' '.join((a[i]))
        result += temp_string
        result += "\n"
    bot.send_message(message.from_user.id, result)
    table(message)


# def data_x(message):  # получаем x
#     global data
#     global datax
#     datax = message.text.split()
#     data['x']=datax
#     bot.send_message(message.from_user.id, 'Введите y')
#     bot.register_next_step_handler(message, data_y)


def data_show(user):  # получаем y
    global data
    # global datay
    # datay = message.text.split()
    # data['y']=datay
    result = ' '.join(data.columns) + '\n'
    a = data.values
    for i in range(len(datax)):
        temp_string = ' '.join((a[i]))
        result += temp_string
        result += "\n"
    # bot.send_message(message.from_user.id, ' '.join(datax))
    # bot.send_message(message.from_user.id, ' '.join(datay))
    bot.send_message(user, result)
    # plot(datax,datay)
    # bot.send_photo(message.from_user.id, 'plot.png')


bot.polling(none_stop=True)
