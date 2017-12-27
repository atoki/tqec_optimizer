from .module import Module

from ..position import Position
from ..node import Node
from ..edge import Edge


class ModuleFactory:
    def __init__(self, type_, loop):
        self._type = type_
        self._loop = loop
        self._module = Module(self._loop.id)
        # (端1, 端2, 端1と端2を繋ぐ辺)
        self._joint_pair_list = []

    def create(self):
        self.__create_frame()
        self.__create_cross_edge()
        self._module.update()

        return self._module, self._joint_pair_list

    def __create_frame(self):
        cross_edge_num = len(self._loop.cross_list)
        node_array = []
        pos = Position(0, 0, 0)

        # create frame node
        node_array.append(self.__new_node(pos))
        pos.incy(2)
        node_array.append(self.__new_node(pos))
        for n in range(0, cross_edge_num):
            pos.incz(2)
            node_array.append(self.__new_node(pos))
        pos.decy(2)
        node_array.append(self.__new_node(pos))
        for n in range(0, cross_edge_num - 1):
            pos.decz(2)
            node_array.append(self.__new_node(pos))

        # create frame edge
        last_node = None
        for node in node_array:
            if last_node is not None:
                edge = self.__new__edge(node, last_node, "edge", self._loop.id)
                self._module.add_edge(edge)
            last_node = node
        edge = self.__new__edge(node_array[0], last_node, "edge", self._loop.id)
        self._module.add_edge(edge)

    def __create_cross_edge(self):
        type_ = "dual" if self._type == "primal" else "primal"
        pos1, pos2 = Position(1, 1, 1), Position(-1, 1, 1)
        for cross_edge_id in self._loop.cross_list:
            node1 = self.__new_node(pos1, type_, cross_edge_id)
            node2 = self.__new_node(pos2, type_, cross_edge_id)
            cross_edge = self.__new__edge(node1, node2, "edge", cross_edge_id)
            self._module.add_cross_edge(cross_edge)
            self._joint_pair_list.append((node1, node2, cross_edge))
            pos1.incz(2)
            pos2.incz(2)

    def __new_node(self, pos, type_=None, id_=0):
        if type_ is None:
            node = Node(pos.x, pos.y, pos.z, self._loop.id, self._type)
        else:
            node = Node(pos.x, pos.y, pos.z, id_, type_)

        self._module.add_node(node)
        return node

    @staticmethod
    def __new__edge(node1, node2, category, id_=0):
        edge = Edge(node1, node2, category, id_)
        node1.add_edge(edge)
        node2.add_edge(edge)

        return edge


