import heapq

from ..graph import Node


class BestFirstSearch:
    def __init__(self, src, dst, used_node_array, invalid_edge, size, space):
        self._src = src
        self._dst = dst
        self._used_node_array = used_node_array
        self._invalid_edge = invalid_edge
        self._space = space
        self._size = size

    def search(self):
        first = Node(self._src.x, self._src.y, self._src.z)
        last = Node(self._dst.x, self._dst.y, self._dst.z)

        queue = []
        # keyは探索済みノード. valueはその前のノード
        visited_node = {first: Node(0, 0, 0)}
        heapq.heappush(queue, (0, first))
        while len(queue) != 0:
            current_node_cost, current_node = heapq.heappop(queue)
            if self.__is_dst_node(current_node):
                break

            for next_node in self.__expand_node(current_node):
                if next_node not in visited_node:
                    visited_node[next_node] = current_node
                    heapq.heappush(queue, (current_node_cost + 1, next_node))

        route = []
        node = last
        while not self.__is_src_node(node):
            route.insert(0, node)
            node = visited_node[node]
        route.insert(0, node)

        return route

    def __is_src_node(self, node):
        if node.x == self._src.x and node.y == self._src.y and node.z == self._src.z:
            return True

        return False

    def __is_dst_node(self, node):
        if node.x == self._dst.x and node.y == self._dst.y and node.z == self._dst.z:
            return True

        return False

    def __expand_node(self, node):
        expanded_nodes = []
        dx = [2, 0, -2, 0, 0, 0]
        dy = [0, 2, 0, -2, 0, 0]
        dz = [0, 0, 0, 0, 2, -2]

        for i in range(6):
            next_node = Node(node.x + dx[i], node.y + dy[i], node.z + dz[i])
            if not self.__is_prohibit(node, next_node):
                expanded_nodes.append(next_node)

        return expanded_nodes

    def __is_prohibit(self, current_node, next_node):
        if current_node in self._invalid_edge and next_node == self._invalid_edge[current_node]:
            return True

        if next_node.x < -self._space or next_node.x > self._size[0] \
                or next_node.y < -self._space or next_node.y > self._size[1] \
                or next_node.z < -self._space or next_node.z > self._size[2]:
            return True

        edge_x = int((current_node.x + next_node.x) / 2)
        edge_y = int((current_node.y + next_node.y) / 2)
        edge_z = int((current_node.z + next_node.z) / 2)
        if self._used_node_array[edge_x + self._space][edge_y + self._space][edge_z + self._space]:
            return True

        if self._dst.x == next_node.x and self._dst.y == next_node.y and self._dst.z == next_node.z:
            return False

        if self._used_node_array[next_node.x + self._space][next_node.y + self._space][next_node.z + self._space]:
            return True

        return False


