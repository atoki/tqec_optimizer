from .best_first_search import BestFirstSearch


class LocalSearch:
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

        count = 0
        while True:
            improved = self.__opt2()
            if not improved:
                break
            count += 1

        route = {}
        for index in range(0, size - 1):
            if self._invalidate_pair[self._route[index]] == self._route[index + 1]:
                continue
            route[self._route[index]] = self._route[index + 1]
        if self._invalidate_pair[self._route[size - 1]] != self._route[0]:
            route[self._route[size - 1]] = self._route[0]

        return route

    def __opt2(self):
        size = len(self._route)
        cost_diff_best = 0.0
        i_best, j_best = None, None

        for i in range(0, size - 2):
            for j in range(i + 2, size):
                if i == 0 and j == size - 1:
                    continue

                if self._invalidate_pair[self._route[i]] == self._route[int((i + 1) % size)] \
                        or self._invalidate_pair[self._route[j]] == self._route[int((j + 1) % size)]:
                    continue

                cost_diff = self.__calculate_exchange_cost(i, j)

                if cost_diff < cost_diff_best:
                    cost_diff_best = cost_diff
                    i_best, j_best = i, j

        if cost_diff_best < 0.0:
            self.__apply_exchange(i_best, j_best)
            return True
        else:
            return False

    def __calculate_exchange_cost(self, i, j):
        size = len(self._route)
        a, b = i, int((i + 1) % size)
        c, d = j, int((j + 1) % size)

        cost_before = self._dist_table[(self._route[a], self._route[b])] \
                        + self._dist_table[(self._route[c], self._route[d])]
        cost_after = self._dist_table[(self._route[a], self._route[c])] \
                        + self._dist_table[(self._route[b], self._route[d])]

        return cost_after - cost_before

    def __apply_exchange(self, i, j):
        tmp = self._route[i + 1: j + 1]
        tmp.reverse()
        self._route[i + 1: j + 1] = tmp

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

