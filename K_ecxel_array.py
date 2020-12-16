import pandas as pd
import numpy as np


def excel_array_url(url):
    data = pd.read_excel(url)
    x, y = np.array(data['x']), np.array(data['y'])
    return x, y
