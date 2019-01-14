from vp_tree import VPTree
from utils import euclidean_distance, edit_distance
import os
import pandas as pd
import numpy as np
import random
import string
import math


class ConsoleApp:
    """
    控制台应用，用来接受用户输入，输入数据，创建VP tree等
    """
    def __init__(self):
        """
        构造函数
        """
        self._data_type = None
        self._data_dim = 0
        self._vp_tree = None
        pass

    def main(self):
        """
        主函数，用来接受用户的指令并执行特定的操作
        :return:
        """
        self._print_tips()
        while True:
            selection = input('\nplease input a integer to select an operation:')
            try:
                # 将selection转化为int
                selection = int(selection)
            except Exception as e:
                pass
            # 检查类型转换是否成功
            if not isinstance(selection, int):
                print("wrong input: ", selection)
                continue
            # 退出console app
            if selection == 0:
                print('exit')
                break
            # 从键盘中输入数据并创建vp tree
            elif selection == 1:
                result = self._get_data_from_console()
                if result['success'] is False:
                    continue
                else:
                    self._data_type = result['data_type']
                    self._data_dim = result['data_dim']
                    if self._data_type == 'string':
                        self._vp_tree = VPTree(result['data'], edit_distance, data_type=self._data_type)
                        print('create vp tree successfully')
                    else:
                        self._vp_tree = VPTree(result['data'], euclidean_distance, data_type=self._data_type)
                        print('create vp tree successfully')
            # 从文件中读取数据，并创建vp tree
            elif selection == 2:
                result = self._get_data_from_file()
                if result['success'] is False:
                    continue
                else:
                    self._data_type = result['data_type']
                    self._data_dim = result['data_dim']
                    if self._data_type == 'string':
                        self._vp_tree = VPTree(result['data'], edit_distance, data_type=self._data_type)
                        print('create vp tree successfully')
                    else:
                        self._vp_tree = VPTree(result['data'], euclidean_distance, data_type=self._data_type)
                        print('create vp tree successfully')
            # 在创建好的vp tree中进行搜索
            elif selection == 3:
                if self._vp_tree is None:
                    print('please create a vp tree first')
                else:
                    success, query_data = self._input_query_data()
                    if not success:
                        print('wrong in input query data')
                        continue
                    success, max_distance = ConsoleApp._input_a_num('max distance', float, 0)
                    if not success:
                        continue

                    search_result = self._vp_tree.search(query_data, max_distance)
                    print('find %d result, calculate distance %d times. (enter y to print all neighbors)' %
                          (len(search_result['neighbors']), search_result['cal_distance_times']))
                    whether_print = input()
                    if whether_print == 'y':
                        self._print_neighbors(search_result['neighbors'])
            # 进行vp tree的性能测试
            elif selection == 4:
                min_length = max_length = min_value = max_value = -1
                if self._vp_tree is None:
                    print('please create a vp tree first')
                else:
                    # 输入自动测试次数
                    success, testing_times = ConsoleApp._input_a_num('testing times each round', int, 0)
                    if not success:
                        continue
                    if self._data_type == 'string':
                        # 输入测试用的字符串的最小长度与最大长度
                        success, min_length = ConsoleApp._input_a_num('min length of string', int)
                        if not success:
                            continue
                        success, max_length = ConsoleApp._input_a_num('max length of string', int, min_length)
                        if not success:
                            continue
                    else:
                        # 输入测试数据的最小值与最大值
                        success, min_value = ConsoleApp._input_a_num('min value', float)
                        if not success:
                            continue
                        success, max_value = ConsoleApp._input_a_num('max value', float, min_value)
                        if not success:
                            continue
                    # ----------------------
                    # 输入测试用的max_distance
                    success, distance_start = ConsoleApp._input_a_num('start of max distance', float, 0)
                    if not success:
                        continue
                    success, distance_end = ConsoleApp._input_a_num('end of max distance', float, distance_start)
                    if not success:
                        continue
                    success, distance_interval = ConsoleApp._input_a_num('interval of max distance', float, 0)
                    if not success:
                        continue
                    # 迭代生成多组数据进行测试
                    max_distance = distance_start
                    testing_result = []
                    print('calculating.....')
                    while max_distance <= distance_end:
                        if math.floor((max_distance/distance_end)*100) % 10 == 0:
                            print('progress: %d percent' % math.floor((max_distance/distance_end)*100))
                        cal_dis_time = 0
                        for i in range(testing_times):
                            if self._data_type == 'string':
                                length = random.randint(min_length, max_length)
                                query_data = ''.join(random.sample(string.ascii_letters + string.digits, length))
                            else:
                                query_data = np.random.random(self._data_dim)
                                query_data = query_data * max_value + min_value
                            res = self._vp_tree.search(query_data, max_distance)
                            cal_dis_time += res['cal_distance_times']
                        average = cal_dis_time / testing_times
                        testing_result.append({'max_distance': max_distance, 'average_cal_dis_times': average})
                        # max_distance递增
                        max_distance += distance_interval
                    print('done')
                    print('enter y to print all average distance calculating times')
                    whether_print = input()
                    if whether_print == 'y':
                        ConsoleApp._print_average_distance_calculating_times(testing_result)
            # 清空console
            elif selection == 5:
                print("\n"*30)
                ConsoleApp._print_tips()
            else:
                print("wrong input: ", selection)
                continue

    @staticmethod
    def _print_tips():
        """
        打印提示
        :return:
        """
        print("-----------------------------------------------------\n"
              "type 1 to input data from keyboard and create a VP tree\n"
              "type 2 to input data from file and create a VP tree\n"
              "type 3 to search in VP tree\n"
              "type 4 to test performance of VP tree\n"
              "type 5 to clean the console\n"
              "type 0 to exit\n"
              "-----------------------------------------------------\n")

    @staticmethod
    def _get_data_from_console():
        """
        从控制台中获取用户的输入
        :return:
        """
        result = dict()
        result['success'] = False
        data_dim = 0
        # 输入数据的个数
        success, data_count = ConsoleApp._input_a_num('count of data', int, 0)
        if not success:
            return result

        # 输入数据的类型
        data_type = input("please input the type of data(string or num):")
        if data_type != "string" and data_type != "num":
            print("wrong data type")
            return result

        if data_type == 'num':
            # 如果数据类型是num，则需要输入数据的维度
            success, data_dim = ConsoleApp._input_a_num('dimension of point', int, 0)
            if not success:
                return result

        print("please input the data, each line is a data object.")
        if data_type == 'num':
            print("num type example (separated by commas): 1,2,3")
            data = []
            # 从键盘中读取data_count个数据点
            for i in range(data_count):
                line = input()
                line = line.split(",")
                # 当一行读取到的数据点的维度没有达到data_dim的时候，继续输入
                while len(line) < data_dim:
                    temp = input()
                    temp = temp.split(",")
                    line.extend(temp)
                try:
                    # 输入的数据是string，转化为float
                    line = [float(line_num) for line_num in line]
                    line = line[0: data_dim]
                except Exception as e:
                    print(e)
                    return result
                data.append(line)
        else:
            data = []
            for i in range(data_count):
                string = input()
                data.append(string)

        result['success'] = True
        result['data'] = data
        result['data_type'] = data_type
        result['data_dim'] = data_dim
        return result

    @staticmethod
    def _get_data_from_file():
        """
        从文件中获取用户的输入
        :return:
        """
        result = dict()
        result['success'] = False
        data_dim = 0
        data_type = input("please input the type of data(string or num):")
        # 数据数据类型，string/num
        if data_type != "string" and data_type != "num":
            print("wrong data type")
            return result
        # 输入csv文件路径
        file_path = input('please input the path of csv data file:')
        if not os.path.exists(file_path):
            print('the file does not exist')
            return result
        else:
            try:
                if data_type == 'num':
                    data = pd.read_csv(file_path, dtype=float)
                    data = data.values[:, 1:]
                    data_dim = data.shape[1]
                else:
                    data = pd.read_csv(file_path, dtype=str)
                    data = data.values[:, 1:]
                    data = np.squeeze(data)
                    if len(data.shape) > 1:
                        raise ValueError('wrong data type in file')
            except Exception as e:
                print(e)
                return result
            # 读取数据成功，并返回
            result['success'] = True
            result['data_type'] = data_type
            result['data'] = data
            result['data_dim'] = data_dim
            return result

    def _input_query_data(self):
        """
        输入要搜索的query data
        :return:
        """
        if self._data_type == 'string':
            query_data = input('please input a string as query data:')
        else:
            # data type=='num'
            query_data = input("please input num list of %d dim(separated by commas ,):" % self._data_dim)
            query_data = query_data.split(",")
            # 当用户输入的数据维度，还没有达到dim维度时，继续输入
            while len(query_data) < self._data_dim:
                temp = input()
                temp = temp.split(",")
                query_data.extend(temp)
            try:
                # 输入的数据query data为字符串，需要进行类型转换
                query_data = [float(num) for num in query_data]
                query_data = np.array(query_data[0:self._data_dim])
            except Exception as e:
                print(e)
                return False, None
        return True, query_data

    @staticmethod
    def _print_neighbors(neighbors):
        """
        打印搜索到的所有neighbors
        :param neighbors:
        :return:
        """
        for neig in neighbors:
            print('neighbors:', neig['object'], '\tdistance: %0.3f' % neig['distance'])

    @staticmethod
    def _print_average_distance_calculating_times(result):
        for res in result:
            print('max_distance: %0.2f, average_cal_dis_times: %0.2f' % (res['max_distance'], res['average_cal_dis_times']))

    @staticmethod
    def _input_a_num(name, dtype, min_value=None):
        """
        从键盘中获取一个数
        :param name: 获取的数据的名称
        :param dtype: 获取的数据的类型
        :param min_value: 获取的数据需要大于的最小值
        :return:
        """
        if not isinstance(name, str):
            raise ValueError('name should be a str')
        if dtype != int and dtype != float:
            raise ValueError('data type should be int or float')

        data = input("please input the %s:" % name)
        try:
            data = dtype(data)
        finally:
            if not isinstance(data, dtype):
                print("%s should be a %s." % (name, str(dtype)))
                return False, data

            if min_value is not None and data <= min_value:
                print("%s should great than %d." % (name, min_value))
                return False, data
            return True, data

