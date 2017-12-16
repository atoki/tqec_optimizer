import copy
import sys
from collections import defaultdict

from .module_list_factory import ModuleListFactory
from .sequence_triple import SequenceTriple
from .neighborhood_generator import SwapNeighborhoodGenerator, ShiftNeighborhoodGenerator
from .tsp import TSP
from .rip_and_reroute import RipAndReroute
from .tqec_evaluator import TqecEvaluator

from ..graph import Graph
from ..node import Node
from ..edge import Edge
from ..circuit_writer import CircuitWriter

sys.setrecursionlimit(10000)


class Relocation:
    """
    モジュールへの切断と再配置による最適化を行う
    """
    def __init__(self, graph):
        self._graph = graph
        self._module_list = []
        self._joint_pair_list = []
        self._injector_list = defaultdict(list)
        self._var_node_count = 0

        # イジェクター(Pin, Cap)の情報を抜き出す
        for edge in self._graph.edge_list:
            if edge.is_injector():
                self._injector_list[edge.id].append(edge.category)

    def execute(self):
        """
        1.モジュール化と再接続による最適化を行う
        2.Sequence-Tripleを用いた局所探索法による再配置を行う
        """
        graph = self.__reduction(self._graph)
        graph = self.__relocation(graph)
        self.__add_injector(graph)

        return graph

    def __reduction(self, graph):
        """
        最初にモジュール化と再接続による最適化を行う
        """
        module_list, joint_pair_list = ModuleListFactory(graph, "primal").create()
        graph = self.__to_graph(module_list)
        route_pair = TSP(joint_pair_list).search()
        RipAndReroute(graph, module_list, route_pair).search()

        result_graph = graph
        cost, loop_count = TqecEvaluator(None, result_graph, True).evaluate(), 0
        primal_reduction, dual_reduction = True, True
        while primal_reduction or dual_reduction:
            type_ = "primal" if loop_count % 2 == 0 else "dual"
            if type_ == "dual":
                dual_reduction = False
            else:
                primal_reduction = False
            module_list, joint_pair_list = ModuleListFactory(result_graph, type_).create()
            graph = self.__to_graph(module_list)
            route_pair = TSP(joint_pair_list).search()
            RipAndReroute(graph, module_list, route_pair).search()
            current_cost = TqecEvaluator(None, graph, True).evaluate()
            if cost > current_cost:
                if type_ == "dual":
                    dual_reduction = True
                else:
                    primal_reduction = True
                result_graph = graph
                cost = current_cost
            loop_count += 1

        CircuitWriter(graph).write("3-reduction.json")

        return result_graph

    def __relocation(self, graph):
        """
        Sequence-Tripleを用いた局所探索法による再配置を行う
        """
        primal_reduction, dual_reduction = True, True
        loop_count = 0
        while primal_reduction or dual_reduction:
            type_ = "dual" if loop_count % 2 == 0 else "primal"
            if loop_count > 1:
                if type_ == "dual":
                    dual_reduction = False
                else:
                    primal_reduction = False
            reduction = True
            while reduction:
                reduction = False
                module_list, joint_pair_list = ModuleListFactory(graph, type_).create()
                cost = TqecEvaluator(module_list).evaluate()
                place = SequenceTriple(type_, module_list)
                p1, p2, p3 = place.build_permutation()
                swap_permutations_list = SwapNeighborhoodGenerator((p1, p2, p3)).generator()
                shift_permutations_list = ShiftNeighborhoodGenerator((p1, p2, p3)).generator()

                result_module_list = copy.deepcopy(module_list)
                result_joint_pair = copy.deepcopy(joint_pair_list)
                for step, permutations in enumerate(swap_permutations_list + shift_permutations_list):
                    relocation_module = SequenceTriple(type_, permutations[0], permutations).recalculate_coordinate()
                    if self.__is_validate(relocation_module):
                        current_cost = TqecEvaluator(relocation_module).evaluate()
                        if cost > current_cost:
                            reduction = True
                            if type_ == "dual":
                                dual_reduction = True
                            if type_ == "primal":
                                primal_reduction = True
                            cost = current_cost
                            result_module_list = copy.deepcopy(relocation_module)
                            result_joint_pair = copy.deepcopy(joint_pair_list)
                graph = self.__to_graph(result_module_list)
                route_pair = TSP(result_joint_pair).search()
                RipAndReroute(graph, result_module_list, route_pair).search()
                file_name = str(4 + loop_count) + "-relocation.json"
                CircuitWriter(graph).write(file_name)
            loop_count += 1

        return graph

    @staticmethod
    def __is_validate(module_list):
        used_node = {}
        for module_ in module_list:
            for edge in module_.edge_list + module_.cross_edge_list:
                node1, node2 = edge.node1, edge.node2
                if node1 in used_node:
                    if edge.id != used_node[node1]:
                        return False
                if node2 in used_node:
                    if edge.id != used_node[node2]:
                        return False
                if node1 not in used_node:
                    used_node[node1] = edge.id
                if node2 not in used_node:
                    used_node[node2] = edge.id

        return True

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
                new_edge = self.__new__edge(node1, node2, edge.category, edge.id)
                new_edge.set_color(color)
                graph.add_edge(new_edge)
                if edge.node1 not in added_node:
                    graph.add_node(node1)
                    added_node[edge.node1] = node1
                if edge.node2 not in added_node:
                    graph.add_node(node2)
                    added_node[edge.node2] = node2

        return graph

    def __add_injector(self, graph):
        """
        インジェクターの情報を復元する

        :param graph グラフ
        """
        for id_, category_list in self._injector_list.items():
            for category in category_list:
                candidate_edge = graph.edge_list[0]
                for edge in graph.edge_list:
                    if edge.id == id_ and not edge.is_injector():
                        if edge.z > candidate_edge.z:
                            candidate_edge = edge
                        if edge.z == candidate_edge.z and edge.x < candidate_edge.x:
                            candidate_edge = edge
                candidate_edge.set_category(category)

    @staticmethod
    def __new__node(node):
        node = Node(node.x, node.y, node.z, node.id, node.type)

        return node

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

    def __color_route_pair(self, route_pair_list):
        """
        モジュールに色付けをして可視化する
        """
        for key, value in route_pair_list.items():
            id_ = key.id
            color = self.__create_random_color(id_)
            key.set_color(color)
            value.set_color(color)

    @staticmethod
    def __create_random_color(loop_id):
        colors = [0xffdead, 0x808080, 0x191970, 0x00ffff, 0x008000,
                  0x00ff00, 0xffff00, 0x8b0000, 0xff1493, 0x800080]
        return colors[loop_id % 10]

    def debug(self):
        print("--- module list ---")
        for module_ in self._module_list:
            module_.debug()

