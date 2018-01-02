import math

from ..vector3d import Vector3D


class Module:
    """
    モジュールクラス
    """
    def __init__(self, module_id):
        """
        コンストラクタ

        :param module_id モジュールを構成する閉路の番号
        """
        self._id = module_id
        self._frame_node_list = []
        self._cross_node_list = []
        self._frame_edge_list = []
        self._cross_edge_list = []
        self._cross_id_list = set()
        self._joint_pair_list = []
        self._pos = Vector3D()
        self._inner_pos = Vector3D()
        self._width = 0
        self._height = 0
        self._depth = 0
        self._inner_width = 0
        self._inner_height = 0
        self._inner_depth = 0

    @property
    def id(self):
        return self._id

    @property
    def pos(self):
        return self._pos

    @property
    def inner_pos(self):
        return self._inner_pos

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
    def inner_width(self):
        return self._inner_width

    @property
    def inner_height(self):
        return self._inner_height

    @property
    def inner_depth(self):
        return self._inner_depth

    @property
    def node_list(self):
        return self._frame_node_list + self._cross_node_list

    @property
    def frame_node_list(self):
        return self._frame_node_list

    @property
    def cross_node_list(self):
        return self._cross_node_list

    @property
    def edge_list(self):
        return self._frame_edge_list + self._cross_edge_list

    @property
    def frame_edge_list(self):
        return self._frame_edge_list

    @property
    def cross_edge_list(self):
        return self._cross_edge_list

    @property
    def cross_id_list(self):
        return self._cross_id_list

    @property
    def joint_pair_list(self):
        return self._joint_pair_list

    def add_frame_node(self, node):
        self._frame_node_list.append(node)

    def add_cross_node(self, node):
        self._cross_node_list.append(node)

    def add_frame_edge(self, edge):
        self._frame_edge_list.append(edge)

    def add_cross_edge(self, edge):
        self._cross_edge_list.append(edge)

    def add_cross_id(self, id_):
        self._cross_id_list.add(id_)

    def add_joint_pair(self, joint_pair):
        self._joint_pair_list.append(joint_pair)

    def set_inner_size(self, inner_width, inner_height, inner_depth):
        self._inner_width = inner_width
        self._inner_height = inner_height
        self._inner_depth = inner_depth

    def set_size(self, width, height, depth):
        self._width = width
        self._height = height
        self._depth = depth

    def set_inner_position(self, inner_position):
        self._inner_pos = inner_position

    def set_position(self, position, replace=False):
        """
        モジュールの座標(左, 下, 手前)を設定する

        :param position 設定する座標
        :param replace 既に作成されたモジュールに新しく設定する場合はTrue
        """
        if replace:
            diff_x = position.x - self._pos.x
            diff_y = position.y - self._pos.y
            diff_z = position.z - self._pos.z

            for node in self._frame_node_list + self._cross_node_list:
                node.move(diff_x, diff_y, diff_z)

            self.update()

        self._pos = position

    def update(self):
        """
        モジュールのサイズを求めて設定する
        """
        min_x = min_y = min_z = math.inf
        max_x = max_y = max_z = -math.inf
        # (x,y,z)が最小となる座標(pos)とモジュールの大きさを計算する
        for node in self._frame_node_list:
            # モジュールの最小、最大値を更新する
            min_x = min(node.x - 1, min_x)
            min_y = min(node.y - 1, min_y)
            min_z = min(node.z - 1, min_z)
            max_x = max(node.x + 1, max_x)
            max_y = max(node.y + 1, max_y)
            max_z = max(node.z + 1, max_z)

        self._inner_pos.set(min_x, min_y, min_z)
        self._inner_width = max_x - min_x
        self._inner_height = max_y - min_y
        self._inner_depth = max_z - min_z

        # (x,y,z)が最小となる座標(pos)とモジュールの大きさを計算する
        for node in self._cross_node_list:
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

    def rotate(self, axis):
        center = Vector3D(self.pos.x + (self.width / 2.0),
                          self.pos.y + (self.height / 2.0),
                          self.pos.z + (self.depth / 2.0))

        if axis == 'X':
            for node in self._frame_node_list + self._cross_node_list:
                rel_x, rel_y, rel_z = node.x - center.x, node.y - center.y, node.z - center.z
                relative_pos = Vector3D(rel_x, rel_y, rel_z)
                relative_pos.set(rel_x, -rel_z, rel_y)
                if self.__invalidate_rotate(rel_x, relative_pos.x):
                    return False
                node.pos.set(relative_pos.x + center.x, relative_pos.y + center.y, relative_pos.z + center.z)
            self.update()
        elif axis == 'Y':
            for node in self._frame_node_list + self._cross_node_list:
                rel_x, rel_y, rel_z = node.x - center.x, node.y - center.y, node.z - center.z
                relative_pos = Vector3D(rel_x, rel_y, rel_z)
                relative_pos.set(rel_z, rel_y, -rel_x)
                if self.__invalidate_rotate(rel_x, relative_pos.x):
                    return False
                node.pos.set(relative_pos.x + center.x, relative_pos.y + center.y, relative_pos.z + center.z)
            self.update()
        else:
            for node in self._frame_node_list + self._cross_node_list:
                rel_x, rel_y, rel_z = node.x - center.x, node.y - center.y, node.z - center.z
                relative_pos = Vector3D(rel_x, rel_y, rel_z)
                relative_pos.set(-rel_y, rel_x, rel_z)
                if self.__invalidate_rotate(rel_x, relative_pos.x):
                    return False
                node.pos.set(relative_pos.x + center.x, relative_pos.y + center.y, relative_pos.z + center.z)
            self.update()

        return True

    @staticmethod
    def __invalidate_rotate(from_, to):
        return from_ % 2 != to % 2

    def debug(self):
        print("--- ", self._id, " ---")
        print("position : (", self._pos.x, ",", self._pos.y, ",", self._pos.z, ")")
        print("width : ", self._width)
        print("height: ", self._height)
        print("depth : ", self._depth)
