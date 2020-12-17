import matplotlib.pyplot as plt
import numpy as np


def plot(x, y,
         x_label,
         x_tick,
         y_label,
         y_tick,
         title,
         dot_color='black',
         line_color='black',
         line_label='',
         dot_label='',
         ):

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

    plt.xticks([min(x) + i*x_tick for i in range(round((max(x)-min(x))/x_tick)+1)])
    plt.yticks([min(y) + i * y_tick for i in range(round((max(y) - min(y)) / y_tick) + 1)])
    plt.grid()

    plt.plot(x, y, color=line_color, label=line_label)  # line

    plt.scatter(x, y, color=dot_color, label=dot_label)  # dots

    A = np.vstack([x, np.ones(len(x))]).T  # least square
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]

    plt.plot(x, m*x + c)

    if line_label != '' or dot_label != '':
        plt.legend()

    plt.savefig('plot.png')
    plt.clf()
