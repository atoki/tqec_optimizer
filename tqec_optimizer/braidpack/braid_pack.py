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
        for n in range(0, 20):
            for z in range(3, self._size.z + 1):
                press_edge_list = []
                slide_x_edge_list = []
                slide_y_edge_list = []
                for edge in self._graph.edge_list:
                    if edge.z == z and edge.dir != "Z":
                        if self.__can_move(edge):
                            press_edge_list.append(edge)
                        elif edge.dir == "Y" and self.__can_move_x(edge):
                            slide_x_edge_list.append(edge)
                        elif edge.dir == "X" and self.__can_move_y(edge):
                            slide_y_edge_list.append(edge)

                self.__move(press_edge_list)
                # self.__slide_x(slide_x_edge_list)
                # self.__slide_y(slide_y_edge_list)

                press_edge_list.clear()
                slide_x_edge_list.clear()
                slide_y_edge_list.clear()

    def __move(self, edge_list):
        for edge in edge_list:
            node1, node2 = edge.node1, edge.node2
            id_, type_ = node1.edge_list[0].id, node1.type
            category = edge.category

            # primal defect に付いたinjectorの移動
            if len(node1.edge_list) > 2:
                new_node1, exist1 = self.__new_node(type_, node1.x, node1.y, node1.z - 2)
                new_node2, exist2 = self.__new_node(type_, node2.x, node2.y, node2.z - 2)
                del_edge = self.__edge(node1, node2)
                self.__delete_edge(del_edge)
                node1.remove_edge(del_edge)
                node2.remove_edge(del_edge)
                new_edge = self.__new__edge(new_node1, new_node2, category)
                new_node1.add_edge(new_edge)
                new_node2.add_edge(new_edge)
                continue

            # create node
            new_node1, exist1 = self.__new_node(type_, node1.x, node1.y, node1.z - 2)
            new_node2, exist2 = self.__new_node(type_, node2.x, node2.y, node2.z - 2)

            # create edge
            new_edge1 = self.__new__edge(new_node1, new_node2, category)
            new_edge2 = self.__new__edge(node1, new_node1, "edge")
            new_edge3 = self.__new__edge(node2, new_node2, "edge")

            # delete node and edge
            self.__delete_edge(edge)
            node1.remove_edge(edge)
            node2.remove_edge(edge)
            new_node1.add_edge(new_edge1)
            new_node2.add_edge(new_edge1)
            if exist1:
                node1.remove_edge(new_edge2)
                new_node1.remove_edge(new_edge2) 
                self.__delete_node(node1)
                self.__delete_edge(new_edge2)
            if exist2:
                node2.remove_edge(new_edge3)
                new_node2.remove_edge(new_edge3)
                self.__delete_node(node2)
                self.__delete_edge(new_edge3)

            if not exist1:
                node1.add_edge(new_edge2)
                new_node1.add_edge(new_edge2)

            if not exist2:
                node2.add_edge(new_edge3)
                new_node2.add_edge(new_edge3)

    def __slide_x(self, edge_list):
        for edge in edge_list:
            coef = self.__calc_gravity_dir(edge, "X")
            node1, node2 = edge.node1, edge.node2
            id_, type_ = node1.edge_list[0].id, node1.type
            category = edge.category

            # create node
            new_node1, exist1 = self.__new_node(type_, node1.x + 2 * coef, node1.y, node1.z)
            new_node2, exist2 = self.__new_node(type_, node2.x + 2 * coef, node2.y, node2.z)

            # create edge
            new_edge1 = self.__new__edge(new_node1, new_node2, category)
            new_edge2 = self.__new__edge(node1, new_node1, "edge")
            new_edge3 = self.__new__edge(node2, new_node2, "edge")

            # delete node and edge
            self.__delete_edge(edge)
            node1.remove_edge(edge)
            node2.remove_edge(edge)
            new_node1.add_edge(new_edge1)
            new_node2.add_edge(new_edge1)
            if exist1:
                node1.remove_edge(new_edge2)
                new_node1.remove_edge(new_edge2)
                self.__delete_node(node1)
                self.__delete_edge(new_edge2)
            if exist2:
                node2.remove_edge(new_edge3)
                new_node2.remove_edge(new_edge3)
                self.__delete_node(node2)
                self.__delete_edge(new_edge3)

            if not exist1:
                node1.add_edge(new_edge2)
                new_node1.add_edge(new_edge2)
            if not exist2:
                node2.add_edge(new_edge3)
                new_node2.add_edge(new_edge3)

    def __slide_y(self, edge_list):
        for edge in edge_list:
            coef = self.__calc_gravity_dir(edge, "Y")
            node1, node2 = edge.node1, edge.node2
            id_, type_ = node1.edge_list[0].id, node1.type
            category = edge.category

            # create node
            new_node1, exist1 = self.__new_node(type_, node1.x, node1.y + 2 * coef, node1.z)
            new_node2, exist2 = self.__new_node(type_, node2.x, node2.y + 2 * coef, node2.z)

            # create edge
            new_edge1 = self.__new__edge(new_node1, new_node2, category)
            new_edge2 = self.__new__edge(node1, new_node1, "edge")
            new_edge3 = self.__new__edge(node2, new_node2, "edge")

            # delete node and edge
            self.__delete_edge(edge)
            node1.remove_edge(edge)
            node2.remove_edge(edge)
            new_node1.add_edge(new_edge1)
            new_node2.add_edge(new_edge1)
            if exist1:
                node1.remove_edge(new_edge2)
                new_node1.remove_edge(new_edge2)
                self.__delete_node(node1)
                self.__delete_edge(new_edge2)
            if exist2:
                node2.remove_edge(new_edge3)
                new_node2.remove_edge(new_edge3)
                self.__delete_node(node2)
                self.__delete_edge(new_edge3)

            if not exist1:
                node1.add_edge(new_edge2)
                new_node1.add_edge(new_edge2)
            if not exist2:
                node2.add_edge(new_edge3)
                new_node2.add_edge(new_edge3)

    def __can_move(self, edge):
        cross_pos = Vector3D(edge.x, edge.y, edge.z - 1)
        next_pos = Vector3D(edge.x, edge.y, edge.z - 2)
        for e in self._graph.edge_list:
            if e.x == cross_pos.x and e.y == cross_pos.y and e.z == cross_pos.z:
                return False
            if e.x == next_pos.x and e.y == next_pos.y and e.z == next_pos.z:
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
        coef = self.__calc_gravity_dir(edge, "X")
        cross_pos = Vector3D(edge.x + 1 * coef, edge.y, edge.z)
        next_pos = Vector3D(edge.x + 2 * coef, edge.y, edge.z)
        for e in self._graph.edge_list:
            if e.x == cross_pos.x and e.y == cross_pos.y and e.z == cross_pos.z:
                return False
            if e.x == next_pos.x and e.y == next_pos.y and e.z == next_pos.z:
                return False

        node1, node2 = edge.node1, edge.node2
        obstacle_node1, obstacle_node2 = None, None
        can_move1, can_move2 = False, False
        for node in self._graph.node_list:
            if node.x == node1.x + 2 * coef and node.y == node1.y and node.z == node1.z:
                obstacle_node1 = node
            if node.x == node2.x + 2 * coef and node.y == node2.y and node.z == node2.z:
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
        coef = self.__calc_gravity_dir(edge, "Y")
        cross_pos = Vector3D(edge.x, edge.y + 1 * coef, edge.z)
        next_pos = Vector3D(edge.x, edge.y + 2 * coef, edge.z)
        for e in self._graph.edge_list:
            if e.x == cross_pos.x and e.y == cross_pos.y and e.z == cross_pos.z:
                return False
            if e.x == next_pos.x and e.y == next_pos.y and e.z == next_pos.z:
                return False

        node1, node2 = edge.node1, edge.node2
        obstacle_node1, obstacle_node2 = None, None
        can_move1, can_move2 = False, False
        for node in self._graph.node_list:
            if node.x == node1.x and node.y == node1.y + 2 * coef and node.z == node1.z:
                obstacle_node1 = node
            if node.x == node2.x and node.y == node2.y + 2 * coef and node.z == node2.z:
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
        del_edge = None
        for index in non_loop_node_index:
            has_injector = False
            for edge in self._graph.node_list[index].edge_list:
                if edge.is_injector():
                    has_injector = True
                if edge.id == 0:
                    del_edge = edge
            if del_edge is not None:
                self._graph.node_list[index].remove_edge(del_edge)
            if not has_injector:
                del self._graph.node_list[index]

    def __calc_gravity_dir(self, edge, dir_):
        result = 1
        if dir_ == "X":
            result = self.__calc_x_gravity_dir(edge)
        if dir_ == "Y":
            result = self.__calc_y_gravity_dir(edge)

        return result

    def __calc_x_gravity_dir(self, edge):
        dir_ = 0
        p_exist, n_exist = False, False
        for e in self._graph.edge_list:
            if edge.x + 1 == e.x and edge.y == e.y and edge.z == e.z:
                p_exist = True
            if edge.x - 1 == e.x and edge.y == e.y and edge.z == e.z:
                n_exist = True

        if not p_exist and not n_exist:
            dir_ = 1
        elif not p_exist and n_exist:
            dir_ = 1
        elif p_exist and not n_exist:
            dir_ = -1

        return dir_

    def __calc_y_gravity_dir(self, edge):
        dir_ = 0
        p_exist, n_exist = False, False
        for e in self._graph.edge_list:
            if edge.x == e.x and edge.y + 1 == e.y and edge.z == e.z:
                p_exist = True
            if edge.x == e.x and edge.y - 1 == e.y and edge.z == e.z:
                n_exist = True

        if not p_exist and not n_exist:
            dir_ = 1
        elif not p_exist and n_exist:
            dir_ = 1
        elif p_exist and not n_exist:
            dir_ = -1

        return dir_

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
                return edge

        edge = Edge(node1, node2, category, id_)
        node1.add_edge(edge)
        node2.add_edge(edge)
        self._graph.add_edge(edge)

        return edge
