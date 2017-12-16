import math

from collections import defaultdict


class TqecEvaluator:
    def __init__(self, module_list):
        self._module_list = module_list

    def evaluate(self):
        point = 0
        node_list = []
        for module_ in self._module_list:
            for edge in module_.edge_list:
                node_list.append(edge.node1)
                node_list.append(edge.node2)

        point += self.__evaluate_convex_hull(node_list)

        return point

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

        return width * height * depth

    @staticmethod
    def __evaluate_wiring_distance(edge_list):
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
