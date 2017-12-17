import random
import math

from .best_first_search import BestFirstSearch


class SA:
    def __init__(self, graph, module_list, route_list, invalidate_pair):
        self._graph = graph
        self._module_list = module_list
        self._route = route_list
        self._invalidate_pair = invalidate_pair
        self._dist_table = {}
        self._space = 2
        self._invalid_edge = {}

        (max_x, max_y, max_z) = (0, 0, 0)
        for node in self._graph.node_list:
            max_x = max(max_x, node.x)
            max_y = max(max_y, node.y)
            max_z = max(max_z, node.z)

        self._size = (max_x + self._space, max_y + self._space, max_z + self._space)
        self.__create_used_node_array(max_x, max_y, max_z)
        self.__create_invalid_edge_array()
        self.__create_dist_table()

    def execute(self):
        size = len(self._route)
        if size == 2:
            route = {self._route[0]: self._route[1]}
            return route

        initial_t = 100
        final_t = 0.01
        cool_rate = 0.97
        limit = 100

        current_cost = self.__total_cost()
        t = initial_t
        while True:
            for n in range(limit):
                index1 = random.randint(0, size - 1)
                index2 = random.randint(0, size - 1)

                if not self.__swap(index1, index2):
                    continue

                new_cost = self.__total_cost()

                if self.__should_change(new_cost - current_cost, t):
                    current_cost = new_cost
                else:
                    self.__swap(index1, index2)
            t *= cool_rate
            if t < final_t:
                break

        # ネット割当のdictを作成
        route = {}
        for index in range(0, size - 1):
            if self._invalidate_pair[self._route[index]] == self._route[index + 1]:
                continue
            route[self._route[index]] = self._route[index + 1]
        if self._invalidate_pair[self._route[size - 1]] != self._route[0]:
            route[self._route[size - 1]] = self._route[0]

        return route

    @staticmethod
    def __should_change(delta, t):
        if delta <= 0:
            return 1
        if random.random() < math.exp(- delta / t):
            return 1
        return 0

    def __swap(self, index1, index2):
        if self._invalidate_pair[self._route[index1 - 1]] == self._route[index1] \
                or self._invalidate_pair[self._route[index2 - 1]] == self._route[index2]:
            return False

        tmp = self._route[index1: index2]
        tmp.reverse()
        self._route[index1: index2] = tmp

        return True

    def __total_cost(self):
        size = len(self._route)
        cost = 0.0
        for index in range(0, size - 1):
            cost += self._dist_table[(self._route[index], self._route[index + 1])]
        cost += self._dist_table[(self._route[0], self._route[size - 1])]

        return cost

    def __create_dist_table(self):
        size = len(self._route)
        for i in range(0, size):
            for j in range(i, size):
                if i == j:
                    continue
                else:
                    route = BestFirstSearch(self._route[i],
                                            self._route[j],
                                            self._used_node_array,
                                            self._invalid_edge,
                                            self._size,
                                            self._space).search()
                    dist = (len(route) - 1) * 2.0
                    self._dist_table[(self._route[i], self._route[j])] = dist
                    self._dist_table[(self._route[j], self._route[i])] = dist

    def __create_invalid_edge_array(self):
        for edge in self._graph.edge_list:
            self._invalid_edge[edge.node1] = edge.node2
            self._invalid_edge[edge.node2] = edge.node1

    def __create_used_node_array(self, max_x, max_y, max_z):
        """
        経路として利用できないノードリストを作成する

        :param max_x　X軸方向の最大サイズ
        :param max_y　Y軸方向の最大サイズ
        :param max_z　Z軸方向の最大サイズ
        """
        self._used_node_array = [[[False
                                   for z in range(0, int(max_z + self._space * 2) + 1)]
                                  for y in range(0, int(max_y + self._space * 2) + 1)]
                                 for x in range(0, int(max_x + self._space * 2) + 1)]

        for node in self._graph.node_list:
            self._used_node_array[node.x + self._space][node.y + self._space][node.z + self._space] = True

        for module_ in self._module_list:
            min_x, max_x = module_.inner_pos.x + 1, module_.inner_pos.x + module_.inner_width
            min_y, max_y = module_.inner_pos.y + 1, module_.inner_pos.y + module_.inner_height
            min_z, max_z = module_.inner_pos.z + 1, module_.inner_pos.z + module_.inner_depth
            for x in range(min_x, max_x):
                for y in range(min_y, max_y):
                    for z in range(min_z, max_z):
                        self._used_node_array[x + self._space][y + self._space][z + self._space] = True

