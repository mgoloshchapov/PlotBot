# module for logging user data

import json5
from types import SimpleNamespace


def generate_default():
    data = {'user': 'default',
            'text':
                {'title': '',
                 'x_axis_name': '',
                 'y_axis_name': '',
                 'line_label': '',
                 'dot_label': ''},
            'visual':
                {'dot_color': 'black',
                 'line_color': 'black', }
            }
    file = open('user_data/user_default.json5', 'w')
    json5.dump(data, file, indent=2)


def new_user(user_id):
    default_file = open('user_data/user_default.json5', 'r')
    new_file = open('user_data/user_{}.json5'.format(user_id), 'w')
    data = json5.load(default_file)
    data['user'] = user_id
    json5.dump(data, new_file, indent=2)


def read_user_data(user_id):
    file = open('user_data/user_{}.json5'.format(user_id), 'r')
    data = json5.load(file)
    return data


def modify_user_data(user_id, datum, *path):
    file = open('user_data/user_{}.json5'.format(user_id), 'r')
    data = json5.load(file)
    sub_data = data
    for i in range(len(path) - 1):
        sub_data = sub_data[path[i]]
    sub_data[path[-1]] = datum
    file = open('user_data/user_{}.json5'.format(user_id), 'w')
    data = json5.dump(data, file, indent=2)


def update_user_data(data):
    user = data['user']
    file = open('user_data/user_{}.json5'.format(user), 'w')
    json5.dump(data, file, indent=2)
