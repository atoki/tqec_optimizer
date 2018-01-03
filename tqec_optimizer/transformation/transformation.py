from .loop import Loop

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

        # 閉じていない辺を削除
        self.__delete_loop(0)
        self.__create_loop()

    def execute(self):
        reduction = True
        no = 1
        while reduction:
            for loop in self._loop_list:
                reduction = self.__rule3(loop)
                if reduction:
                    no += 1
                    break

        reduction = True
        no = 1
        while reduction:
            for loop in self._loop_list:
                reduction = self.__rule2(loop)
                if reduction:
                    no += 1
                    break

        reduction = True
        no = 1
        while reduction:
            for loop in self._loop_list:
                reduction = self.__rule1(loop)
                if reduction:
                    no += 1
                    break

        print("non topological deforming is completed")
        return self._loop_list

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
                loop.update()
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

        # ループを削除する
        cross_loop_list = []
        delete_loop_id = loop.id
        for cross_loop_id in loop.cross_list:
            cross_loop = self.__loop(cross_loop_id)
            cross_loop.remove_cross(delete_loop_id)
            cross_loop_list.append(cross_loop)
        self.__delete_loop(delete_loop_id)

        # ループに交差した辺を全て削除する
        for del_edge in cross_edge_list:
            self.__delete_edge(del_edge)

        # 2つのループを結合する
        self.__connect_loop(cross_loop_list[0], cross_loop_list[1])

        return True

    def __rule3(self, loop):
        """
        変形規則3
        """
        if len(loop.cross_list) < 3 or len(loop.injector_list) != 0:
            return False

        """
        loop1がloop2, loop3, loop4...と交差していると仮定
        1. loop1に交差してinjectorを含まないloop2を見つける
        2. loop2に交差したloopsをloop3, loop4...と公差させる
        3. loop1, loop2を削除
        """
        # loop1に交差してinjectorを含まないloop2を見つける
        cross_loop_list = []
        delete_loop = None
        for cross_loop_id in loop.cross_list:
            cross_loop = self.__loop(cross_loop_id)
            cross_loop_list.append(cross_loop)
            if len(cross_loop.injector_list) == 0:
                delete_loop = cross_loop

        # loop2が見つからなかった
        if delete_loop is None:
            return False

        # loop1と公差しているloopからloop1の公差情報を削除
        for cross_loop in cross_loop_list:
            cross_loop.remove_cross(loop.id)

        # loop2に交差したshift_loopsをloop3, loop4...と公差させる
        for shift_id in delete_loop.cross_list:
            if shift_id == loop.id:
                continue
            shift_loop = self.__loop(shift_id)
            shift_loop.remove_cross(delete_loop.id)
            for cross_loop in cross_loop_list:
                if cross_loop.id == delete_loop.id:
                    continue
                cross_loop.add_cross(shift_id)
                shift_loop.add_cross(cross_loop.id)

        # loop1, loop2を削除
        self.__delete_loop(loop.id)
        self.__delete_loop(delete_loop.id)

        return True

    def __connect_loop(self, loop1, loop2):
        """
        loop1がloop2を吸収する形で2つのループを結合する

        :param loop1 吸収する側のループ
        :param loop2 吸収される側のループ
        """
        for edge in loop2.edge_list:
            edge.set_id(loop1.id)
            loop1.add_edge(edge)

        for cross_id in loop2.cross_list:
            # loop1にloop2が交差していたloop idを追加する
            loop1.add_cross(cross_id)
            # loop2に交差していたloopのloop2.idをloop1.idに変更する
            loop = self.__loop(cross_id)
            loop.remove_cross(loop2.id)
            loop.add_cross(loop1.id)

        for injector in loop2.injector_list:
            loop1.add_injector(injector)

        self.__delete_loop(loop2.id, True)

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
