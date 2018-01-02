import math


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
            min_x = min_y = min_z = math.inf
            max_x = max_y = max_z = -math.inf
            for module_ in self._module_list:
                for node in module_.cross_node_list:
                    min_x = min(node.x, min_x)
                    min_y = min(node.y, min_y)
                    min_z = min(node.z, min_z)
                    max_x = max(node.x, max_x)
                    max_y = max(node.y, max_y)
                    max_z = max(node.z, max_z)

            width = (max_x - min_x) / 2 + 1
            height = (max_y - min_y) / 2 + 1
            depth = (max_z - min_z) / 2 + 1

            point = width + height + depth

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
