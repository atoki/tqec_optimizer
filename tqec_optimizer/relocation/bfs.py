import heapq

from ..graph import Node


class BFS:
    def __init__(self, src, dst, count, grid, used_node_array, size, space, init=False):
        self._src = src
        self._dst = dst
        self._rate = pow(1.05, count)
        self._grid = grid
        self._used_node_array = used_node_array
        self._space = space
        self._size = size
        self._init = init

    def search(self):
        queue = []
        # keyは探索済みノード. valueはその前のノード
        visited_node = {self._src: self._src}
        heapq.heappush(queue, (0, self._src))
        while len(queue) != 0:
            current_node_cost, current_node = heapq.heappop(queue)
            if self.__is_dst_node(current_node):
                break

            for next_node in self.__expand_node(current_node):
                if next_node not in visited_node:
                    visited_node[next_node] = current_node
                    cost = self.__evaluate(current_node_cost, visited_node[current_node], current_node, next_node)
                    heapq.heappush(queue, (cost, next_node))

        route = self.__create_route(visited_node)
        return route

    def __create_route(self, visited_node):
        route = []
        node = self._dst
        self._grid[node.x + self._space][node.y + self._space][node.z + self._space] += 1
        while not self.__is_src_node(node):
            route.append(node)
            node = visited_node[node]
            self._grid[node.x + self._space][node.y + self._space][node.z + self._space] += 1
        route.append(node)
        route.reverse()

        return route

    def __is_src_node(self, node):
        if node.x == self._src.x and node.y == self._src.y and node.z == self._src.z:
            return True

        return False

    def __is_dst_node(self, node):
        if node.x == self._dst.x and node.y == self._dst.y and node.z == self._dst.z:
            return True

        return False

    def __evaluate(self, current_node_cost, previous_node, current_node, next_node):
        if self._init:
            return current_node_cost + 1.0

        point = current_node_cost + 1.0
        t, c = 2.0, 20.0
        # touch -> touch
        if self._grid[previous_node.x + self._space][previous_node.y + self._space][previous_node.z + self._space] > 0.0 \
                and self._grid[current_node.x + self._space][current_node.y + self._space][current_node.z + self._space] > 0.0:
            point += self._rate * t
        # empty -> touch
        elif self._grid[current_node.x + self._space][current_node.y + self._space][current_node.z + self._space] == 0.0 \
                and self._grid[next_node.x + self._space][next_node.y + self._space][next_node.z + self._space] > 0.0:
            point += self._rate * t
        # cross (= empty -> touch -> empty)
        elif self._grid[previous_node.x + self._space][previous_node.y + self._space][previous_node.z + self._space] == 0.0 \
                and self._grid[current_node.x + self._space][current_node.y + self._space][current_node.z + self._space] > 0.0 \
                and self._grid[next_node.x + self._space][next_node.y + self._space][next_node.z + self._space] == 0.0:
            point += self._rate * c

        return point

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


