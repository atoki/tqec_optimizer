import random

from ..vector3d import Vector3D


class SequenceTriple:
    def __init__(self, module_list=None):
        self._module_list = [] if module_list is None else module_list
        self._permutation1 = []
        self._permutation2 = []
        self._permutation3 = []
        self._candidate_permutation1 = []
        self._candidate_permutation2 = []
        self._candidate_permutation3 = []
        self._placed = [False for no in range(0, 100)]
        self._last_rotate = 0, None

        self._module_map = {}
        for module_ in module_list:
            self._module_map[module_.id] = module_

    def set_module_list(self, module_list):
        self._module_list = module_list

    def result(self):
        self._placed = [False for no in range(0, 100)]
        for id_ in self._permutation3:
            new_pos = Vector3D(self.__find_x(id_, self._permutation2),
                               self.__find_y(id_, self._permutation1, self._permutation2),
                               self.__find_z(id_, self._permutation1, self._permutation2))
            self._module_map[id_].set_position(new_pos, True)
            self._placed[id_] = True

        return self._module_list

    def apply(self):
        self._permutation1 = self._candidate_permutation1[:]
        self._permutation2 = self._candidate_permutation2[:]
        self._permutation3 = self._candidate_permutation3[:]

    def recover(self):
        self._candidate_permutation1 = self._permutation1[:]
        self._candidate_permutation2 = self._permutation2[:]
        self._candidate_permutation3 = self._permutation3[:]

        if self._last_rotate is None:
            return

        index, axis = self._last_rotate
        if index > 0 and axis is not None:
            id_ = self._candidate_permutation1[index]
            rotate_module = self._module_map[id_]
            rotate_module.rotate(axis)
            rotate_module.rotate(axis)
            rotate_module.rotate(axis)

    def build_permutation(self):
        # prepare
        for module_ in self._module_list:
            self._permutation1.append(module_.id)
            self._permutation2.append(module_.id)
            self._permutation3.append(module_.id)

        # z direction
        self._permutation3.sort(key=lambda m: (self._module_map[m].pos.z, self._module_map[m].pos.x))
        self._permutation2.sort(key=lambda m: (self._module_map[m].pos.z, self._module_map[m].pos.x))
        self._permutation1.sort(key=lambda m: (self._module_map[m].pos.z, self._module_map[m].pos.x))

        # x direction
        self._permutation2.sort(key=lambda m: (self._module_map[m].pos.x, -self._module_map[m].pos.z), reverse=True)

        self._candidate_permutation1 = self._permutation1[:]
        self._candidate_permutation2 = self._permutation2[:]
        self._candidate_permutation3 = self._permutation3[:]

    def recalculate_coordinate(self):
        self._placed = [False for no in range(0, 100)]
        for id_ in self._candidate_permutation3:
            new_pos = Vector3D(self.__find_x(id_, self._candidate_permutation2),
                               self.__find_y(id_, self._candidate_permutation1, self._candidate_permutation2),
                               self.__find_z(id_, self._candidate_permutation1, self._candidate_permutation2))
            self._module_map[id_].set_position(new_pos, True)
            self._placed[id_] = True

        return self._module_list

    def create_neighborhood(self):
        """
        SA用の近傍を生成する
        1. swap近傍
        2. shift近傍
        3. rotate近傍
        以上の3つを等確率で一つ採用
        """
        strategy = random.randint(1, 3)
        if strategy == 1:
            self._last_rotate = self.__swap(self._candidate_permutation1,
                                            self._candidate_permutation2,
                                            self._candidate_permutation3)
        elif strategy == 2:
            self._last_rotate = self.__shift(self._candidate_permutation1,
                                             self._candidate_permutation2,
                                             self._candidate_permutation3)
        else:
            size = len(self._candidate_permutation1)
            index = random.randint(0, size - 1)
            id_ = self._candidate_permutation1[index]
            rotate_module = self._module_map[id_]
            rotate = self.__rotate(rotate_module)
            self._last_rotate = (index, rotate)

    @staticmethod
    def __swap(p1, p2, p3):
        size = len(p1)
        s1 = random.randint(0, size - 1)
        s2 = random.randint(0, size - 1)

        id1, id2 = p1[s1], p1[s2]
        p1_index1, p1_index2 = p1.index(id1), p1.index(id2)
        p2_index1, p2_index2 = p2.index(id1), p2.index(id2)
        p3_index1, p3_index2 = p3.index(id1), p3.index(id2)

        # permutation swap
        p1[p1_index1], p1[p1_index2] = p1[p1_index2], p1[p1_index1]
        p2[p2_index1], p2[p2_index2] = p2[p2_index2], p2[p2_index1]
        p3[p3_index1], p3[p3_index2] = p3[p3_index2], p3[p3_index1]

        return 0, None

    @staticmethod
    def __shift(p1, p2, p3):
        size = len(p1)
        index = random.randint(0, size - 1)
        shift_size1 = random.randint(1, size - 1)
        shift_size2 = random.randint(1, size - 1)
        pair = random.randint(1, 3)

        id_ = p1[index]
        if pair == 1:
            p1_index, p2_index = p1.index(id_), p2.index(id_)
            p1_id, p2_id = p1.pop(p1_index), p2.pop(p2_index)
            p1.insert(p1_index + shift_size1, p1_id)
            p2.insert(p2_index + shift_size2, p2_id)
        elif pair == 2:
            p1_index, p3_index = p1.index(id_), p3.index(id_)
            p1_id, p3_id = p1.pop(p1_index), p3.pop(p3_index)
            p1.insert(p1_index + shift_size1, p1_id)
            p3.insert(p3_index + shift_size2, p3_id)
        else:
            p2_index, p3_index = p2.index(id_), p3.index(id_)
            p2_id, p3_id = p2.pop(p2_index), p3.pop(p3_index)
            p2.insert(p2_index + shift_size1, p2_id)
            p3.insert(p3_index + shift_size2, p3_id)

            return 0, None

    @staticmethod
    def __rotate(rotate_module):
        axis = random.randint(1, 3)

        if axis == 1:
            if rotate_module.rotate('X'):
                return 'X'
        elif axis == 2:
            if rotate_module.rotate('Y'):
                return 'Y'
        else:
            if rotate_module.rotate('Z'):
                return 'Z'

        return None

    def __find_x(self, target_id, p2):
        p2_list = set()
        flag = False
        for id_ in p2:
            if id_ == target_id:
                flag = True
            if not flag:
                continue
            if self._placed[id_]:
                p2_list.add(id_)

        placed_module_list = p2_list
        x = 0
        for id_ in placed_module_list:
            module_ = self._module_map[id_]
            x = max(x, module_.pos.x + module_.width)

        return x

    def __find_y(self, target_id, p1, p2):
        p1_list = set()
        p2_list = set()
        flag = False
        for id_ in p1:
            if id_ == target_id:
                flag = True
            if not flag:
                continue
            if self._placed[id_]:
                p1_list.add(id_)

        for id_ in p2:
            if id_ == target_id:
                break
            if self._placed[id_]:
                p2_list.add(id_)

        placed_module_list = p1_list & p2_list
        y = 0
        for id_ in placed_module_list:
            module_ = self._module_map[id_]
            y = max(y, module_.pos.y + module_.height)

        return y

    def __find_z(self, target_id, p1, p2):
        p1_list = set()
        p2_list = set()
        for id_ in p1:
            if id_ == target_id:
                break
            if self._placed[id_]:
                p1_list.add(id_)

        for id_ in p2:
            if id_ == target_id:
                break
            if self._placed[id_]:
                p2_list.add(id_)

        placed_module_list = p1_list & p2_list
        z = 0
        for id_ in placed_module_list:
            module_ = self._module_map[id_]
            z = max(z, module_.pos.z + module_.depth)

        return z
