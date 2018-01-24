from .module import Module

from ..vector3d import Vector3D
from ..node import Node, Joint
from ..edge import Edge, CrossEdge


class ModuleFactory:
    def __init__(self, type_, loop):
        self._type = type_
        self._loop = loop
        self._module = Module(self._loop.id)

    def create(self):
        self.__create_frame()
        self.__create_cross_edge()
        self._module.update()

        return self._module

    def __create_frame(self):
        cross_edge_num = max(1, len(self._loop.cross_list))
        injector_num = max(0, len(self._loop.injector_list) - 1)
        node_array = []
        pos = Vector3D(0, 0, 0)

        # create frame node
        node_array.append(self.__new_node("frame", pos))
        pos.incy(2)
        node_array.append(self.__new_node("frame", pos))
        for n in range(0, cross_edge_num + injector_num):
            pos.incz(2)
            node_array.append(self.__new_node("frame", pos))
        pos.decy(2)
        node_array.append(self.__new_node("frame", pos))
        for n in range(0, cross_edge_num + injector_num - 1):
            pos.decz(2)
            node_array.append(self.__new_node("frame", pos))

        # create frame edge
        last_node = None
        for node in node_array:
            if last_node is not None:
                edge = self.__new__edge("frame", node, last_node, "edge", self._loop.id)
                self._module.add_frame_edge(edge)
            last_node = node
        edge = self.__new__edge("frame", node_array[0], last_node, "edge", self._loop.id)
        self._module.add_frame_edge(edge)

    def __create_cross_edge(self):
        type_ = "dual" if self._type == "primal" else "primal"
        pos1, pos2 = Vector3D(1, 1, 1), Vector3D(-1, 1, 1)
        for cross_edge_id in self._loop.cross_list:
            joint1 = self.__new_node("cross", pos1, type_, cross_edge_id, set(self._loop.cross_list))
            joint2 = self.__new_node("cross", pos2, type_, cross_edge_id, set(self._loop.cross_list))
            cross_edge = self.__new__edge("cross", joint1, joint2, "edge", cross_edge_id, self._loop.id)
            self._module.add_cross_edge(cross_edge)
            self._module.add_cross_id(cross_edge_id)
            self._module.add_joint_pair((joint1, joint2, cross_edge))
            pos1.incz(2)
            pos2.incz(2)

    def __new_node(self, category, pos, type_=None, id_=0, id_set=None):
        if category == "frame":
            node = Node(pos.x, pos.y, pos.z, self._loop.id, self._type)
            self._module.add_frame_node(node)
        else:
            node = Joint(pos.x, pos.y, pos.z, id_, type_)
            node.set_id_set(id_set)
            self._module.add_cross_node(node)

        return node

    @staticmethod
    def __new__edge(class_, node1, node2, category, id_=0, module_id=0):
        if class_ == "frame":
            edge = Edge(node1, node2, category, id_)
            node1.add_edge(edge)
            node2.add_edge(edge)
        else:
            edge = CrossEdge(node1, node2, category, id_, module_id)
            node1.add_edge(edge)
            node2.add_edge(edge)

        return edge


