import math

from .module import Module

from ..node import Joint
from ..edge import Edge


class ModuleListFactory:
    def __init__(self, graph, type_):
        self._type = type_
        self._graph = graph
        self._module_list = []
        # (端1, 端2, 端1と端2を繋ぐ辺)
        self._joint_pair_list = []

    def create(self):
        self.__create_module()
        return self._module_list, self._joint_pair_list

    def __create_module(self):
        for loop_id in range(1, self._graph.loop_count + 1):
            module_ = Module(loop_id)

            # ループを構成している辺をモジュールに追加する
            for edge in self._graph.edge_list:
                if edge.id == loop_id and edge.type == self._type:
                    module_.add_edge(edge)
                    module_.add_node(edge.node1)
                    module_.add_node(edge.node2)

            if len(module_.edge_list) == 0:
                continue

            module_.update()
            self.__create_cross_edge(module_)
            module_.update()
            self._module_list.append(module_)

    def __create_cross_edge(self, module_):
        min_x, max_x = module_.pos.x, module_.pos.x + module_.width
        min_y, max_y = module_.pos.y, module_.pos.y + module_.height
        min_z, max_z = module_.pos.z, module_.pos.z + module_.depth

        used_node = {}
        for edge in self._graph.edge_list:
            if edge.type == self._type:
                continue

            if min_x < edge.x < max_x \
                    and min_y < edge.y < max_y \
                    and min_z < edge.z < max_z:
                joint1 = used_node[edge.node1] \
                    if edge.node1 in used_node \
                    else self.__new_joint(edge.node1, edge.id)
                joint2 = used_node[edge.node2] \
                    if edge.node2 in used_node \
                    else self.__new_joint(edge.node2, edge.id)
                cross_edge = self.__new__edge(joint1, joint2, "edge", edge.id)
                module_.add_node(joint1)
                module_.add_node(joint2)
                module_.add_cross_edge(cross_edge)
                self._joint_pair_list.append((joint1, joint2, cross_edge))
                used_node[edge.node1] = joint1
                used_node[edge.node2] = joint2

    def __edge(self, x, y, z):
        for edge in self._graph.edge_list:
            if edge.x == x and edge.y == y and edge.z == z:
                return edge

        return None

    @staticmethod
    def __new_joint(node, id_=0):
        joint = Joint(node.x, node.y, node.z, id_, node.type)

        return joint

    @staticmethod
    def __new__edge(node1, node2, category, id_=0):
        edge = Edge(node1, node2, category, id_)
        node1.add_edge(edge)
        node2.add_edge(edge)

        return edge

    @staticmethod
    def __create_random_color(loop_id):
        colors = [0xffdead, 0x808080, 0x191970, 0x00ffff, 0x008000,
                  0x00ff00, 0xffff00, 0x8b0000, 0xff1493, 0x800080]
        return colors[loop_id % 10]
