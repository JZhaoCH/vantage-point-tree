import numpy as np
import random


class VPTree:
    def __init__(self, data, distance_fun, data_type, tree_ways=2, leaf_capacity=1, selecting_vp_mode='random'):
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
        if selecting_vp_mode != 'random' and selecting_vp_mode != 'max_std':
            raise ValueError('selecting_method should be random or max_std, instead of :', selecting_vp_mode)

        self._childes = []
        self._vantage_point = None
        self._distance_fun = distance_fun
        self._tree_ways = tree_ways
        self._cutoff_values = []
        self._leaf_capacity = leaf_capacity
        self._data_type = data_type
        self._is_leaf = False
        self._leaf_data = None
        self._selecting_vp_mode = selecting_vp_mode
        # build tree 构造树结构
        self.build_tree(data)

    def get_childes(self):
        return self._childes

    def is_leaf(self):
        return self._is_leaf

    def get_leaf_data(self):
        return self._leaf_data

    def get_vantage_point(self):
        return self._vantage_point

    def get_cutoff_values(self):
        return self._cutoff_values

    def get_tree_way(self):
        return self._tree_ways

    def get_leaf_capacity(self):
        return self._leaf_capacity

    def get_selecting_vp_mode(self):
        return self._selecting_vp_mode

    def build_tree(self, data):
        """
        根据data，递归地创建vp tree
        :param data:
        :return:
        """
        # 如果数组为空
        if data is None or len(data) == 0:
            return None

        # 数据比较少，直接放在一个叶子节点中
        if isinstance(data, str):
            self._is_leaf = True
            self._leaf_data = data
            return self
        elif data.shape[0] <= self._leaf_capacity:
            self._is_leaf = True
            self._leaf_data = data
            return self

        # 选择支撑点
        vantage_point, vp_index = self.select_vantage_point(data, self._selecting_vp_mode)
        self._vantage_point = vantage_point

        if self._data_type == 'string' and (isinstance(self._vantage_point, list) or isinstance(self._vantage_point, np.ndarray)):
            self._vantage_point = self._vantage_point[0]

        data = np.delete(data, vp_index, axis=0)

        # 根据每个点到支撑点的距离对数据进行划分
        distances = np.array([self._distance_fun(self._vantage_point, point) for point in data])
        data_splited, cutoff_values = self.split_data_into_multi_ways(data, distances)
        self._cutoff_values = cutoff_values

        # 对划分出来的每一份数据递归创建vp tree
        for child in data_splited:
            self._childes.append(VPTree(child, self._distance_fun, data_type=self._data_type, tree_ways=self._tree_ways,
                                        leaf_capacity=self._leaf_capacity, selecting_vp_mode=self._selecting_vp_mode))

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
            while cutoff_indexes[i] < len(data) and sorted_distance[cutoff_indexes[i]-1] == \
                    sorted_distance[cutoff_indexes[i]]:
                cutoff_indexes[i] += 1
        cutoff_indexes = np.unique(cutoff_indexes)

        for i in range(len(cutoff_indexes)):
            cutoff_val = (sorted_distance[cutoff_indexes[i]-1] +
                          sorted_distance[min(cutoff_indexes[i], len(sorted_distance)-1)])/2
            cutoff_values.append(cutoff_val)

        childes = np.split(sorted_data, cutoff_indexes)
        if len(childes[-1]) == 0:
            childes = np.delete(childes, len(childes)-1)
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
            if node.is_leaf():
                seq_result = self.sequential_search(node.get_leaf_data(), query_point, max_distance)
                result['neighbors'].extend(seq_result['neighbors'])
                result['cal_distance_times'] += seq_result['cal_distance_times']
                continue

            # 如果不是叶子节点
            node_vp = node.get_vantage_point()
            node_cutoff_values = node.get_cutoff_values()
            node_childes = node.get_childes()
            # 首先检查支撑点是否在查询范围内
            dis = self._distance_fun(query_point, node_vp)
            result['cal_distance_times'] += 1
            if dis <= max_distance:
                result['neighbors'].append({'object': node_vp, 'distance': dis})
            # 对该节点的所有孩子进行判断
            for i in range(len(node_cutoff_values)):
                # 根据三角不等式，判断是否要进入某一个分支中进行搜索
                cutoff_val = node_cutoff_values[i]
                if i == 0:
                    if dis - max_distance <= cutoff_val:
                        nodes_to_list.append(node_childes[i])
                    if dis + max_distance > cutoff_val and i+1 < len(node_childes):
                        nodes_to_list.append(node_childes[i+1])
                else:
                    if dis + max_distance > cutoff_val and i+1 < len(node_childes):
                        nodes_to_list.append(node_childes[i + 1])
        return result

    def select_vantage_point(self, data, selecting_mode):
        """
        支撑点选择方法
        :param data: 数据集
        :param selecting_mode: 选择模式, random or max_std
        :return:
        """
        if selecting_mode != 'random' and selecting_mode != 'max_std':
            raise ValueError('selecting_method should be random or max_std, instead of :', selecting_mode)

        if selecting_mode == 'random':
            # data中的数据比较多的情况，选取支撑点
            vp_index = random.randint(0, len(data) - 1)
            vantage_point = data[vp_index]
            return vantage_point, vp_index
        else:
            # 确定候选vp的数量
            candidate_count = min(10, len(data))
            sub_set_count = min(50, len(data)-1)
            # 从数据集中随机采样获得候选vp
            candidate_vp, candidate_vp_index = VPTree.random_sample(data, candidate_count)
            max_std = -1
            vantage_point = None
            vp_index = -1
            for candidate, candidate_ind in zip(candidate_vp, candidate_vp_index):
                # 对于每一个候选vp，从数据集中随机采样获得采样点
                temp_data = np.delete(data, candidate_ind)
                temp_sub_set_data, _ = VPTree.random_sample(temp_data, sub_set_count)
                # 计算每一个采样点与候选vp之间的距离
                distances = [self._distance_fun(candidate, point) for point in temp_sub_set_data]
                # 计算距离的标准差
                std = np.std(distances)
                # 选择标准差最大的候选vp
                if std > max_std:
                    max_std = std
                    vantage_point = candidate
                    vp_index = candidate_ind
            return vantage_point, vp_index

    def get_tree_height(self):
        if self is None:
            return 0
        if self._is_leaf:
            return 1
        childes_height = []
        for child in self._childes:
            childes_height.append(child.get_tree_height())
        height = max(childes_height)+1
        return height

    def get_data_count_of_tree(self):
        """
        获取vp树中存放的元素个数
        :return:
        """
        if self is None:
            return 0
        if self._is_leaf:
            return len(self.get_leaf_data())
        data_count = []
        for child in self._childes:
            data_count.append(child.get_data_count_of_tree())
        # +1表示支撑点
        count = sum(data_count)+1
        return count

    @staticmethod
    def random_sample(population, k):
        """
        从数据集中随机采样不重复的k个元素
        :param population:
        :param k:
        :return:
        """
        if not 0 <= k <= len(population):
            raise ValueError("Sample larger than population")
        sample_index = np.arange(len(population))
        sample_index = np.random.choice(sample_index, k, replace=False)
        sample = population[sample_index]
        return sample, sample_index
