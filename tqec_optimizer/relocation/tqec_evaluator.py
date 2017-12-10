import math

from collections import defaultdict


class TqecEvaluator:
    def __init__(self, module_list):
        self._module_list = module_list

    def evaluate(self):
        point = 0
        edge_map = defaultdict(list)
        for module_ in self._module_list:
            for edge in module_.cross_edge_list:
                edge_map[edge.id].append(edge)

        for id_, edge_list in edge_map.items():
            point += self.__evaluate_module(edge_list)

        return point

    @staticmethod
    def __evaluate_module(edge_list):
        min_x = min_y = min_z = math.inf
        max_x = max_y = max_z = -math.inf
        for edge in edge_list:
            node1, node2 = edge.node1, edge.node2
            min_x = min(node1.x, min_x)
            min_y = min(node1.y, min_y)
            min_z = min(node1.z, min_z)
            max_x = max(node1.x, max_x)
            max_y = max(node1.y, max_y)
            max_z = max(node1.z, max_z)

            min_x = min(node2.x, min_x)
            min_y = min(node2.y, min_y)
            min_z = min(node2.z, min_z)
            max_x = max(node2.x, max_x)
            max_y = max(node2.y, max_y)
            max_z = max(node2.z, max_z)

        point = (max_x - min_x) + (max_y - min_y) + (max_z - min_z)

        return point * 2
