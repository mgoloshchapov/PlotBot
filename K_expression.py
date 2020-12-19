import telebot
import pandas as pd
import numpy as np
from K_eqation_manager import *
from K_user_data import *
from config import token

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['function'])
def function_command(message):
    bot.send_message(message.chat.id,
                     "Type an expression. Make sure the variables are single-letter.")
    bot.register_next_step_handler(message, enter_function)


def enter_function(message):
    expr = Equation(message.text)
    variables = expr.symbols_sting
    enter_variables(message, variables, expr)


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
