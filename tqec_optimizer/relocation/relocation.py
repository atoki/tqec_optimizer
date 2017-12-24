import copy
import random
import math
import sys
from collections import defaultdict

from .module_list_factory import ModuleListFactory
from .sequence_triple import SequenceTriple
from .neighborhood_generator import SwapNeighborhoodGenerator, ShiftNeighborhoodGenerator
from .tsp import TSP
from .rip_and_reroute import RipAndReroute
from .tqec_evaluator import TqecEvaluator
from .compaction import Compaction

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
        2.回路が内空白
        3.Sequence-Tripleを用いた局所探索法による再配置を行う
        """
        # reduction
        graph = self.__reduction(self._graph)
        point = TqecEvaluator(None, graph, True).evaluate()
        print("reduction cost: {}".format(point))
        CircuitWriter(graph).write("3-reduction.json")

        # compaction
        graph = Compaction(graph).execute()
        point = TqecEvaluator(None, graph, True).evaluate()
        print("compaction cost: {}".format(point))
        CircuitWriter(graph).write("4-compaction.json")

        # reduction
        graph = self.__sa_relocation("primal", graph)
        point = TqecEvaluator(None, graph, True).evaluate()
        print("relocation cost: {}".format(point))
        CircuitWriter(graph).write("5-relocation.json")

        self.__add_injector(graph)

        return graph

    def __reduction(self, graph):
        """
        最初にモジュール化と再接続による最適化を行う
        """
        module_list, joint_pair_list = ModuleListFactory(graph, "primal").create()
        graph = self.__to_graph(module_list)
        route_pair = TSP(graph, module_list, joint_pair_list).search()
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
            route_pair = TSP(graph, module_list, joint_pair_list).search()
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
                route_pair = TSP(graph, result_module_list, result_joint_pair).search()
                RipAndReroute(graph, result_module_list, route_pair).search()
                file_name = str(4 + loop_count) + "-relocation.json"
                CircuitWriter(graph).write(file_name)
            loop_count += 1

        return graph

    def __sa_relocation(self, type_, graph):
        initial_t = 100
        final_t = 0.01
        cool_rate = 0.99
        limit = 100

        module_list, joint_pair_list = ModuleListFactory(graph, type_).create()
        current_cost = TqecEvaluator(module_list).evaluate()
        place = SequenceTriple(type_, module_list)
        p1, p2, p3 = place.build_permutation()
        t = initial_t
        init = True
        while t > final_t:
            for n in range(limit):
                np1, np2, np3 = self.__create_neighborhood(type_, module_list, p1, p2, p3, init)
                if np1 is None:
                    continue

                new_cost = TqecEvaluator(module_list).evaluate()

                if init and self.__is_validate(module_list):
                    init = False

                if self.__should_change(new_cost - current_cost, t):
                    current_cost = new_cost
                    p1, p2, p3 = np1, np2, np3

                else:
                    module_list = SequenceTriple(type_, p1, (p1, p2, p3)).recalculate_coordinate()
            t *= cool_rate

        graph = self.__to_graph(module_list)
        route_pair = TSP(graph, module_list, joint_pair_list).search()
        RipAndReroute(graph, module_list, route_pair).search()

        return graph

    def __create_neighborhood(self, type_, module_list, p1, p2, p3, init):
        np1, np2, np3 = p1[:], p2[:], p3[:]

        strategy = random.randint(1, 3)
        # swap
        index, rotate = 0, None
        if strategy == 1:
            self.__swap(np1, np2, np3)
        elif strategy == 2:
            self.__shift(np1, np2, np3)
        else:
            index, rotate = self.__rotate(np1, np2, np3)

        module_list = SequenceTriple(type_, np1, (np1, np2, np3)).recalculate_coordinate()

        if init or self.__is_validate(module_list):
            return np1, np2, np3

        module_list = SequenceTriple(type_, p1, (p1, p2, p3)).recalculate_coordinate()
        if rotate is not None:
            p1[index].rotate(rotate)
            p1[index].rotate(rotate)
            p1[index].rotate(rotate)

        return None, None, None

    @staticmethod
    def __swap(p1, p2, p3):
        size = len(p1)
        s1 = random.randint(0, size - 1)
        s2 = random.randint(0, size - 1)

        module1, module2 = p1[s1], p1[s2]
        p1_index1, p1_index2 = p1.index(module1), p1.index(module2)
        p2_index1, p2_index2 = p2.index(module1), p2.index(module2)
        p3_index1, p3_index2 = p3.index(module1), p3.index(module2)

        # permutation swap
        p1[p1_index1], p1[p1_index2] = p1[p1_index2], p1[p1_index1]
        p2[p2_index1], p2[p2_index2] = p2[p2_index2], p2[p2_index1]
        p3[p3_index1], p3[p3_index2] = p3[p3_index2], p3[p3_index1]

    @staticmethod
    def __shift(p1, p2, p3):
        size = len(p1)
        index = random.randint(0, size - 1)
        shift_size1 = random.randint(0, size - 1)
        shift_size2 = random.randint(0, size - 1)
        pair = random.randint(1, 3)

        module_ = p1[index]
        if pair == 1:
            p1_index, p2_index = p1.index(module_), p2.index(module_)
            p1_module, p2_module = p1.pop(p1_index), p2.pop(p2_index)
            p1.insert(p1_index + shift_size1, p1_module)
            p2.insert(p2_index + shift_size2, p2_module)
        elif pair == 2:
            p1_index, p3_index = p1.index(module_), p3.index(module_)
            p1_module, p3_module = p1.pop(p1_index), p3.pop(p3_index)
            p1.insert(p1_index + shift_size1, p1_module)
            p3.insert(p3_index + shift_size2, p3_module)
        else:
            p2_index, p3_index = p2.index(module_), p3.index(module_)
            p2_module, p3_module = p2.pop(p2_index), p3.pop(p3_index)
            p2.insert(p2_index + shift_size1, p2_module)
            p3.insert(p3_index + shift_size2, p3_module)

    @staticmethod
    def __rotate(p1, p2, p3):
        size = len(p1)
        index = random.randint(0, size - 1)
        axis = random.randint(1, 3)
        rotate_module = p1[index]

        if axis == 1:
            if rotate_module.rotate('X'):
                return index, 'X'
        elif axis == 2:
            if rotate_module.rotate('Y'):
                return index, 'Y'
        else:
            if rotate_module.rotate('Z'):
                return index, 'Z'

        return index, None

    @staticmethod
    def __should_change(delta, t):
        if delta <= 0:
            return 1
        if random.random() < math.exp(- delta / t):
            return 1
        return 0

    @staticmethod
    def __is_validate(module_list):
        used_node = {}
        for module_ in module_list:
            for edge in module_.cross_edge_list:
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
