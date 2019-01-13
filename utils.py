import numpy as np
import pandas as pd
import random
import string
import csv


def euclidean_distance(a, b):
    """
    计算a,b之间的欧几里得距离
    :param a: 点a位置
    :param b: 点b位置
    :return:
    """
    return np.sqrt(np.sum(np.power(a - b, 2)))


def edit_distance(a, b):
    """
    计算a,b字符串之间的编辑距离
    :param a: 字符串a
    :param b: 字符串b
    :return:
    """
    if not isinstance(a, str):
        raise ValueError('a should be a str')
    if not isinstance(b, str):
        raise ValueError('b should be a str')

    len_a = len(a)
    len_b = len(b)
    dis = np.zeros(len_b+1, dtype=np.int)
    for i in range(1, len_b+1):
        dis[i] = i

    for i in range(1, len_a + 1):
        # last记录a[0:i-1]与b[0:j-1]的编辑距离
        last = i - 1
        dis[0] = i
        for j in range(1, len_b + 1):
            temp = dis[j]
            if a[i-1] == b[j-1]:
                dis[j] = last
            else:
                # 插入删除代价为1，替换代价为2
                # dis[j]+1为插入代价，last+2为替换代价，dis[j-1]+1为删除代价
                dis[j] = min(dis[j] + 1, last + 2, dis[j-1] + 1)
            last = temp

    return dis[len_b]


def create_float_data_to_csv(data_count, data_dim, file_path):
    """
    创建浮点数二维数组，并存放到csv文件中
    每一行表示一个点
    :param data_count: 点的个数
    :param data_dim: 点的维度
    :param file_path: 存放文件路径
    :return:
    """
    if not isinstance(data_count, int) or data_count < 0:
        raise ValueError('data_count should be positive integer')
    if not isinstance(data_dim, int) or data_dim < 0:
        raise ValueError('data_dim should be positive integer')

    # 使用np.random生成0-1之间的随机数
    data = np.random.random((data_count, data_dim))
    data_frame = pd.DataFrame(data)
    data_frame.to_csv(file_path, index=True, sep=',')


def create_string_data_to_csv(data_count, min_length, max_length, file_path):
    """
    创建字符串数据，并存放到csv文件中
    每一行一个字符串
    :param data_count: 字符串个数
    :param min_length: 字符串的最小长度
    :param max_length: 字符串的最大长度
    :param file_path: 存放文件路径
    :return:
    """
    if not isinstance(data_count, int) or data_count < 0:
        raise ValueError('data_count should be positive integer')
    if not isinstance(min_length, int) or min_length < 0:
        raise ValueError('min_length should be positive integer')
    if not isinstance(max_length, int) or max_length < 0:
        raise ValueError('max_length should be positive integer')
    if min_length > max_length:
        raise ValueError('min_length greater than max_length')

    with open(file_path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['index', 'string_data'])
        for i in range(data_count):
            length = random.randint(min_length, max_length)
            # 从数字和ascii字符中随机生成长度为length的字符串
            str_data = ''.join(random.sample(string.ascii_letters + string.digits, length))
            writer.writerow([i, str_data])
