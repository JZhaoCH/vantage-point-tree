from vp_tree import VPTree
from utils import euclidean_distance, edit_distance
import os
import pandas as pd
import numpy as np


class ConsoleApp:
    def __init__(self):
        self._data_type = None
        self._data_dim = 0
        self._vp_tree = None
        pass

    def main(self):
        self._print_tips()
        while True:
            selection = input('\nplease input a integer to select an operation:')
            try:
                selection = int(selection)
            except Exception as e:
                pass
            if not isinstance(selection, int) or selection < 0 or selection > 4:
                print("wrong input: ", selection)
                continue
            if selection == 0:
                print('exit')
                break
            elif selection == 1:
                result = self._get_data_from_console()
                if result['success'] is False:
                    continue
                else:
                    self._data_type = result['data_type']
                    self._data_dim = result['data_dim']
                    if self._data_type == 'string':
                        self._vp_tree = VPTree(result['data'], edit_distance)
                        print('create vp tree successfully')
                    else:
                        self._vp_tree = VPTree(result['data'], euclidean_distance)
                        print('create vp tree successfully')

            elif selection == 2:
                result = self._get_data_from_file()
                if result['success'] is False:
                    continue
                else:
                    self._data_type = result['data_type']
                    self._data_dim = result['data_dim']
                    if self._data_type == 'string':
                        self._vp_tree = VPTree(result['data'], edit_distance)
                        print('create vp tree successfully')
                    else:
                        self._vp_tree = VPTree(result['data'], euclidean_distance)
                        print('create vp tree successfully')

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
            else:
                print("\n"*30)
                self._print_tips()

    def _print_tips(self):
        print("-----------------------------------------------------\n"
              "type 1 to input data from keyboard and create a VP tree\n"
              "type 2 to input data from file and create a VP tree\n"
              "type 3 to search in VP tree\n"
              "type 4 to clean the console\n"
              "type 0 to exit\n"
              "-----------------------------------------------------\n")

    def _get_data_from_console(self):
        result = dict()
        result['success'] = False

        data_dim = 0
        data_count = input("please input the count of data:")
        try:
            data_count = int(data_count)
        finally:
            if not isinstance(data_count, int) or data_count < 0:
                print("count of data should be a positive integer")
                return result

        data_type = input("please input the type of data(string or num):")
        if data_type != "string" and data_type != "num":
            print("wrong data type")
            return result

        if data_type == 'num':
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
            for i in range(data_count):
                line = input()
                line = line.split(" ")
                while len(line) < data_dim:
                    temp = input()
                    temp = temp.split(" ")
                    line.extend(temp)
                try:
                    line = [float(line_num) for line_num in line]
                except Exception as e:
                    print(e)
                    return result
                data.append(line[0: data_dim])
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

    def _get_data_from_file(self):
        result = dict()
        result['success'] = False
        data_type = input("please input the type of data(string or num):")

        if data_type != "string" and data_type != "num":
            print("wrong data type")
            return result

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

            result['success'] = True
            result['data_type'] = data_type
            result['data'] = np.squeeze(data)
            result['data_dim'] = data_dim
            return result

    def _input_query_data(self):
        if self._data_type == 'string':
            query_data = input('please input a string as query data:')
        else:
            query_data = input()
            query_data = query_data.split("please input num list of %d dim:" % self._data_dim)
            while len(query_data) < self._data_dim:
                temp = input()
                temp = temp.split(" ")
                query_data.extend(temp)
            try:
                query_data = [float(num) for num in query_data]
            except Exception as e:
                print(e)
                return None
        return query_data

    def _input_max_distance(self):
        max_distance = input("please input the max distance for searching:")
        try:
            max_distance = float(max_distance)
        finally:
            if not isinstance(max_distance, float) or max_distance < 0:
                print("length of data should be a positive float")
                return None
        return max_distance
