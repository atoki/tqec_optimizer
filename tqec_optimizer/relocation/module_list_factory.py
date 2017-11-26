import math

from .module import Module

from ..node import Joint
from ..edge import Edge


class ModuleListFactory:
    def __init__(self, graph, type_):
        self._type = type_
        self._graph = graph
        self._module_list = []
        # (端1, 端2, ループ番号)
        self._joint_pair_list = []

    def create(self):
        self.__create_module()
        return self._module_list, self._joint_pair_list

    def __create_module(self):
        for loop_id in range(1, self._graph.loop_count + 1):
            module_ = Module(loop_id)
            # (ループに属する辺, ←に交差する辺)
            edge_pair_list = []

            # ループを構成している辺をモジュールに追加する
            for edge in self._graph.edge_list:
                if edge.id == loop_id and edge.type == self._type:
                    module_.add_edge(edge)
                    if len(edge.cross_edge_list) > 0 and edge.cross_edge_list[0] in self._graph.edge_list:
                        edge_pair_list.append((edge, edge.cross_edge_list[0]))

            if len(module_.edge_list) == 0:
                continue

            # ループを構成している辺と交差している辺をモジュールに追加する
            for edge_pair in edge_pair_list:
                cross_node_list = self.__create_cross_node_list(module_, edge_pair[0], edge_pair[1])
                loop_id = edge_pair[1].id
                (joint1, joint2) = (None, None)
                (end1, end2) = (None, None)
                for no, cross_node in enumerate(cross_node_list):
                    id_ = loop_id if no == 0 or no == len(cross_node_list) - 1 else -1
                    joint1 = self.__new_joint(cross_node, id_)
                    if no == 0:
                        end1 = joint1
                    if no == len(cross_node_list) - 1:
                        end2 = joint1
                    if joint2 is not None:
                        new_cross_edge = self.__new__edge(joint1, joint2, "edge", loop_id)
                        if new_cross_edge == edge_pair[1]:
                            new_cross_edge.add_cross_edge(edge_pair[0])
                            new_cross_edge.set_color(0x00ffff)
                        module_.add_cross_edge(new_cross_edge)
                    joint2 = joint1
                self._joint_pair_list.append((end1, end2, loop_id))

            # モジュールを構成する全ての辺から座標とサイズ情報を更新する
            module_.update()

            # モジュールの中身があればリストに追加
            self._module_list.append(module_)

    def __create_cross_node_list(self, module_, border1, cross_edge):
        (min_, max_) = (math.inf, -math.inf)

        if border1.dir == 'X':
            for edge in module_.edge_list:
                if border1.x == edge.x and border1 != edge:
                    if cross_edge.dir == 'Y':
                        max_ = max(border1.y, edge.y)
                        min_ = min(border1.y, edge.y)
                    elif cross_edge.dir == 'Z':
                        max_ = max(border1.z, edge.z)
                        min_ = min(border1.z, edge.z)
                    break
        elif border1.dir == 'Y':
            for edge in module_.edge_list:
                if border1.y == edge.y and border1 != edge:
                    if cross_edge.dir == 'X':
                        max_ = max(border1.x, edge.x)
                        min_ = min(border1.x, edge.x)
                    elif cross_edge.dir == 'Z':
                        max_ = max(border1.z, edge.z)
                        min_ = min(border1.z, edge.z)
                    break
        else:
            for edge in module_.edge_list:
                if border1.z == edge.z and border1 != edge:
                    if cross_edge.dir == 'X':
                        max_ = max(border1.x, edge.x)
                        min_ = min(border1.x, edge.x)
                    elif cross_edge.dir == 'Y':
                        max_ = max(border1.y, edge.y)
                        min_ = min(border1.y, edge.y)
                    break

        if min_ == math.inf or max_ == math.inf:
            return []

        cross_node_list = self.__expand_edge((min_, max_), cross_edge)
        return cross_node_list

    def __expand_edge(self, range_, cross_edge):
        cross_node_list = []
        (min_, max_) = (range_[0], range_[1])

        if min_ == math.inf or max_ == math.inf:
            return cross_node_list

        if cross_edge.dir == 'X':
            (y, z) = (cross_edge.y, cross_edge.z)
            for x in range(int(min_), int(max_) + 1, 2):
                edge = self.__edge(x, y, z)
                if edge is None:
                    break
                cross_node_list.append(edge.node1)
                cross_node_list.append(edge.node2)
            cross_node_list = list(set(cross_node_list))
            cross_node_list.sort(key=lambda m: (m.x))

        elif cross_edge.dir == 'Y':
            (x, z) = (cross_edge.x, cross_edge.z)
            for y in range(int(min_), int(max_) + 1, 2):
                edge = self.__edge(x, y, z)
                if edge is None:
                    break
                cross_node_list.append(edge.node1)
                cross_node_list.append(edge.node2)
            cross_node_list = list(set(cross_node_list))
            cross_node_list.sort(key=lambda m: (m.y))

        else:
            (x, y) = (cross_edge.x, cross_edge.y)
            for z in range(int(min_), int(max_) + 1, 2):
                edge = self.__edge(x, y, z)
                if edge is None:
                    break
                cross_node_list.append(edge.node1)
                cross_node_list.append(edge.node2)
            cross_node_list = list(set(cross_node_list))
            cross_node_list.sort(key=lambda m: (m.z))

        return cross_node_list

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
