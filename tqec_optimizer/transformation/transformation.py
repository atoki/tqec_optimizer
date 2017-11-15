import math
import heapq

from .loop import Loop

from ..graph import Edge


class Transformation:
    def __init__(self, graph):
        self._graph = graph
        self._var_node_count = graph.var_node_count
        self._loop_list = []

    def execute(self):
        self.__delete_loop(0)
        self.__generate_loop()
        # self.__color_loop()

        # reduction = True
        # while reduction:
        #     for loop in self._loop_list:
        #         reduction = self.__rule1(loop)
        #         if reduction:
        #             break

        for loop in self._loop_list:
            if self.__rule2(loop):
                break

    def __generate_loop(self):
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

            if len(loop.edge_list) > 0:
                self._loop_list.append(loop)

        # 交差情報の更新
        for loop in self._loop_list:
            for edge in loop.edge_list:
                for cross_edge in edge.cross_edge_list:
                    loop.add_cross(cross_edge.id)

    def __rule1(self, loop):
        """
        変形規則1
        """
        if len(loop.cross_list) > 1 or len(loop.cross_list) == 0 \
                or len(loop.injector_list) > 1 or len(loop.injector_list) == 0:
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
        print("rule2")
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
            del_edge.debug()
            self.__delete_edge(del_edge)

        # 2つのループを結合する
        self.__connect_loop(cross_loop_list[0], cross_loop_list[1])

        # ループを1つにするためにノードをつなげる
        # self.__connect_node(cross_loop_list[0], node1, node4)
        # self.__connect_node(cross_loop_list[0], node2, node3)

        # for loop in self._loop_list:
        #     loop.debug()

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
        :param start ノード
        :param end ノード
        """
        d = [math.inf for i in self._graph.node_list]
        pren = [-1 for i in self._graph.node_list]

        # main loop
        queue = []
        heapq.heappush(queue, (0, start))
        d[start.id] = 0
        dx = [2, 0, -2, 0, 0, 0]
        dy = [0, 2, 0, -2, 0, 0]
        dz = [0, 0, 0, 0, 2, -2]
        while len(queue) != 0:
            current_node_cost, current_node = heapq.heappop(queue)
            if d[current_node.id] < current_node_cost:
                continue
            for i in range(6):
                nx = current_node.x + dx[i]
                ny = current_node.y + dy[i]
                nz = current_node.z + dz[i]
                if 0 <= nx < self._graph.width and 0 <= ny < self._graph.height \
                        and 0 <= nz < self._graph.depth and exit flag:
                    next_node = self._graph.node(nx, ny, nz)
                    if d[next_node.id] > current_node_cost + 1:
                        d[next_node.id] = current_node_cost + 1
                        heapq.heappush(queue, (current_node_cost + 1, next_node))
                        pren[next_node.id] = current_node.id

        # set path
        path = [-1 for i in self._graph.node_list]
        preid = pren[end.id]
        path[preid] = net_id
        while preid != start.id:
            preid = pren[preid]
            path[preid] = net_id
        path[start.id] = net_id
        path[end.id] = net_id


        edge = Edge(node1, node2, "edge", loop.id)
        loop.add_edge(edge)
        self._graph.add_edge(edge)

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
                non_loop_node_index.append(self._graph.node_list.index(edge.node1))
                non_loop_node_index.append(self._graph.node_list.index(edge.node2))

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
            id = loop.id
            color = self.__generate_random_color(id)
            for edge in loop.edge_list:
                edge.set_color(color)
                edge.node1.set_color(color)
                edge.node2.set_color(color)

    def __loop(self, loop_id):
        for loop in self._loop_list:
            if loop.id == loop_id:
                return loop

    @staticmethod
    def __generate_random_color(loop_id):
        colors = [0xffdead, 0x808080, 0x191970, 0x0000ff, 0x00ffff, 0x008000,
                  0x00ff00, 0xffff00, 0x8b0000, 0xff1493, 0x800080]
        return colors[loop_id % 11]
