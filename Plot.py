import matplotlib.pyplot as plt
import numpy as np

TOKEN = '1413803675:AAFLUeKKJ1Y59N43-7ZDlbRLd4dqtlHbojg'


def plot(x, y,
         dot_color='black',
         line_color='black',
         title='',
         x_axis_name='',
         y_axis_name='',
         line_label='',
         dot_label=''):

    plt.title(title)
    plt.xlabel(x_axis_name)
    plt.ylabel(y_axis_name)

    plt.plot(x, y, color=line_color, label=line_label)  # line

    plt.scatter(x, y, color=dot_color, label=dot_label)  # dots

    A = np.vstack([x, np.ones(len(x))]).T  # least square
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]

    plt.plot(x, m*x + c)

    if line_label != '' or dot_label != '':
        plt.legend()

    plt.savefig('plot.png')
