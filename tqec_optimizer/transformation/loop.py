import math

from ..vector3d import Vector3D


class Loop:
    """
    ループクラス
    """
    def __init__(self, loop_id):
        """
        コンストラクタ

        :param loop_id モジュールを構成する閉路の番号
        """
        self._id = loop_id
        self._pos = Vector3D()
        self._width = 0
        self._height = 0
        self._depth = 0
        self._edge_list = []
        self._cross_list = []
        self._cap_list = []
        self._pin_list = []
        self._injector_list = []

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._edge_list[0].node1.type

    @property
    def pos(self):
        return self._pos

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
    def cross_list(self):
        return self._cross_list

    @property
    def cap_list(self):
        return self._cap_list

    @property
    def pin_list(self):
        return self._pin_list

    @property
    def injector_list(self):
        return self._injector_list

    def set_id(self, id_):
        for edge in self._edge_list:
            edge.set_id(id_)

    def add_edge(self, edge):
        self._edge_list.append(edge)

    def add_cross(self, cross_loop_id):
        if cross_loop_id in self._cross_list:
            self._cross_list.remove(cross_loop_id)
        else:
            self._cross_list.append(cross_loop_id)

    def add_cap(self, cap):
        self._cap_list.append(cap)

    def add_pin(self, pin):
        self._pin_list.append(pin)

    def add_injector(self, injector):
        self._injector_list.append(injector)
        if injector.category == "cap":
            self.add_cap(injector)
        else:
            self.add_pin(injector)

    def remove_cross(self, cross_loop_id):
        self._cross_list.remove(cross_loop_id)

    def shift_injector(self, category):
        """
        他のループからインジェクターを移動させてくる
        移す場所は適当

        :param category 移動させるピンの種類
        """
        candidate_edge = self._edge_list[0]
        for edge in self._edge_list:
            if edge.is_injector():
                continue

            if edge.z > candidate_edge.z:
                candidate_edge = edge

            if edge.z == candidate_edge.z:
                if edge.x < candidate_edge.x:
                    candidate_edge = edge

        candidate_edge.set_category(category)
        self.add_injector(candidate_edge)

    def update(self):
        """
        モジュールのサイズを求めて設定する
        """
        min_x = min_y = min_z = math.inf
        max_x = max_y = max_z = -math.inf
        # (x,y,z)が最小となる座標(pos)とモジュールの大きさを計算する
        for edge in self._edge_list:
            for n in range(0, 2):
                node = edge.node1 if n == 1 else edge.node2

                # モジュールの最小、最大値を更新する
                min_x = min(node.x, min_x)
                min_y = min(node.y, min_y)
                min_z = min(node.z, min_z)
                max_x = max(node.x, max_x)
                max_y = max(node.y, max_y)
                max_z = max(node.z, max_z)

        self._pos.set(min_x, min_y, min_z)
        self._width = max_x - min_x
        self._height = max_y - min_y
        self._depth = max_z - min_z

    def dump(self):
        print("-----  loop id: {} -----".format(self._id))
        print("type          = {}".format(self._edge_list[0].node1.type))
        print("edge list     = {}".format(len(self._edge_list)))
        print("cross list    = {}".format(len(self._cross_list)))
        print("injector list = {}".format(len(self._injector_list)))
        print("position : (", self._pos.x, ",", self._pos.y, ",", self._pos.z, ")")
        print("width : ", self._width)
        print("height: ", self._height)
        print("depth : ", self._depth)
