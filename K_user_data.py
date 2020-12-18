# module for logging user data

import json5
import pandas


def generate_default():
    data = {'user': 'default',
            'dataframe': None,
            'other':
                {'figsize': [6.4, 4.8],
                 'dpi': 100,
                 'approx': True},
            'text':
                {'line_label': '',
                 'dot_label': '',
                 'title': '',
                 'x_axis_name': '',
                 'y_axis_name': ''
                 },
            'visual':
                {'dot_color': 'black',
                 'line_color': 'black',
                 'linestyle': '-'},
            }
    file = open('user_data/user_default.json5', 'w')
    json5.dump(data, file, indent=2)


def get_dataframe(user_id):
    file = open('user_data/user_{}.json5'.format(user_id), 'r')
    data = json5.load(file)
    dataframe = pandas.DataFrame.from_dict(data['dataframe'])
    return dataframe


def update_dataframe(user_id, dataframe):
    file = open('user_data/user_{}.json5'.format(user_id), 'r')
    data = json5.load(file)
    dict_frame = dataframe.to_dict()
    # print('cum')
    # print(dict_frame)
    data['dataframe'] = dict_frame
    file = open('user_data/user_{}.json5'.format(user_id), 'w')
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
    json5.dump(data, file, indent=2)


def update_user_data(data):
    user = data['user']
    file = open('user_data/user_{}.json5'.format(user), 'w')
    json5.dump(data, file, indent=2)


generate_default()
