import numpy as np
import random


class VPTree:
    def __init__(self, data, distance_fun, data_type, tree_ways=2, leaf_capacity=1):
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
        if data_type != 'string' and data_type != 'num':
            raise ValueError('data type should be string or num')

        self.childes = []
        self.vantage_point = None
        self._distance_fun = distance_fun
        self._tree_ways = tree_ways
        self.cutoff_values = []
        self._leaf_capacity = leaf_capacity
        self.data_type = data_type
        self.is_leaf = False
        self.leaf_data = None
        # build tree 构造树结构
        self.build_tree(data)

    def build_tree(self, data):
        """
        根据data，递归地创建vp tree
        :param data:
        :param distance_fun:
        :return:
        """
        # 如果数组为空
        if data is None or len(data) == 0:
            return None

        # 数据比较少，直接放在一个叶子节点中
        if len(data) <= self._leaf_capacity:
            self.is_leaf = True
            self.leaf_data = data
            return self

        # data中的数据比较多的情况，选取支撑点
        vp_index = random.randint(0, len(data)-1)
        self.vantage_point = data[vp_index]

        if self.data_type == 'string' and not isinstance(self.vantage_point, str):
            self.vantage_point = self.vantage_point[0]
        data = np.delete(data, vp_index, axis=0)

        # 根据每个点到支撑点的距离对数据进行划分
        distances = np.array([self._distance_fun(self.vantage_point, point) for point in data])
        data_splited, cutoff_values = self.split_data_into_multi_ways(data, distances)
        self.cutoff_values = cutoff_values

        # 对划分出来的每一份数据递归创建vp tree
        for child in data_splited:
            self.childes.append(VPTree(child, self._distance_fun, self.data_type, self._tree_ways))

    def split_data_into_multi_ways(self, data, distances):
        """
        根据每个点到支撑点的距离，对数据划分成self._tree_way份
        :param data: 数据点
        :param distances: data中的每个点到支撑点的距离
        :return:
        """
        # 先根据距离，对数据点进行排序
        sorted_ind = np.argsort(distances)
        sorted_distance = distances[sorted_ind]
        sorted_data = data[sorted_ind]

        # 根据_tree_ways将数据划分成多份
        partition_size = round(len(data)/self._tree_ways)
        cutoff_indexes = [i*partition_size for i in range(1, self._tree_ways)]

        # cutoff_values为不同划分之间的距离划分值
        cutoff_values = []

        # 检查相邻划分中，前一个划分的前面的数据点 是否与后一个划分的后面的数据点相同
        # 如果相同，将后一个划分的前面的数据点并入前一个划分中
        for i in range(len(cutoff_indexes)):
            while cutoff_indexes[i] < len(data) and sorted_distance[cutoff_indexes[i]-1] == sorted_distance[cutoff_indexes[i]]:
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
        """
        对data中的数据进行顺序搜索
        :param data: list数据，多个数据点
        :param query_point: 查询数据
        :param max_distance: 与查询数据之间的最大距离
        :return:
        """
        result = dict()
        result['neighbors'] = []
        cal_distance_times = 0
        if data is None or len(data) == 0:
            return result
        # 按顺序比较data中的每一个点到query_point的距离
        for point in data:
            dis = self._distance_fun(point, query_point)
            cal_distance_times += 1
            if dis <= max_distance:
                result['neighbors'].append({'object': point, 'distance': dis})

        result['cal_distance_times'] = cal_distance_times
        return result

    def search(self, query_point, max_distance):
        """
        范围搜索
        :param query_point: 查询数据
        :param max_distance: 与查询数据之间的最大距离
        :return:
        """
        result = dict()
        result['neighbors'] = []
        result['cal_distance_times'] = 0
        nodes_to_list = [self]

        while len(nodes_to_list) > 0:
            node = nodes_to_list.pop(0)

            if node is None:
                continue

            # 如果是叶子节点，则进行顺序搜索
            if node.is_leaf is True:
                seq_result = self.sequential_search(node.leaf_data, query_point, max_distance)
                result['neighbors'].extend(seq_result['neighbors'])
                result['cal_distance_times'] += seq_result['cal_distance_times']
                continue

            # 如果不是叶子节点
            # 首先检查支撑点是否在查询范围内
            dis = self._distance_fun(query_point, node.vantage_point)
            result['cal_distance_times'] += 1
            if dis <= max_distance:
                result['neighbors'].append({'object': node.vantage_point, 'distance': dis})
            # 对该节点的所有孩子进行判断
            for i in range(len(node.cutoff_values)):
                # 根据三角不等式，判断是否要加入某一个分支中进行搜索
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
