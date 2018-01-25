import math

from ..vector3d import Vector3D, Size
from ..node import Node
from ..edge import Edge


class Braidpack:
    def __init__(self, graph):
        self._graph = graph
        self._size = self.__create_size()
        self._var_node_count = graph.var_node_count

        self.__delete_not_closed()

    def execute(self):
        self.__compress()

        return self._graph

    def __compress(self):
        """
        Z軸方向に圧縮する
        """
        for n in range(0, 1):
            print("----- {} -----".format(n))
            for z in range(3, 13):
                print("-- {} --".format(z))
                press_edge_list = []
                slide_x_edge_list = []
                slide_y_edge_list = []
                for edge in self._graph.edge_list:
                    if edge.z == z and edge.dir != "Z":
                        if self.__can_move(edge):
                            press_edge_list.append(edge)
                        if edge.dir == "Y" and self.__can_move_x(edge):
                            slide_x_edge_list.append(edge)
                        if edge.dir == "X" and self.__can_move_y(edge):
                            slide_y_edge_list.append(edge)

                self.__move(press_edge_list)
                for edge in slide_x_edge_list:
                    edge.dump()
                # self.__slide_x(slide_x_edge_list)
                # self.__slide_y(slide_y_edge_list)
                press_edge_list.clear()
                slide_x_edge_list.clear()
                slide_y_edge_list.clear()

    def __move(self, edge_list):
        for edge in edge_list:
            node1, node2 = edge.node1, edge.node2
            id_, type_ = node1.edge_list[0].id, node1.type

            # create node
            new_node1, exist1 = self.__new_node(type_, node1.x, node1.y, node1.z - 2)
            new_node2, exist2 = self.__new_node(type_, node2.x, node2.y, node2.z - 2)

            # create edge
            new_edge = self.__new__edge(new_node1, new_node2, "edge")
            self.__new__edge(node1, new_node1, "edge")
            self.__new__edge(node2, new_node2, "edge")

            # delete node and edge
            del_edge = self.__edge(node1, node2)
            self.__delete_edge(del_edge)
            node1.remove_edge(del_edge)
            node2.remove_edge(del_edge)
            if exist1:
                self.__delete_node(node1)
                del_edge = self.__edge(node1, new_node1)
                self.__delete_edge(del_edge)
                new_node1.remove_edge(del_edge)
                # new_edge.dump()
                new_node1.add_edge(new_edge)
            if exist2:
                self.__delete_node(node2)
                del_edge = self.__edge(node2, new_node2)
                self.__delete_edge(del_edge)
                new_node2.remove_edge(del_edge)
                # new_edge.dump()
                new_node2.add_edge(new_edge)

    def __slide_x(self, edge_list):
        print("-- slide x --")
        for edge in edge_list:
            if edge.x < 3.0:
                return

            edge.dump()
            diff_x = 2
            node1, node2 = edge.node1, edge.node2
            print("node1", end=": ")
            node1.dump()
            for edge1 in node1.edge_list:
                edge1.dump()
            print("node2", end=": ")
            node2.dump()
            for edge2 in node2.edge_list:
                edge2.dump()
            id_, type_ = node1.edge_list[0].id, node1.type

            # create node
            new_node1, exist1 = self.__new_node(type_, node1.x + diff_x, node1.y, node1.z)
            new_node2, exist2 = self.__new_node(type_, node2.x + diff_x, node2.y, node2.z)

            # create edge
            new_edge = self.__new__edge(new_node1, new_node2, "edge")
            self.__new__edge(node1, new_node1, "edge")
            self.__new__edge(node2, new_node2, "edge")

            # delete node and edge
            del_edge = self.__edge(node1, node2)
            self.__delete_edge(del_edge)
            node1.remove_edge(del_edge)
            node2.remove_edge(del_edge)
            if exist1:
                self.__delete_node(node1)
                del_edge = self.__edge(node1, new_node1)
                self.__delete_edge(del_edge)
                new_node1.remove_edge(del_edge)
                new_node1.add_edge(new_edge)
            if exist2:
                self.__delete_node(node2)
                del_edge = self.__edge(node2, new_node2)
                self.__delete_edge(del_edge)
                new_node2.remove_edge(del_edge)
                new_node2.add_edge(new_edge)

    def __slide_y(self, edge):
        pass
        # diff_y = 2
        # node1, node2 = edge.node1, edge.node2
        # id_, type_ = node1.edge_list[0].id, node1.type
        #
        # # create node
        # new_node1, exist1 = self.__new_node(type_, node1.x, node1.y + diff_y, node1.z)
        # new_node2, exist2 = self.__new_node(type_, node2.x, node2.y + diff_y, node2.z)
        #
        # # create edge
        # new_edge = self.__new__edge(new_node1, new_node2, "edge")
        # self.__new__edge(node1, new_node1, "edge")
        # self.__new__edge(node2, new_node2, "edge")
        #
        # # delete node and edge
        # del_edge = self.__edge(node1, node2)
        # self.__delete_edge(del_edge)
        # node1.remove_edge(del_edge)
        # node2.remove_edge(del_edge)
        # if exist1:
        #     self.__delete_node(node1)
        #     del_edge = self.__edge(node1, new_node1)
        #     self.__delete_edge(del_edge)
        #     new_node1.remove_edge(del_edge)
        #     new_node1.add_edge(new_edge)
        # if exist2:
        #     self.__delete_node(node2)
        #     del_edge = self.__edge(node2, new_node2)
        #     self.__delete_edge(del_edge)
        #     new_node2.remove_edge(del_edge)
        #     new_node2.add_edge(new_edge)

    def __can_move(self, edge):
        cross_pos = Vector3D(edge.x, edge.y, edge.z - 1)
        for e in self._graph.edge_list:
            if e.x == cross_pos.x and e.y == cross_pos.y and e.z == cross_pos.z:
                return False

        node1, node2 = edge.node1, edge.node2
        obstacle_node1, obstacle_node2 = None, None
        can_move1, can_move2 = False, False
        for node in self._graph.node_list:
            if node.x == node1.x and node.y == node1.y and node.z == node1.z - 2:
                obstacle_node1 = node
            if node.x == node2.x and node.y == node2.y and node.z == node2.z - 2:
                obstacle_node2 = node

        if obstacle_node1 is None:
            can_move1 = True
        else:
            for edge in obstacle_node1.edge_list:
                alt_node = edge.alt_node(obstacle_node1)
                if alt_node == node1:
                    can_move1 = True

        if obstacle_node2 is None:
            can_move2 = True
        else:
            for edge in obstacle_node2.edge_list:
                alt_node = edge.alt_node(obstacle_node2)
                if alt_node == node2:
                    can_move2 = True

        if can_move1 and can_move2:
            return True

        return False

    def __can_move_x(self, edge):
        cross_pos = Vector3D(edge.x + 1, edge.y, edge.z)
        for e in self._graph.edge_list:
            if e.x == cross_pos.x and e.y == cross_pos.y and e.z == cross_pos.z:
                return False

        node1, node2 = edge.node1, edge.node2
        obstacle_node1, obstacle_node2 = None, None
        can_move1, can_move2 = False, False
        for node in self._graph.node_list:
            if node.x == node1.x + 2 and node.y == node1.y and node.z == node1.z:
                obstacle_node1 = node
            if node.x == node2.x + 2 and node.y == node2.y and node.z == node2.z:
                obstacle_node2 = node

        if obstacle_node1 is None:
            can_move1 = True
        else:
            for edge in obstacle_node1.edge_list:
                alt_node = edge.alt_node(obstacle_node1)
                if alt_node == node1:
                    can_move1 = True

        if obstacle_node2 is None:
            can_move2 = True
        else:
            for edge in obstacle_node2.edge_list:
                alt_node = edge.alt_node(obstacle_node2)
                if alt_node == node2:
                    can_move2 = True

        if can_move1 and can_move2:
            return True

        return False

    def __can_move_y(self, edge):
        cross_pos = Vector3D(edge.x, edge.y + 1, edge.z)
        for e in self._graph.edge_list:
            if e.x == cross_pos.x and e.y == cross_pos.y and e.z == cross_pos.z:
                return False

        node1, node2 = edge.node1, edge.node2
        obstacle_node1, obstacle_node2 = None, None
        can_move1, can_move2 = False, False
        for node in self._graph.node_list:
            if node.x == node1.x and node.y == node1.y + 2 and node.z == node1.z:
                obstacle_node1 = node
            if node.x == node2.x and node.y == node2.y + 2 and node.z == node2.z:
                obstacle_node2 = node

        if obstacle_node1 is None:
            can_move1 = True
        else:
            for edge in obstacle_node1.edge_list:
                alt_node = edge.alt_node(obstacle_node1)
                if alt_node == node1:
                    can_move1 = True

        if obstacle_node2 is None:
            can_move2 = True
        else:
            for edge in obstacle_node2.edge_list:
                alt_node = edge.alt_node(obstacle_node2)
                if alt_node == node2:
                    can_move2 = True

        if can_move1 and can_move2:
            return True

        return False

    def __delete_not_closed(self):
        """
        閉じていないdefectを削除する
        """
        non_loop_edge_index = []
        non_loop_node_index = []
        for no, edge in enumerate(self._graph.edge_list):
            # 閉じていないdefectにはidに0が振られている
            if edge.id == 0:
                non_loop_edge_index.append(no)
                (node1, node2) = (edge.node1, edge.node2)
                non_loop_node_index.append(self._graph.node_list.index(node1))
                non_loop_node_index.append(self._graph.node_list.index(node2))

        non_loop_edge_index.reverse()
        # 重複した要素を取り除く
        non_loop_node_index = list(set(non_loop_node_index))
        non_loop_node_index.sort()
        non_loop_node_index.reverse()

        # delete edge
        for index in non_loop_edge_index:
            del self._graph.edge_list[index]

        # delete node
        for index in non_loop_node_index:
            has_injector = False
            for edge in self._graph.node_list[index].edge_list:
                if edge.is_injector():
                    has_injector = True
            if not has_injector:
                del self._graph.node_list[index]

    def __create_size(self):
        max_x = max_y = max_z = -math.inf
        for node in self._graph.node_list:
            max_x = max(node.x, max_x)
            max_y = max(node.y, max_y)
            max_z = max(node.z, max_z)

        return Size(max_x, max_y, max_z)

    def __delete_node(self, del_node):
        """
        指定されたノードをグラフから削除する

        :param del_node 削除するノード
        """
        del_node_index = -1
        for no, node in enumerate(self._graph.node_list):
            if del_node == node:
                del_node_index = no

        if del_node_index > -1:
            del self._graph.node_list[del_node_index]

    def __delete_edge(self, del_edge):
        """
        指定された辺をグラフから削除する

        :param del_edge 削除する辺
        """
        del_edge_index = -1
        for no, edge in enumerate(self._graph.edge_list):
            if del_edge == edge:
                del_edge_index = no

        if del_edge_index > -1:
            del self._graph.edge_list[del_edge_index]

    @staticmethod
    def __edge(node1, node2):
        for edge in node1.edge_list:
            alt_node = edge.alt_node(node1)
            if alt_node == node2:
                return edge

    def __new_node_variable(self):
        self._var_node_count += 1
        return self._var_node_count

    def __new_node(self, type_, x, y, z):
        for node in self._graph.node_list:
            if node.x == x and node.y == y and node.z == z:
                return node, True

        node = Node(x, y, z, self.__new_node_variable(), type_)
        self._graph.add_node(node)

        return node, False

    def __new__edge(self, node1, node2, category, id_=0):
        if node1 == node2:
            return

        for edge in node1.edge_list:
            alt_node = edge.alt_node(node1)
            if alt_node == node2:
                return

        edge = Edge(node1, node2, category, id_)
        node1.add_edge(edge)
        node2.add_edge(edge)
        self._graph.add_edge(edge)

        return edge
