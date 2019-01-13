from vp_tree import VPTree
from utils import euclidean_distance, edit_distance
import os
import pandas as pd
import numpy as np


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
            if not isinstance(selection, int) or selection < 0 or selection > 4:
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
                    query_data = self._input_query_data()
                    max_distance = self._input_max_distance()
                    if query_data is not None:
                        self._vp_tree.search(query_data, max_distance)
                    else:
                        print('wrong in input query data')
            # 清空console
            else:
                print("\n"*30)
                self._print_tips()

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
              "type 4 to clean the console\n"
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
        data_count = input("please input the count of data:")
        try:
            data_count = int(data_count)
        finally:
            if not isinstance(data_count, int) or data_count < 0:
                print("count of data should be a positive integer")
                return result
        # 输入数据的类型
        data_type = input("please input the type of data(string or num):")
        if data_type != "string" and data_type != "num":
            print("wrong data type")
            return result

        if data_type == 'num':
            # 如果数据类型是num，则需要输入数据的维度
            data_dim = input("please input the dimension of the point:")
            try:
                data_dim = int(data_dim)
            finally:
                if not isinstance(data_dim, int) or data_dim < 0:
                    print("dimension should be a positive integer")
                    return result

        print("please input the data, each line is a data object.")
        print("num type example (dimension==3): 1 2 3")
        if data_type == 'num':
            data = []
            # 从键盘中读取data_count个数据点
            for i in range(data_count):
                line = input()
                line = line.split(" ")
                # 当一行读取到的数据点的维度没有达到data_dim的时候，继续输入
                while len(line) < data_dim:
                    temp = input()
                    temp = temp.split(" ")
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
        result['data'] = np.squeeze(data)
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
                else:
                    data = pd.read_csv(file_path)
                data = data.values[:, 1:]
                data_dim = data.shape[1]
            except Exception as e:
                print(e)
                return result
            # 读取数据成功，并返回
            result['success'] = True
            result['data_type'] = data_type
            result['data'] = np.squeeze(data)
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
            query_data = input()
            query_data = query_data.split("please input num list of %d dim:" % self._data_dim)
            # 当用户输入的数据维度，还没有达到dim维度时，继续输入
            while len(query_data) < self._data_dim:
                temp = input()
                temp = temp.split(" ")
                query_data.extend(temp)
            try:
                # 输入的数据query data为字符串，需要进行类型转换
                query_data = [float(num) for num in query_data]
                query_data = query_data[0:self._data_dim]
            except Exception as e:
                print(e)
                return None
        return query_data

    @staticmethod
    def _input_max_distance():
        """
        输入query data的最大距离
        :return:
        """
        max_distance = input("please input the max distance for searching:")
        try:
            # 输入的max_distance是字符串需要进行类型转换
            max_distance = float(max_distance)
        finally:
            if not isinstance(max_distance, float) or max_distance < 0:
                print("length of data should be a positive float")
                return None
        return max_distance
