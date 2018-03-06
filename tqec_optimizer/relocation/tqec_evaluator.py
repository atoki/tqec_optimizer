import math

from ..vector3d import Vector3D


class TqecEvaluator:
    def __init__(self, module_list):
        self._module_list = module_list

    def evaluate(self):
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
        point += self.__evaluate_wiring(point, (max(width, height, depth) - 1) * 2)

        return point

    def __evaluate_wiring(self, perimeter, max_size):
        cost = 0.0
        count = 0
        for m1 in self._module_list:
            for m2 in self._module_list:
                if m1.id != m2.id:
                    center1 = Vector3D(m1.pos.x + m1.width / 2, m1.pos.y + m1.height / 2, m1.pos.z + m1.depth / 2)
                    center2 = Vector3D(m2.pos.x + m2.width / 2, m2.pos.y + m2.height / 2, m2.pos.z + m2.depth / 2)
                    dist = center1.dist(center2)
                    intersection = m1.cross_id_list & m2.cross_id_list
                    cost = cost + dist * len(intersection)
                    count = count + len(intersection)

        cost = cost / 2
        count = count / 2

        module_num = len(self._module_list)
        point = (cost - module_num * 2) / (max_size * count - module_num * 2)
        point = perimeter * 0.25 * point

        return point
