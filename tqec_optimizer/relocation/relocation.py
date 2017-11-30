import math

from .module import Module
from .module_list_factory import ModuleListFactory
from .sequence_triple import SequenceTriple
from .tsp import TSP
from .rip_and_reroute import RipAndReroute

from ..graph import Graph
from ..node import Node
from ..edge import Edge


class Relocation:
    """
    モジュールへの切断と再配置による最適化を行う
    """
    def __init__(self, graph):
        self._graph = graph
        self._module_list = []
        self._joint_pair_list = []
        self._var_node_count = 0

    def execute(self):
        """
        1.グラフ情報を用いてモジュールを作成
        2.モジュール単位で再配置を行う
        3.再配置したモジュールの再接続を行う
        4.コストが減少しなくなるまで 2.3 を繰り返す
        """
        module_list, joint_pair_list = ModuleListFactory(self._graph, "dual").create()
        route_pair = TSP(joint_pair_list).search()
        # place = SequenceTriple("dual", module_list, (6, 6, 20))
        # place.build_permutation()
        # module_list = place.recalculate_coordinate()
        graph = self.__to_graph(module_list)
        RipAndReroute(graph, module_list, route_pair).search()

        module_list, joint_pair_list = ModuleListFactory(graph, "primal").create()
        route_pair = TSP(joint_pair_list).search()
        # place = SequenceTriple("primal", module_list, (6, 6, 20))
        # place.build_permutation()
        # module_list = place.recalculate_coordinate()
        graph = self.__to_graph(module_list)
        RipAndReroute(graph, module_list, route_pair).search()

        return graph

    def __to_graph(self, module_list):
        """
        モジュールを構成するノードと辺の情報をもとにグラフクラスを作成する

        :param module_list グラフ化するモジュールのリスト
        """
        graph = Graph()
        graph.set_loop_count(self._graph.loop_count)
        added_node = {}
        for module_ in module_list:
            for edge in module_.edge_list + module_.cross_edge_list:
                color = edge.color
                node1 = added_node[edge.node1] if edge.node1 in added_node else edge.node1
                node2 = added_node[edge.node2] if edge.node2 in added_node else edge.node2
                edge = self.__new__edge(node1, node2, edge.category, edge.id)
                edge.set_color(color)
                graph.add_edge(edge)
                if edge.node1 not in added_node:
                    graph.add_node(node1)
                    added_node[edge.node1] = node1
                if edge.node2 not in added_node:
                    graph.add_node(node2)
                    added_node[edge.node2] = node2

        return graph

    @staticmethod
    def __new__edge(node1, node2, category, id_=0):
        edge = Edge(node1, node2, category, id_)

        return edge

    def __color_module(self, module_list):
        """
        モジュールに色付けをして可視化する
        """
        for module_ in module_list:
            id_ = module_.id
            color = self.__create_random_color(id_)
            for edge in module_.edge_list + module_.cross_edge_list:
                edge.set_color(color)
                edge.node1.set_color(color)
                edge.node2.set_color(color)

    def __color_graph(self, graph):
        """
        モジュールに色付けをして可視化する
        """
        for edge in graph.edge_list:
            id_ = edge.id
            color = self.__create_random_color(id_)
            edge.set_color(color)
            edge.node1.set_color(color)
            edge.node2.set_color(color)

    def __color_cross_edge(self, module_list):
        """
        モジュールに色付けをして可視化する
        """
        for module_ in module_list:
            for edge in module_.cross_edge_list:
                id_ = edge.id
                color = self.__create_random_color(id_)
                edge.set_color(color)
                edge.node1.set_color(color)
                edge.node2.set_color(color)

    def __color_jont(self, joint_pair_list):
        """
        モジュールに色付けをして可視化する
        """
        for joint_pair in joint_pair_list:
            id_ = joint_pair[0].id
            color = self.__create_random_color(id_)
            joint_pair[0].set_color(color)
            joint_pair[1].set_color(color)

    @staticmethod
    def __create_random_color(loop_id):
        colors = [0xffdead, 0x808080, 0x191970, 0x00ffff, 0x008000,
                  0x00ff00, 0xffff00, 0x8b0000, 0xff1493, 0x800080]
        return colors[loop_id % 10]

    def debug(self):
        print("--- module list ---")
        for module_ in self._module_list:
            module_.debug()

