import numpy as np
import pandas as pd
import random
import string
import csv


def euclidean_distance(a, b):
    return np.sqrt(np.sum(np.power(a - b, 2)))


def edit_distance(a, b):
    n = len(a)
    m = len(b)
    dis = np.zeros((n + 1, m + 1), dtype=np.int)
    for i in range(1, n + 1):
        dis[i, 0] = dis[i - 1, 0] + 1
    for j in range(1, m + 1):
        dis[0, j] = dis[0, j - 1] + 1
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dis[i, j] = min(dis[i - 1, j] + 1, dis[i - 1, j - 1] + 2, dis[i, j - 1] + 1)
    return dis[n, m]


def create_float_data_to_csv(data_count, data_dim, file_path):
    data = np.random.random((data_count, data_dim))
    data_frame = pd.DataFrame(data)
    data_frame.to_csv(file_path, index=True, sep=',')


def create_string_data_to_csv(data_count, max_length, file_path):
    half_max_length = round(max_length/2)
    with open(file_path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['index', 'string_data'])
        for i in range(data_count):
            length = random.randint(half_max_length, max_length)
            str_data = ''.join(random.sample(string.ascii_letters + string.digits, length))
            writer.writerow([i, str_data])
