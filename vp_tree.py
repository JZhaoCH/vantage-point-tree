import numpy as np
import random


class VPTree:
    def __init__(self, data, distance_fun, tree_ways=2, leaf_capacity=1):
        """
        构造函数
        :param data:
        :param distance_fun:
        """
        if data is None or len(data) == 0:
            raise ValueError('Data can not be empty')
        if not isinstance(tree_ways, int) or tree_ways < 2:
            raise ValueError('leaf_data should be a integer and must bigger than 1')
        if not isinstance(leaf_capacity, int) or leaf_capacity < 1:
            raise ValueError('leaf_capacity should be a positive integer')

        self.childes = []
        self.vantage_point = None
        self._distance_fun = distance_fun
        self._tree_ways = tree_ways
        self.cutoff_values = []
        self._leaf_capacity = leaf_capacity
        self.is_leaf = False
        self.leaf_data = None

        # build tree 构造树结构
        self.build_tree(data, distance_fun)

    def build_tree(self, data, distance_fun):
        """
        :param data:
        :param distance_fun:
        :return:
        """
        # 如果数组为空
        if data is None or len(data) == 0:
            return None

        # 数据比较少，当成叶子节点
        if len(data) <= self._leaf_capacity:
            self.is_leaf = True
            self.leaf_data = data
            return self

        # data中的数据比较多的情况，选取支撑点，并进行数据的划分
        vp_index = random.randint(0, len(data)-1)
        self.vantage_point = data[vp_index]
        data = np.delete(data, vp_index)

        distances = np.array([self._distance_fun(self.vantage_point, point) for point in data])
        data_splited, cutoff_values = self.split_data_into_multi_ways(data, distances)
        self.cutoff_values = cutoff_values

        for child in data_splited:
            self.childes.append(VPTree(child, distance_fun, self._tree_ways))

    def split_data_into_multi_ways(self, data, distances):
        sorted_ind = np.argsort(distances)
        sorted_distance = distances[sorted_ind]
        sorted_data = data[sorted_ind]

        partition_size = round(len(data)/self._tree_ways)
        cutoff_indexes = [i*partition_size for i in range(1, self._tree_ways)]
        cutoff_values = []

        for i in range(len(cutoff_indexes)):
            while cutoff_indexes[i] < len(data) and data[cutoff_indexes[i]-1] == data[cutoff_indexes[i]]:
                cutoff_indexes[i] += 1
            if cutoff_indexes[i] < len(data):
                cutoff_val = (sorted_distance[cutoff_indexes[i]-1]+sorted_distance[cutoff_indexes[i]])/2
            else:
                cutoff_val = sorted_distance[cutoff_indexes[i]-1]
            cutoff_values.append(cutoff_val)

        childes = np.split(sorted_data, cutoff_indexes)
        for child in childes:
            if len(child) == 0:
                childes.remove(child)
        return childes, cutoff_values

    def sequential_search(self, data, query_point, max_distance):
        result = []
        if data is None or len(data) == 0:
            return result

        for point in data:
            dis = self._distance_fun(point, query_point)
            if dis <= max_distance:
                result.append({'object': point, 'distance': dis})
        return result

    def search(self, query_point, max_distance):
        result = []
        nodes_to_list = [self]

        while len(nodes_to_list) > 0:
            node = nodes_to_list.pop(0)

            if node is None:
                continue

            # 如果是叶子节点，则搜索
            if node.is_leaf is True:
                result.extend(self.sequential_search(node.leaf_data, query_point, max_distance))
                continue

            # 如果不是叶子节点
            dis = self._distance_fun(query_point, node.vantage_point)
            if dis <= max_distance:
                result.append({'object': node.vantage_point, 'distance': dis})
            for i in range(len(node.cutoff_values)):
                cutoff_val = node.cutoff_values[i]
                if i == 0:
                    if dis - max_distance <= cutoff_val and i < len(node.childes):
                        nodes_to_list.append(node.childes[i])
                    if dis + max_distance > cutoff_val and i+1 < len(node.childes):
                        nodes_to_list.append(node.childes[i+1])
                else:
                    if dis + max_distance > cutoff_val:
                        nodes_to_list.append(node.childes[i + 1])
        return result
