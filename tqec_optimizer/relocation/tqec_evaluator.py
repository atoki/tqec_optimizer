import math

from collections import defaultdict


class TqecEvaluator:
    def __init__(self, module_list, graph=None, is_graph=False):
        self._module_list = module_list
        self._graph = graph
        self._is_graph = is_graph
        self._alpha = 0.1
        self._beta = 1.0

    def evaluate(self):
        point = 0
        if self._is_graph:
            point += self.__evaluate_graph()

            return point
        else:
            node_list = []
            edge_map = defaultdict(list)
            for module_ in self._module_list:
                for edge in module_.edge_list:
                    node_list.append(edge.node1)
                    node_list.append(edge.node2)
                for edge in module_.cross_edge_list:
                    edge_map[edge.id].append(edge)

            for id_, edge_list in edge_map.items():
                point += self.__evaluate_wiring_distance(edge_list)

            point *= self._alpha
            point += self._beta * self.__evaluate_convex_hull(node_list)

            return point

    def __evaluate_graph(self):
        min_x = min_y = min_z = math.inf
        max_x = max_y = max_z = -math.inf
        for node in self._graph.node_list:
            if node.type == "primal":
                min_x, min_y, min_z = min(node.x, min_x), min(node.y, min_y), min(node.z, min_z)
                max_x, max_y, max_z = max(node.x, max_x), max(node.y, max_y), max(node.z, max_z)

        width = (max_x - min_x) / 2 + 1
        height = (max_y - min_y) / 2 + 1
        depth = (max_z - min_z) / 2 + 1

        return width * height * depth

    @staticmethod
    def __evaluate_convex_hull(node_list):
        min_x = min_y = min_z = math.inf
        max_x = max_y = max_z = -math.inf
        for node in node_list:
            min_x = min(node.x, min_x)
            min_y = min(node.y, min_y)
            min_z = min(node.z, min_z)
            max_x = max(node.x, max_x)
            max_y = max(node.y, max_y)
            max_z = max(node.z, max_z)

        width = (max_x - min_x) / 2 + 1
        height = (max_y - min_y) / 2 + 1
        depth = (max_z - min_z) / 2 + 1

        return width + height + depth

    @staticmethod
    def __evaluate_wiring_distance(edge_list):
        min_x = min_y = min_z = math.inf
        max_x = max_y = max_z = -math.inf
        for edge in edge_list:
            node1, node2 = edge.node1, edge.node2
            min_x = min(node1.x, node2.x, min_x)
            min_y = min(node1.y, node2.y, min_y)
            min_z = min(node1.z, node2.z, min_z)
            max_x = max(node1.x, node2.x, max_x)
            max_y = max(node1.y, node2.y, max_y)
            max_z = max(node1.z, node2.z, max_z)

        point = (max_x - min_x) + (max_y - min_y) + (max_z - min_z)

        return point * 2
