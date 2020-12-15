import pandas as pd


def excel_array_url(url):
    data = pd.read_excel(url)
    x, y = list(data['x']), list(data['y'])
    return x, y
