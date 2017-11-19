import heapq

from ..graph import Node


class BestFirstSearch:
    def __init__(self, src, dst, used_node_array, size, space):
        self._src = src
        self._dst = dst
        self._used_node_array = used_node_array
        self._space = space
        self._size = size

    def search(self):
        first = Node(0, "first", self._src.x, self._src.y, self._src.z)
        last = Node(0, "last", self._dst.x, self._dst.y, self._dst.z)

        queue = []
        # keyは探索済みノード. valueはその前のノード
        visited_node = {first: Node(-1, self._src.type, 0, 0, 0)}
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
            next_node = Node(0, self._src.type, node.x + dx[i], node.y + dy[i], node.z + dz[i])
            if not self.__is_prohibit(next_node):
                expanded_nodes.append(next_node)

        return expanded_nodes

    def __is_prohibit(self, node):
        if self._dst.x == node.x and self._dst.y == node.y and self._dst.z == node.z:
            return False

        if node.x < -self._space or node.x > self._size[0] \
                or node.y < -self._space or node.y > self._size[1] \
                or node.z < -self._space or node.z > self._size[2]:
            return True

        if self._used_node_array[node.x + self._space][node.y + self._space][node.z + self._space]:
            return True

        return False

