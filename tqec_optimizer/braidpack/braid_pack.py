import math

from ..vector3d import Vector3D, Size


class Braidpack:
    def __init__(self, graph):
        self._graph = graph
        self._size = self.__create_size()

        self.__delete_not_closed()

    def execute(self):
        return self._graph

    def __compress(self):
        """
        Z軸方向に圧縮する
        """
        for z in range(2, self._size.z + 1):
            for node in self._graph.node_list:
                if node.z == z and self.__can_move(node):
                    node.pos.decz(2)

    def __can_move(self, node):
        next_pos = Vector3D(node.x, node.y, node.z - 2)
        for node in self._graph.node_list:
            if node.x == next_pos.x and node.y == next_pos.y and node.z == next_pos.z:
                return False

        return True

    def __create_size(self):
        max_x = max_y = max_z = -math.inf
        for node in self._graph.node_list:
            max_x = max(node.x, max_x)
            max_y = max(node.y, max_y)
            max_z = max(node.z, max_z)

        return Size(max_x, max_y, max_z)

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
            for edge in self._graph.node_list[index].edge_list:
                if not edge.is_injector():
                    del self._graph.node_list[index]
