from .position import Position


class Node:
    """
    ノードクラス
    """
    def __init__(self, x, y, z, id_=0, type_="none"):
        """
        コンストラクタ

        :param x X座標
        :param y Y座標
        :param z Z座標
        :param id_ ノード番号
        :param type_ primal or dual
        """
        self._id = id_
        self._type = type_
        self._pos = Position(x, y, z)
        self._edge_list = []
        self._color = 0

    def __lt__(self, other):
        return self.id < other.id

    def __gt__(self, other):
        return self.id > other.id

    def __hash__(self):
        return hash((self._pos.x, self._pos.y, self._pos.z))

    def __eq__(self, other):
        return (self._id, self._pos.x, self._pos.y, self._pos.z) == (other.id, other.x, other.y, other.z)

    def set_type(self, type_):
        self._type = type_

    def add_edge(self, edge):
        self._edge_list.append(edge)

    def set_color(self, color):
        self._color = color

    def move(self, diff_x, diff_y, diff_z):
        self._pos.incx(diff_x)
        self._pos.incy(diff_y)
        self._pos.incz(diff_z)

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def color(self):
        return self._color

    @property
    def pos(self):
        return self._pos

    @property
    def x(self):
        return int(self._pos.x)

    @property
    def y(self):
        return int(self._pos.y)

    @property
    def z(self):
        return int(self._pos.z)

    @property
    def edge_list(self):
        return self._edge_list

    def debug(self):
        print("type: {} id: {} ({}, {}, {})".format(self._type, self._id, self._pos.x, self._pos.y, self._pos.z))