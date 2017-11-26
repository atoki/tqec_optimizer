from .loop import Loop
from .best_first_search import BestFirstSearch

from ..graph import Node
from ..graph import Edge


class Transformation:
    """
    非トポロジー的な変形を行うクラス
    """
    def __init__(self, graph):
        """
        コンストラクタ

        :param graph Graph
        """
        self._graph = graph
        self._var_node_count = graph.var_node_count
        self._loop_list = []
        self._space = 4

        (max_x, max_y, max_z) = (0, 0, 0)
        for node in self._graph.node_list:
            max_x = max(max_x, node.x)
            max_y = max(max_y, node.y)
            max_z = max(max_z, node.z)

        self._size = (max_x + self._space, max_y + self._space, max_z + self._space)

        self._used_node_array = [[[False
                                   for z in range(0, int(max_z + self._space * 2) + 1)]
                                  for y in range(0, int(max_y + self._space * 2) + 1)]
                                 for x in range(0, int(max_x + self._space * 2) + 1)]

        for node in self._graph.node_list:
            self._used_node_array[node.x + self._space][node.y + self._space][node.z + self._space] = True

    def execute(self):
        # 閉じていない辺を削除
        self.__delete_loop(0)
        self.__create_loop()
        # self.__color_loop()

        reduction = True
        no = 1
        print("-- rule2 --")
        while reduction:
            print("-step{}".format(no))
            for loop in self._loop_list:
                reduction = self.__rule2(loop)
                if reduction:
                    no += 1
                    break

        reduction = True
        no = 1
        print("-- rule1 --")
        while reduction:
            print("-step{}".format(no))
            for loop in self._loop_list:
                reduction = self.__rule1(loop)
                if reduction:
                    no += 1
                    break

        # self.__color_loop()

    def __create_loop(self):
        """
        ループを生成する
        """
        # 辺の追加
        for loop_id in range(1, self._graph.loop_count + 1):
            loop = Loop(loop_id)

            # ループを構成している辺を追加する
            for edge in self._graph.edge_list:
                if edge.id == loop_id:
                    if edge.is_injector():
                        loop.add_injector(edge)
                    loop.add_edge(edge)
                    # 交差情報の更新
                    for cross_edge in edge.cross_edge_list:
                        loop.add_cross(cross_edge.id)

            if len(loop.edge_list) > 0:
                self._loop_list.append(loop)

    def __rule1(self, loop):
        """
        変形規則1
        """
        if len(loop.cross_list) != 1 or len(loop.injector_list) != 1:
            return False

        cross_loop = self.__loop(loop.cross_list[0])
        cross_loop.shift_injector(loop.injector_list[0].category)
        cross_loop.remove_cross(loop.id)
        self.__delete_loop(loop.id)

        return True

    def __rule2(self, loop):
        """
        変形規則2
        """
        if len(loop.cross_list) != 2 or len(loop.injector_list) != 0:
            return False

        cross_edge_list = []
        for edge in loop.edge_list:
            for cross_edge in edge.cross_edge_list:
                cross_edge_list.append(cross_edge)

        node1 = cross_edge_list[0].node1
        node2 = cross_edge_list[0].node2
        node3 = cross_edge_list[1].node1
        node4 = cross_edge_list[1].node2

        # ループを削除する
        cross_loop_list = []
        for cross_loop_id in loop.cross_list:
            cross_loop = self.__loop(cross_loop_id)
            cross_loop.remove_cross(loop.id)
            cross_loop_list.append(cross_loop)
        self.__delete_loop(loop.id)

        # ループに交差した辺を全て削除する
        for del_edge in cross_edge_list:
            self.__delete_edge(del_edge)

        # 2つのループを結合する
        self.__connect_loop(cross_loop_list[0], cross_loop_list[1])

        # self.__color_node()

        # ループを1つにするためにノードをつなげる
        self.__connect_node(cross_loop_list[0], node1, node3)
        self.__connect_node(cross_loop_list[0], node2, node4)

        return True

    def __rule3(self, loop):
        pass

    def __connect_loop(self, loop1, loop2):
        """
        loop1がloop2を吸収する形で2つのループを結合する

        :param loop1 吸収する側のループ
        :param loop2 吸収される側のループ
        """
        for edge in loop2.edge_list:
            loop1.add_edge(edge)
            edge.set_id(loop1.id)

        for cross_id in loop2.cross_list:
            loop1.add_cross(cross_id)

        for injector in loop2.injector_list:
            loop1.add_injector(injector)

        self.__delete_loop(loop2.id, True)

    def __connect_node(self, loop, start, end):
        """
        start(node)とend(node)を接続する
        接続するために追加されたノード, 辺はloopに追加する

        :param loop 接続のために生成されたノードと辺を追加するループ
        :param start 接続元ノード
        :param end 接続先ノード
        """
        route = BestFirstSearch(start, end, self._used_node_array, self._size, self._space).search()
        self.__create_route(loop, start, end, route)

    def __create_route(self, loop, start, end, route):
        """
        start(node)とend(node)を接続するrouteを元に
        経路をに必要なノードと辺を作成する

        :param loop 接続のために生成されたノードと辺を追加するループ
        :param start 接続元ノード
        :param end 接続先ノード
        :param route 経路に必要なノードの配列
        """
        # routeが始点と終点のみで構成されている場合
        if len(route) == 2:
            edge = self.__new__edge(start, end, "edge", loop.id)
            loop.add_edge(edge)
            return

        node_array = []
        # 始点と終点は既にグラフに追加されているため追加しない
        for node in route[1:len(route)-1]:
            node = self.__new_node(start.type, node.x, node.y, node.z)
            node_array.append(node)

        node_array.insert(0, start)
        node_array.append(end)
        last_node = None
        for node in node_array:
            if last_node is not None:
                edge = self.__new__edge(node, last_node, "edge", loop.id)
                loop.add_edge(edge)
            last_node = node

    def __delete_edge(self, del_edge):
        """
        指定された辺をグラフから削除する

        :param del_edge 削除する辺
        """
        del_edge_index = -1
        for no, edge in enumerate(self._graph.edge_list):
            if del_edge == edge:
                del_edge_index = no

        if del_edge_index > -1:
            del self._graph.edge_list[del_edge_index]

    def __delete_loop(self, loop_id, only_loop=False):
        """
        指定されたループ番号のループを削除する
        only_loopのときグラフ上の情報は消さずにループ情報のみ削除する

        :param loop_id 削除するループ番号
        :param only_loop グラフ情報を残す場合はTrue, 全て消す場合は引数を省略
        """
        non_loop_edge_index = []
        non_loop_node_index = []
        for no, edge in enumerate(self._graph.edge_list):
            if edge.id == loop_id:
                non_loop_edge_index.append(no)
                (node1, node2) = (edge.node1, edge.node2)
                non_loop_node_index.append(self._graph.node_list.index(node1))
                non_loop_node_index.append(self._graph.node_list.index(node2))
                if not only_loop:
                    self._used_node_array[node1.x + self._space][node1.y + self._space][node1.z + self._space] = False
                    self._used_node_array[node2.x + self._space][node2.y + self._space][node2.z + self._space] = False

        non_loop_edge_index.reverse()
        # 重複した要素を取り除く
        non_loop_node_index = list(set(non_loop_node_index))
        non_loop_node_index.sort()
        non_loop_node_index.reverse()

        if not only_loop:
            # delete edge
            for index in non_loop_edge_index:
                del self._graph.edge_list[index]

            # delete node
            for index in non_loop_node_index:
                del self._graph.node_list[index]

        # delete loop
        if loop_id > 0:
            loop_index = self._loop_list.index(self.__loop(loop_id))
            del self._loop_list[loop_index]

    def __new_node_variable(self):
        self._var_node_count += 1
        return self._var_node_count

    def __color_loop(self):
        """
        ループに色付けをして可視化する
        """
        for loop in self._loop_list:
            id_ = loop.id
            color = self.__generate_random_color(id_)
            for edge in loop.edge_list:
                edge.set_color(color)
                edge.node1.set_color(color)
                edge.node2.set_color(color)

    def __loop(self, loop_id):
        for loop in self._loop_list:
            if loop.id == loop_id:
                return loop

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

    @staticmethod
    def __generate_random_color(loop_id):
        colors = [0xffdead, 0x808080, 0x191970, 0x0000ff, 0x00ffff, 0x008000,
                  0x00ff00, 0xffff00, 0x8b0000, 0xff1493, 0x800080]
        return colors[loop_id % 11]
