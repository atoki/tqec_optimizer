import random
import math
import time
from collections import defaultdict

from .module_factory import ModuleFactory
from .sequence_triple import SequenceTriple
from .tsp import TSP
from .routing import Routing
from .tqec_evaluator import TqecEvaluator

from ..position import Position
from ..graph import Graph
from ..node import Node
from ..edge import Edge
from ..circuit_writer import CircuitWriter


class Relocation:
    """
    モジュールへの切断と再配置による最適化を行う
    """
    def __init__(self, type_, loop_list, graph):
        self._type = type_
        self._loop_list = loop_list
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
        Sequence-Tripleを用いたSAによる再配置を行う
        """
        graph = self.__sa_relocation(self._type)
        CircuitWriter(graph).write("5-relocation.json")
        self.__add_injector(graph)

        return graph

    def __sa_relocation(self, type_):
        """
        Simulated Annealingによる再配置を行う

        :param type_ primal or dual モジュールを作る基準
        """
        initial_t = 100
        final_t = 0.1
        cool_rate = 0.9
        limit = 100

        module_list, joint_pair_list = [], []
        for loop in self._loop_list:
            if loop.type != type_:
                continue
            module_ = ModuleFactory(type_, loop).create()
            module_list.append(module_)

        new_pos = Position(0, 0, 0)
        for module_ in module_list:
            module_.set_position(Position(new_pos.x, new_pos.y, new_pos.z), True)
            new_pos.incz(module_.depth)

        graph = self.__to_graph(module_list)
        CircuitWriter(graph).write("3-module.json")

        current_cost = TqecEvaluator(module_list).evaluate()
        place = SequenceTriple(module_list)
        place.build_permutation()
        t = initial_t
        start = time.time()
        # TODO: モジュール配置に無効条件を通過するバグの修正
        while t > final_t:
            if t % 10 < 1.0:
                print(t)
            for n in range(limit):
                place.create_neighborhood()
                module_list = place.recalculate_coordinate()

                if not self.__is_validate(module_list):
                    place.recover()
                    continue

                new_cost = TqecEvaluator(module_list).evaluate()

                if self.__should_change(new_cost - current_cost, t):
                    current_cost = new_cost
                    place.apply()
                else:
                    place.recover()
            t *= cool_rate

        elapsed_time = time.time() - start
        print("処理時間: {}".format(elapsed_time))

        if not self.__is_validate(module_list):
            print("False")
            for m in module_list:
                m.debug()
            print("")
            for m in module_list:
                print("--")
                for node in m.frame_node_list + m.cross_node_list:
                    node.debug()

        self.__color_cross_edge(module_list)
        graph = self.__to_graph(module_list)
        CircuitWriter(graph).write("4-relocation.json")
        route_pair = TSP(graph, module_list).search()
        Routing(graph, module_list, route_pair).execute()

        return graph

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
            for node in module_.cross_node_list:
                if node in used_node:
                    if node.id != used_node[node]:
                        return False
                if node not in used_node:
                    used_node[node] = node.id

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
            for edge in module_.frame_edge_list + module_.cross_edge_list:
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
