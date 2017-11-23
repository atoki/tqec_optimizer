import math

from .module import Module
from .sequence_triple import SequenceTriple

from ..graph import *


class Relocation:
    """
    モジュールへの切断と再配置による最適化を行う
    """
    def __init__(self, graph):
        self._graph = graph
        self._primal_module_list = []
        self._dual_module_list = []
        self._var_node_count = 0

    def execute(self):
        """
        1.グラフ情報を用いてモジュールを作成
        2.モジュール単位で再配置を行う
        3.再配置したモジュールの再接続を行う
        4.コストが減少しなくなるまで 2.3 を繰り返す
        """
        self.__create_module()
        self.__color_module()

        # primal defect
        # place = SequenceTriple("primal", self._primal_module_list, (6, 6, 20))
        # place.build_permutation()
        # module_list = place.recalculate_coordinate()

        # dual defect
        # place = SequenceTriple("dual", self._dual_module_list, (6, 6, 20))
        # place.build_permutation()
        # module_list = place.recalculate_coordinate()
        #
        # graph = self.__module_to_graph(module_list)
        #
        graph = self.__module_to_graph(self._dual_module_list)
        return graph

    def __create_module(self):
        """
        モジュールを生成する
        """
        for loop_id in range(1, self._graph.loop_count + 1):
            module_ = Module(loop_id)
            edge_pair_list = []

            # ループを構成している辺をモジュールに追加する
            for edge in self._graph.edge_list:
                if edge.id == loop_id:
                    module_.add_edge(edge)
                    if len(edge.cross_edge_list) > 0 and edge.cross_edge_list[0] in self._graph.edge_list:
                        edge_pair_list.append((edge, edge.cross_edge_list[0]))

            if len(module_.edge_list) == 0:
                continue

            # ループを構成している辺と交差している辺をモジュールに追加する
            for edge_pair in edge_pair_list:
                for cross_edge in self.__create_cross_edge_list(module_, edge_pair[0], edge_pair[1]):
                    joint1 = self.__new_joint(cross_edge.node1)
                    joint2 = self.__new_joint(cross_edge.node2)
                    new_cross_edge = self.__new__edge(joint1, joint2, cross_edge.category, cross_edge.id)
                    module_.add_cross_edge(new_cross_edge)

            type_ = module_.edge_list[0].type

            # モジュールを構成する全ての辺から座標とサイズ情報を更新する
            module_.update()

            # モジュールの中身があればリストに追加
            if type_ == "primal":
                self._primal_module_list.append(module_)
            else:
                self._dual_module_list.append(module_)

    def __create_cross_edge_list(self, module_, border1, cross_edge):
        cross_edge_list = []
        (min_, max_) = (math.inf, -math.inf)

        if border1.dir == 'X':
            for edge in module_.edge_list:
                if border1.x == edge.x and border1 != edge:
                    if cross_edge.dir == 'Y':
                        max_ = max(border1.y, edge.y)
                        min_ = min(border1.y, edge.y)
                    elif cross_edge.dir == 'Z':
                        max_ = max(border1.z, edge.z)
                        min_ = min(border1.z, edge.z)
                    break
        elif border1.dir == 'Y':
            for edge in module_.edge_list:
                if border1.y == edge.y and border1 != edge:
                    if cross_edge.dir == 'X':
                        max_ = max(border1.x, edge.x)
                        min_ = min(border1.x, edge.x)
                    elif cross_edge.dir == 'Z':
                        max_ = max(border1.z, edge.z)
                        min_ = min(border1.z, edge.z)
                    break
        else:
            for edge in module_.edge_list:
                if border1.z == edge.z and border1 != edge:
                    if cross_edge.dir == 'X':
                        max_ = max(border1.x, edge.x)
                        min_ = min(border1.x, edge.x)
                    elif cross_edge.dir == 'Y':
                        max_ = max(border1.y, edge.y)
                        min_ = min(border1.y, edge.y)
                    break

        if min_ == math.inf or max_ == math.inf:
            return cross_edge_list

        if cross_edge.dir == 'X':
            y = cross_edge.y
            z = cross_edge.z
            for x in range(int(min_), int(max_) + 1, 2):
                cross_edge_list.append(self.__edge(x, y, z))

        if cross_edge.dir == 'Y':
            x = cross_edge.x
            z = cross_edge.z
            for y in range(int(min_), int(max_) + 1, 2):
                cross_edge_list.append(self.__edge(x, y, z))

        if cross_edge.dir == 'Z':
            x = cross_edge.x
            y = cross_edge.y
            for z in range(int(min_), int(max_) + 1, 2):
                cross_edge_list.append(self.__edge(x, y, z))

        return cross_edge_list

    def __expand_edge(self):
        pass

    @staticmethod
    def __to_graph(module_list):
        """
        モジュールを構成するノードと辺の情報をもとにグラフクラスを作成する

        :param module_list グラフ化するモジュールのリスト
        """
        graph = Graph()
        for module_ in module_list:
            for edge in module_.edge_list + module_.cross_edge_list:
                graph.add_edge(edge)
                graph.add_node(edge.node1)
                graph.add_node(edge.node2)

        return graph

    def __edge(self, x, y, z):
        for edge in self._graph.edge_list:
            if edge.x == x and edge.y == y and edge.z == z:
                return edge

    def __new_node_variable(self):
        self._var_node_count += 1
        return self._var_node_count

    def __new_joint(self, node):
        joint = Node(node.x, node.y, node.z, self.__new_node_variable(), node.type)

        return joint

    def __new__edge(self, node1, node2, category, id_=0):
        edge = Edge(node1, node2, category, id_)
        node1.add_edge(edge)
        node2.add_edge(edge)

        return edge

    def __color_module(self):
        """
        モジュールに色付けをして可視化する
        """
        for module_ in self._dual_module_list:
            id_ = module_.id
            color = self.__create_random_color(id_)
            for edge in module_.edge_list + module_.cross_edge_list:
                edge.set_color(color)
                edge.node1.set_color(color)
                edge.node2.set_color(color)

    @staticmethod
    def __create_random_color(loop_id):
        colors = [0xffdead, 0x808080, 0x191970, 0x00ffff, 0x008000,
                  0x00ff00, 0xffff00, 0x8b0000, 0xff1493, 0x800080]
        return colors[loop_id % 10]

    def debug(self):
        print("--- primal module list ---")
        for module_ in self._primal_module_list:
            module_.debug()
        print("--- dual module list ---")
        for module_ in self._dual_module_list:
            module_.debug()
