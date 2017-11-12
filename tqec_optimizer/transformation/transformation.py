from .loop import Loop


class Transformation:
    def __init__(self, graph):
        self._graph = graph
        self._loop_list = []

    def execute(self):
        self.__delete_loop(0)
        self.__generate_loop()
        # self.__color_loop()

        reduction = True
        while reduction:
            for loop in self._loop_list:
                reduction = self.__rule1(loop)
                if reduction:
                    break

    def __delete_loop(self, loop_id):
        """
        指定されたループ番号のループを削除する

        :param loop_id 削除するループ番号
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
        pass

    def __rule3(self, loop):
        pass

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
