import random
import math
import time
import copy
from collections import defaultdict

from .module import Module
from .module_factory import ModuleFactory
from .sequence_triple import SequenceTriple
from .allocation import Allocation
from .tsp import TSP
from .routing import Routing
from .tqec_evaluator import TqecEvaluator

from ..vector3d import Vector3D
from ..graph import Graph
from ..node import Node, Joint
from ..edge import Edge, CrossEdge
from ..circuit_writer import CircuitWriter


class Relocation:
    """
    モジュールへの切断と再配置による最適化を行う
    """
    def __init__(self, type_, loop_list, graph):
        self._type = type_
        self._loop_list = loop_list
        self._graph = graph
        self._cross_id_set = {}
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
        # create module list
        module_list = [ModuleFactory(self._type, loop, self._injector_list[loop.id]).create()
                       for loop in self._loop_list if loop.type == self._type]
        self._cross_id_set = {module_.id: set(module_.cross_id_list) for module_ in module_list}

        # 各モジュールの配置決定
        result = self.__sa_relocation(module_list)

        # 各辺に対するidの割当を決定
        Allocation(result, self._cross_id_set).execute()
        print("allocation is completed")
        graph = self.__to_graph(result)

        # 各辺の接合部の接続割当を決定
        route_pair = TSP(graph, result).search()
        print("TSP is completed")

        # 各ネットの結ぶ経路の決定
        Routing(graph, result, route_pair).execute()
        print("routing is completed")

        # injectorを復元
        self.__add_injector(graph)

        return graph

    def __sa_relocation(self, module_list):
        """
        Simulated Annealingによる再配置を行う
        :param module_list Moduleの配列
        """
        initial_t = 100
        final_t = 0.01
        cool_rate = 0.99
        limit = 100

        self.__create_initial_placement(module_list)
        current_cost = TqecEvaluator(module_list).evaluate()
        place = SequenceTriple(module_list)
        place.build_permutation()
        t = initial_t
        start = time.time()
        result = module_list
        while t > final_t:
            for n in range(limit):
                place.create_neighborhood()
                candidate = place.recalculate_coordinate()

                if not self.__is_validate(candidate, self._cross_id_set):
                    place.recover()
                    continue

                new_cost = TqecEvaluator(candidate).evaluate()

                if self.__should_change(new_cost - current_cost, t):
                    current_cost = new_cost
                    place.apply()
                    if t < 1.0:
                        result = self.__deep_copy_module_list(candidate)
                else:
                    place.recover()
            t *= cool_rate

        elapsed_time = time.time() - start
        print("処理時間: {}".format(elapsed_time))
        print("relocation is completed")

        return result

    @staticmethod
    def __create_initial_placement(module_list):
        """
         初期配置を生成する
         :param module_list Moduleの配列
         """
        # adjust position and create cross id set map
        new_pos = Vector3D(0, 0, 0)
        for module_ in module_list:
            # adjust position
            module_.set_position(Vector3D(new_pos.x, new_pos.y, new_pos.z), True)
            new_pos.incz(module_.depth)

    @staticmethod
    def __should_change(delta, t):
        if delta <= 0:
            return 1
        if random.random() < math.exp(- delta / t):
            return 1
        return 0

    @staticmethod
    def __is_validate(module_list, cross_id_set):
        edge_map = {}
        connect_edge = defaultdict(list)
        for module_ in module_list:
            for joint_pair in module_.joint_pair_list:
                joint1, joint2 = joint_pair[0], joint_pair[1]
                edge = joint_pair[2]

                if joint1 in edge_map and joint2 in edge_map:
                    connect_edge[edge_map[joint1]].extend(connect_edge[edge_map[joint2]])
                    connect_edge[edge_map[joint1]].append(edge)
                    del_edge = edge_map[joint2]

                    for edge in connect_edge[edge_map[joint2]]:
                        node1, node2 = edge.node1, edge.node2
                        edge_map[node1] = edge_map[joint1]
                        edge_map[node2] = edge_map[joint1]

                    del connect_edge[del_edge]

                elif joint1 in edge_map:
                    edge_map[joint2] = edge_map[joint1]
                    connect_edge[edge_map[joint1]].append(edge)

                elif joint2 in edge_map:
                    edge_map[joint1] = edge_map[joint2]
                    connect_edge[edge_map[joint2]].append(edge)

                else:
                    edge_map[joint1] = edge
                    edge_map[joint2] = edge
                    connect_edge[edge].append(edge)

        id_set = copy.deepcopy(cross_id_set)
        for key_edge, edge_list in sorted(connect_edge.items(), key=lambda x: len(x[1]), reverse=True):
            if len(edge_list) == 1:
                break
            result = id_set[edge_list[0].module_id]
            for edge in edge_list:
                tmp = id_set[edge.module_id]
                result = result & tmp

            if len(result) == 0:
                return False

            del_num = result.pop()
            for edge in edge_list:
                id_set[edge.module_id].remove(del_num)

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
            for edge in module_.edge_list:
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
            edge_list = []
            for edge in graph.edge_list:
                if id_ == edge.id:
                    edge_list.append(edge)
            candidate_edge = graph.edge_list[0]
            for category in category_list:
                for edge in edge_list:
                    if not edge.is_injector():
                        if edge.z > candidate_edge.z:
                            candidate_edge = edge
                        if edge.z == candidate_edge.z and edge.x < candidate_edge.x:
                            candidate_edge = edge
                        if edge.z == candidate_edge.z \
                                and edge.x == candidate_edge.x \
                                and edge.y > candidate_edge.y:
                            candidate_edge = edge
                candidate_edge.set_category(category)

    @staticmethod
    def __deep_copy_module_list(module_list):
        result = []
        for m in module_list:
            module_ = Module(m.id)

            # set frame edge
            added_node = {}
            for edge in m.frame_edge_list:
                node1 = added_node[edge.node1] if edge.node1 in added_node \
                    else Node(edge.node1.x, edge.node1.y, edge.node1.z, edge.node1.id, edge.node1.type)
                node2 = added_node[edge.node2] if edge.node2 in added_node \
                    else Node(edge.node2.x, edge.node2.y, edge.node2.z, edge.node2.id, edge.node2.type)
                frame_edge = Edge(node1, node2, edge.category, m.id)
                module_.add_frame_edge(frame_edge)
                if edge.node1 not in added_node:
                    added_node[edge.node1] = node1
                if edge.node2 not in added_node:
                    added_node[edge.node2] = node2

            # set cross edge
            for joint_pair in m.joint_pair_list:
                joint1 = Joint(joint_pair[0].x, joint_pair[0].y, joint_pair[0].z, joint_pair[0].id, joint_pair[0].type)
                joint2 = Joint(joint_pair[1].x, joint_pair[1].y, joint_pair[1].z, joint_pair[1].id, joint_pair[1].type)
                cross_edge = CrossEdge(joint1, joint2, "edge", joint_pair[2].id, joint_pair[2].module_id)
                module_.add_cross_node(joint1)
                module_.add_cross_node(joint2)
                module_.add_cross_edge(cross_edge)
                module_.add_joint_pair((joint1, joint2, cross_edge))

            # set id set
            for id_ in m.cross_id_list:
                m.add_cross_id(id_)

            # set size and pos
            module_.set_inner_size(m.inner_width, m.inner_height, m.inner_depth)
            module_.set_size(m.width, m.height, m.depth)
            module_.set_inner_position(Vector3D(m.inner_pos.x, m.inner_pos.y, m.inner_pos.z))
            module_.set_position(Vector3D(m.pos.x, m.pos.y, m.pos.z))

            result.append(module_)

        return result

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

