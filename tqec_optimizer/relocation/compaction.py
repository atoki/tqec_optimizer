import math

from .module_list_factory import ModuleListFactory
from .tsp import TSP
from .rip_and_reroute import RipAndReroute

from ..position import Position
from ..edge import Edge
from ..graph import Graph


class Compaction:
    def __init__(self, graph):
        self._graph = graph

    def execute(self):
        graph = self.__primal_compaction(self._graph)
        graph = self.__dual_compaction(graph)

        return graph

    def __primal_compaction(self, graph):
        module_list, joint_pair_list = ModuleListFactory(graph, "primal").create()
        module_list.sort(key=lambda m: (m.pos.x, m.pos.z))

        x, width, pre_x = 0, 0, -math.inf
        for module_ in module_list:
            if pre_x == module_.pos.x:
                x -= width
                module_.set_position(Position(x, module_.pos.y, module_.pos.z), True)
                x += width
                if module_.width > width:
                    x += module_.width - width
                    width = module_.width
            else:
                pre_x = module_.pos.x
                if x <= module_.pos.x:
                    module_.set_position(Position(x, module_.pos.y, module_.pos.z), True)
                    width = module_.width
                    x += width
                else:
                    x = max(x, module_.pos.x + module_.width)

        graph = self.__to_graph(module_list)
        route_pair = TSP(graph, module_list, joint_pair_list).search()
        RipAndReroute(graph, module_list, route_pair).search()

        return graph

    def __dual_compaction(self, graph):
        module_list, joint_pair_list = ModuleListFactory(graph, "dual").create()
        module_list.sort(key=lambda m: (m.pos.z, m.pos.x))

        z, depth, pre_z = 0, 0, -math.inf
        for module_ in module_list:
            if pre_z == module_.pos.z:
                z -= depth
                module_.set_position(Position(module_.pos.x, module_.pos.y, z), True)
                z += depth
                if module_.depth > depth:
                    z += module_.depth - depth
                    depth = module_.depth
            else:
                pre_z = module_.pos.z
                if z <= module_.pos.z:
                    module_.set_position(Position(module_.pos.x, module_.pos.y, z), True)
                    depth = module_.depth
                    z += depth
                else:
                    z = max(z, module_.pos.z + module_.depth)

        graph = self.__to_graph(module_list)
        route_pair = TSP(graph, module_list, joint_pair_list).search()
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

    @staticmethod
    def __new__edge(node1, node2, category, id_=0):
        edge = Edge(node1, node2, category, id_)

        return edge
