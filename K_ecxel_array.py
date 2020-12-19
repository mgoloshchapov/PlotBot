import pandas as pd
import numpy as np


def excel_x_y(url, var1, var2):
    data = pd.read_excel(url)
    x, y = np.array(data[var1]), np.array(data[var2])
    return x, y


def excel_dataframe(url):
    data = pd.read_excel(url)
    return data


def decrease_dataframe(dataframe, *args):
    new_data = dataframe.copy()
    for arg in args:
        del dataframe[arg]
    return new_data
