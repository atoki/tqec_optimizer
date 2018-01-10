import random
import math

from collections import defaultdict


class Allocation:
    def __init__(self, module_list, id_set):
        self._module_list = module_list
        self._id_set = id_set
        self._edge_map = {}
        self._connect_edge = defaultdict(list)

        # init
        for module_ in self._module_list:
            for edge in module_.edge_list:
                edge.set_id(0)
                edge.node1.set_id(0)
                edge.node2.set_id(0)

    def execute(self):
        self.__detect_connect_edge()
        self.__assign_connect_edge()
        self.__assign_isolated_edge()
        self.__sa()

    def __sa(self):
        initial_t = 100
        final_t = 0.01
        cool_rate = 0.97
        limit = 100

        current_cost = self.__evaluate(self._module_list)
        t = initial_t
        while t > final_t:
            for n in range(limit):
                module_size = len(self._module_list)
                module_index = random.randint(0, module_size - 1)
                cross_edge_size = len(self._module_list[module_index].cross_edge_list)
                edge_index1 = random.randint(0, cross_edge_size - 1)
                edge_index2 = random.randint(0, cross_edge_size - 1)

                if not self.__swap(module_index, edge_index1, edge_index2):
                    continue

                new_cost = self.__evaluate(self._module_list)

                if self.__should_change(new_cost - current_cost, t):
                    current_cost = new_cost
                else:
                    self.__swap(module_index, edge_index1, edge_index2)
            t *= cool_rate

    @staticmethod
    def __should_change(delta, t):
        if delta <= 0:
            return 1
        if random.random() < math.exp(- delta / t):
            return 1
        return 0

    def __swap(self, module_index, edge_index1, edge_index2):
        edge1 = self._module_list[module_index].cross_edge_list[edge_index1]
        edge2 = self._module_list[module_index].cross_edge_list[edge_index2]

        if edge1.is_fixed() or edge2.is_fixed():
            return False

        edge1_id = edge1.id
        edge2_id = edge2.id
        edge1.set_id(edge2_id)
        edge1.node1.set_id(edge2_id)
        edge1.node2.set_id(edge2_id)
        edge2.set_id(edge1_id)
        edge2.node1.set_id(edge1_id)
        edge2.node2.set_id(edge1_id)

        return True

    @staticmethod
    def __evaluate(module_list):
        cross_node_map = defaultdict(list)
        for module_ in module_list:
            for node in module_.cross_node_list:
                cross_node_map[node.id].append(node)

        point = 0.0
        for id_, node_list in cross_node_map.items():
            min_x = min_y = min_z = math.inf
            max_x = max_y = max_z = -math.inf
            for node in node_list:
                min_x, min_y, min_z = min(node.x, min_x), min(node.y, min_y), min(node.z, min_z)
                max_x, max_y, max_z = max(node.x, max_x), max(node.y, max_y), max(node.z, max_z)

            point += ((max_x - min_x) + (max_y - min_y) + (max_z - min_z)) * 2.0

        return point

    def __detect_connect_edge(self):
        for module_ in self._module_list:
            for joint_pair in module_.joint_pair_list:
                joint1, joint2 = joint_pair[0], joint_pair[1]
                edge = joint_pair[2]

                if joint1 in self._edge_map and joint2 in self._edge_map:
                    self._connect_edge[self._edge_map[joint1]].extend(self._connect_edge[self._edge_map[joint2]])
                    self._connect_edge[self._edge_map[joint1]].append(edge)
                    del_edge = self._edge_map[joint2]

                    for edge in self._connect_edge[self._edge_map[joint2]]:
                        node1, node2 = edge.node1, edge.node2
                        self._edge_map[node1] = self._edge_map[joint1]
                        self._edge_map[node2] = self._edge_map[joint1]

                    del self._connect_edge[del_edge]

                elif joint1 in self._edge_map:
                    self._edge_map[joint2] = self._edge_map[joint1]
                    self._connect_edge[self._edge_map[joint1]].append(edge)

                elif joint2 in self._edge_map:
                    self._edge_map[joint1] = self._edge_map[joint2]
                    self._connect_edge[self._edge_map[joint2]].append(edge)

                else:
                    self._edge_map[joint1] = edge
                    self._edge_map[joint2] = edge
                    self._connect_edge[edge].append(edge)

    def __assign_connect_edge(self):
        for key_edge, edge_list in sorted(self._connect_edge.items(), key=lambda x: len(x[1]), reverse=True):
            if len(edge_list) == 1:
                break

            result = self._id_set[edge_list[0].module_id]
            for edge in edge_list:
                tmp = self._id_set[edge.module_id]
                result = result & tmp

            assign_id = result.pop()
            for edge in edge_list:
                edge.set_id(assign_id)
                edge.fix()
                edge.node1.set_id(assign_id)
                edge.node2.set_id(assign_id)
                self._id_set[edge.module_id].remove(assign_id)

    def __assign_isolated_edge(self):
        for module_ in self._module_list:
            for edge in module_.cross_edge_list:
                if edge.id > 0:
                    continue
                assign_id = self._id_set[edge.module_id].pop()
                edge.set_id(assign_id)
                edge.node1.set_id(assign_id)
                edge.node2.set_id(assign_id)
