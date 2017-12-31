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

        module_list = []
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
        p1, p2, p3 = place.build_permutation()
        t = initial_t
        init = True
        start = time.time()
        while t > final_t:
            if t % 10 < 1.0:
                print(t)
            for n in range(limit):
                np1, np2, np3 = self.__create_neighborhood(module_list, p1, p2, p3, init)
                if np1 is None:
                    continue

                new_cost = TqecEvaluator(module_list).evaluate()

                if init and self.__is_validate(module_list):
                    p1, p2, p3 = np1, np2, np3
                    t = initial_t
                    init = False

                if self.__should_change(new_cost - current_cost, t):
                    current_cost = new_cost
                    p1, p2, p3 = np1, np2, np3
                else:
                    module_list = SequenceTriple(p1, (p1, p2, p3)).recalculate_coordinate()
            t *= cool_rate

        elapsed_time = time.time() - start
        print("処理時間: {}".format(elapsed_time))

        graph = self.__to_graph(module_list)
        CircuitWriter(graph).write("4-relocation.json")
        route_pair = TSP(graph, module_list).search()
        Routing(graph, module_list, route_pair).execute()

        return graph

    def __create_neighborhood(self, module_list, p1, p2, p3, init):
        """
        SA用の近傍を生成する
        1. swap近傍
        2. shift近傍
        3. rotate近傍
        以上の3つを等確率で一つ採用
        :param module_list モジュールの集合
        :param p1 順列1
        :param p2 順列2
        :param p3 順列3
        :param init 初期配置が決定していればTrue, そうでなければFalse
        """
        np1, np2, np3 = p1[:], p2[:], p3[:]

        strategy = random.randint(1, 3)
        # swap
        index, rotate = 0, None
        if strategy == 1:
            self.__swap(np1, np2, np3)
        elif strategy == 2:
            self.__shift(np1, np2, np3)
        else:
            index, rotate = self.__rotate(np1)

        module_list = SequenceTriple(np1, (np1, np2, np3)).recalculate_coordinate()

        if init or self.__is_validate(module_list):
            return np1, np2, np3

        module_list = SequenceTriple(p1, (p1, p2, p3)).recalculate_coordinate()
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
    def __rotate(p1):
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
