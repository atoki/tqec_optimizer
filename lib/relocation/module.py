import math

from ..position import Position


class Module:
    def __init__(self, loop_id):
        self._id = loop_id
        self._edge_list = []
        self._cross_edge_list = []
        self._pos = Position()
        self._width = 0
        self._height = 0
        self._depth = 0

    @property
    def id(self):
        return self._id

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def depth(self):
        return self._depth

    @property
    def edge_list(self):
        return self._edge_list

    @property
    def cross_edge_list(self):
        return self._cross_edge_list

    def add_edge(self, edge):
        self._edge_list.append(edge)

    def add_cross_edge(self, edge):
        self._cross_edge_list.append(edge)

    def set_size(self, width, height, depth):
        self._width = width
        self._height = height
        self._depth = depth

    def set_position(self, position):
        self._pos = position

    def update(self):
        min_x = min_y = min_z = math.inf
        max_x = max_y = max_z = -math.inf
        # (x,y,z)が最小となる座標(pos)とモジュールの大きさを計算する
        for edge in self._edge_list + self._cross_edge_list:
            for n in range(0, 2):
                node = edge.node1 if n == 1 else edge.node2

                # モジュールの最小、最大値を更新する
                min_x = min(node.x, min_x)
                min_y = min(node.y, min_y)
                min_z = min(node.z, min_z)
                max_x = max(node.x, max_x)
                max_y = max(node.y, max_y)
                max_z = max(node.z, max_z)

        # モジュールと座標とサイズの更新
        self._pos.set(min_x, min_y, min_z)
        self._width = max_x - min_x
        self._height = max_y - min_y
        self._depth = max_z - min_z

    def debug(self):
        print("--- ", self._id, " ---")
        print("position : (", self._pos.x, ",", self._pos.y, ",", self._pos.z, ")")
        print("width : ", self._width)
        print("height: ", self._height)
        print("depth : ", self._depth)
