import telebot
import pandas as pd
from telebot import types

bot = telebot.TeleBot("1489374378:AAEKhKVW91XaEgRybkOwvXRM2vjmBLInzQc", parse_mode=None)

data = pd.DataFrame()

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/plot':
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
        keyboard1.row('Да', 'Нет')
        bot.send_message(message.chat.id, 'Будем добавлять еще столбец в таблицу?', reply_markup=keyboard1)
        bot.register_next_step_handler(message , decision)
    else:
        bot.send_message(message.from_user.id, 'Напиши /plot')


@bot.message_handler(content_types=['text'])
def decision(message):
    bot.send_message(message.from_user.id, ' тут'+ message.text)
    if message.text == 'Да':
        bot.send_message(message.from_user.id, 'Введите название переменной(столбца)')
        bot.register_next_step_handler(message, column_naming)
    elif message.text == 'Нет':
        bot.send_message(message.from_user.id,'Перейдем к проверке введенных данных')
        data_show(message)
    else:
        bot.send_message(message.from_user.id,'Шизоид ты как это сделал, перезапускай все')

def column_naming(message):
    bot.send_message(message.from_user.id, 'секция с названием')
    global column_title
    column_title = str(message.text)
    bot.send_message(message.from_user.id, 'Введите данные соответствующие переменной(столбца)')
    bot.register_next_step_handler(message, table_content_change)


@bot.message_handler(content_types=['text'])
def table_content_change(message):
    global column_title
    bot.send_message(message.from_user.id, 'aaaaaa')
    data[column_title] = message.text.split()
    result = ' '.join(data.columns) + '\n'
    a = data.values
    for i in range(len(data[column_title])):
        temp_string = ' '.join((a[i]))
        result += temp_string
        result += "\n"
    bot.send_message(message.chat.id, result)
    keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
    keyboard1.row('Да', 'Нет')
    bot.send_message(message.chat.id, 'Будем добавлять еще столбец в таблицу?', reply_markup=keyboard1)
    bot.register_next_step_handler(message, decision)

@bot.message_handler(content_types=['text'])
def data_show(message):
    global data
    result = ' '.join(data.columns) + '\n'
    a = data.values
    for i in range(len(data[column_title])):
        temp_string = ' '.join((a[i]))
        result += temp_string
        result += "\n"
    bot.send_message(message.from_user.id, result)
    bot.register_next_step_handler(message, start)


bot.polling(none_stop=True)
