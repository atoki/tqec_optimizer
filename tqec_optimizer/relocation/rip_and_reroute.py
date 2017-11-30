from .best_first_search import BestFirstSearch

from ..edge import Edge
from ..node import Node


class RipAndReroute:
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
        self.__create_invalid_edge_array()

    def search(self):
        for src, dst in self._route_pair.items():
            bfs = BestFirstSearch(src, dst, self._used_node_array, self._invalid_edge, self._size, self._space)
            route = bfs.search()
            self.__create_route(src, dst, route)

    def __create_route(self, src, dst, route):
        """
        start(node)とend(node)を接続するrouteを元に
        経路をに必要なノードと辺を作成する

        :param src 接続元ノード
        :param dst 接続先ノード
        :param route 経路に必要なノードの配列
        """
        # routeが始点と終点のみで構成されている場合
        if len(route) == 2:
            edge = self.__new__edge(src, dst, "edge", src.id)
            return

        node_array = []
        # 始点と終点は既にグラフに追加されているため追加しない
        for node in route[1:len(route) - 1]:
            node = self.__new_node(src.type, node.x, node.y, node.z)
            node_array.append(node)

        node_array.insert(0, src)
        node_array.append(dst)
        last_node = None
        for node in node_array:
            if last_node is not None:
                edge = self.__new__edge(node, last_node, "edge", src.id)
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

    def __create_invalid_edge_array(self):
        for edge in self._graph.edge_list:
            self._invalid_edge[edge.node1] = edge.node2
            self._invalid_edge[edge.node2] = edge.node1

    def __new_node_variable(self):
        self._var_node_count += 1
        return self._var_node_count

    def __new_node(self, type_, x, y, z):
        node = Node(x, y, z, self.__new_node_variable(), type_)
        self._used_node_array[x + self._space][y + self._space][z + self._space] = True
        self._graph.add_node(node)

        return node

    def __new__edge(self, node1, node2, category, id=0):
        edge = Edge(node1, node2, category, id)
        node1.add_edge(edge)
        node2.add_edge(edge)
        self._graph.add_edge(edge)

        return edge

