from collections import defaultdict

from .bfs import BFS

from ..node import Node
from ..edge import Edge


class Routing:
    """
    タッチアンドクロス法を用いて経路を決定する
    """
    def __init__(self, graph, module_list, route_pair):
        self._graph = graph
        self._module_list = module_list
        self._route_pair = route_pair
        self._var_node_count = graph.var_node_count
        self._space = 4
        self._invalid_edge = {}

        (max_x, max_y, max_z) = (0, 0, 0)
        for node in self._graph.node_list:
            max_x = max(max_x, node.x)
            max_y = max(max_y, node.y)
            max_z = max(max_z, node.z)

        self._size = (max_x + self._space, max_y + self._space, max_z + self._space)
        self.__create_used_node_array(max_x, max_y, max_z)

        self._grid = [[[0
                        for z in range(0, int(max_z + self._space * 2) + 1)]
                       for y in range(0, int(max_y + self._space * 2) + 1)]
                      for x in range(0, int(max_x + self._space * 2) + 1)]

    def execute(self):
        routes = defaultdict(list)
        # 初期経路
        for index, (src, dst) in enumerate(self._route_pair.items(), start=1):
            route = BFS(src, dst,
                        1,
                        self._grid,
                        self._used_node_array,
                        self._size,
                        self._space,
                        True).search()
            routes[index] = route

        # 経路決定まで引き剥がしをlimitを限度に繰り返す
        update = self.__check()
        count, limit = 0, 100
        while update:
            count += 1
            print("loop: {}".format(count))
            for index, (src, dst) in enumerate(self._route_pair.items(), start=1):
                self.__clear(index, routes)
                route = BFS(src, dst,
                            count,
                            self._grid,
                            self._used_node_array,
                            self._size,
                            self._space).search()
                routes[index] = route
            update = self.__check()
            if count == limit:
                break

        self.__create_route(routes)

    def __clear(self, index, routes):
        """
        indexの経路を引き剥がす

        :param index ネット番号
        :param routes indexをkeyとしたrouteのdict
        """
        for node in routes[index]:
            self._grid[node.x + self._space][node.y + self._space][node.z + self._space] -= 1

        routes[index].clear()

    def __check(self):
        for z in range(0, self._size[2] + self._space):
            for x in range(0, self._size[0] + self._space):
                for y in range(0, self._size[1] + self._space):
                    if self._grid[x][y][z] > 1:
                        return True

        return False

    def __create_route(self, routes):
        for route in routes.values():
            id_, type_ = route[0].id, route[0].type
            node_array = []
            # 始点と終点は既にグラフに追加されているため追加しない
            for node in route[1:len(route) - 1]:
                node = self.__new_node(type_, node.x, node.y, node.z)
                node_array.append(node)

            last_node = None
            node_array.insert(0, route[0])
            node_array.append(route[-1])
            for node in node_array:
                if last_node is not None:
                    self.__new__edge(node, last_node, "edge", id_)
                last_node = node

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

    def __new_node_variable(self):
        self._var_node_count += 1
        return self._var_node_count

    def __new_node(self, type_, x, y, z):
        node = Node(x, y, z, self.__new_node_variable(), type_)
        self._graph.add_node(node)
        return node

    def __new__edge(self, node1, node2, category, id=0):
        edge = Edge(node1, node2, category, id)
        node1.add_edge(edge)
        node2.add_edge(edge)
        self._graph.add_edge(edge)
        return edge
