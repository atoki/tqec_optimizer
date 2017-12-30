import random

from ..position import Position


class SequenceTriple:
    def __init__(self, module_list, permutations=None):
        self._module_list = module_list
        self._permutation1 = [] if permutations is None else permutations[0]
        self._permutation2 = [] if permutations is None else permutations[1]
        self._permutation3 = [] if permutations is None else permutations[2]
        self._candidate_permutation1 = []
        self._candidate_permutation2 = []
        self._candidate_permutation3 = []
        self._placed = [False for no in range(0, 100)]
        # (index, axis)
        self._last_rotate = (0, None)

    def apply(self):
        self._permutation1 = self._candidate_permutation1[:]
        self._permutation2 = self._candidate_permutation2[:]
        self._permutation3 = self._candidate_permutation3[:]

    def recover(self):
        index, axis = self._last_rotate
        if index > 0 and axis is not None:
            rotate_module = self._candidate_permutation1[index]
            rotate_module.rotate(axis)
            rotate_module.rotate(axis)
            rotate_module.rotate(axis)

    def build_permutation(self):
        # prepare
        for module_ in self._module_list:
            self._permutation1.append(module_)
            self._permutation2.append(module_)
            self._permutation3.append(module_)

        # z direction
        self._permutation3.sort(key=lambda m: (m.pos.z, m.pos.x))
        self._permutation2.sort(key=lambda m: (m.pos.z, m.pos.x))
        self._permutation1.sort(key=lambda m: (m.pos.z, m.pos.x))

        # x direction
        self._permutation2.sort(key=lambda m: (m.pos.x, -m.pos.z), reverse=True)

        self._candidate_permutation1 = self._permutation1[:]
        self._candidate_permutation2 = self._permutation2[:]
        self._candidate_permutation3 = self._permutation3[:]

    def recalculate_coordinate(self):
        self._placed = [False for no in range(0, 100)]
        for module_ in self._candidate_permutation3:
            id_ = module_.id
            new_pos = Position(self.__find_x(id_), self.__find_y(id_), self.__find_z(id_))
            module_.set_position(new_pos, True)
            self._placed[id_] = True

        return self._module_list

    def __find_x(self, id_):
        p2_list = set()
        flag = False
        for module_ in self._candidate_permutation2:
            if module_.id == id_:
                flag = True
            if not flag:
                continue
            if self._placed[module_.id]:
                p2_list.add(module_)

        placed_module_list = p2_list
        x = 0
        for module_ in placed_module_list:
            x = max(x, module_.pos.x + module_.width)

        return x

    def __find_y(self, id_):
        p1_list = set()
        p2_list = set()
        flag = False
        for module_ in self._candidate_permutation1:
            if module_.id == id_:
                flag = True
            if not flag:
                continue
            if self._placed[module_.id]:
                p1_list.add(module_)

        for module_ in self._candidate_permutation2:
            if module_.id == id_:
                break
            if self._placed[module_.id]:
                p2_list.add(module_)

        placed_module_list = p1_list & p2_list
        y = 0
        for module_ in placed_module_list:
            y = max(y, module_.pos.y + module_.height)

        return y

    def __find_z(self, id_):
        p1_list = set()
        p2_list = set()
        for module_ in self._candidate_permutation1:
            if module_.id == id_:
                break
            if self._placed[module_.id]:
                p1_list.add(module_)

        for module_ in self._candidate_permutation2:
            if module_.id == id_:
                break
            if self._placed[module_.id]:
                p2_list.add(module_)

        placed_module_list = p1_list & p2_list
        z = 0
        for module_ in placed_module_list:
            z = max(z, module_.pos.z + module_.depth)

        return z

    def create_neighborhood(self):
        """
        SA用の近傍を生成する
        1. swap近傍
        2. shift近傍
        3. rotate近傍
        以上の3つを等確率で一つ採用
        """
        self._candidate_permutation1 = self._permutation1[:]
        self._candidate_permutation2 = self._permutation2[:]
        self._candidate_permutation3 = self._permutation3[:]

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
            self._last_rotate = self.__rotate(self._candidate_permutation1)

    @staticmethod
    def __swap(p1, p2, p3):
        size = len(p1)
        s1 = random.randint(0, size - 1)
        s2 = random.randint(0, size - 1)

        module1, module2 = p1[s1], p1[s2]
        p1_index1, p1_index2 = p1.index(module1), p1.index(module2)
        p2_index1, p2_index2 = p2.index(module1), p2.index(module2)
        p3_index1, p3_index2 = p3.index(module1), p3.index(module2)

        # permutation swap
        p1[p1_index1], p1[p1_index2] = p1[p1_index2], p1[p1_index1]
        p2[p2_index1], p2[p2_index2] = p2[p2_index2], p2[p2_index1]
        p3[p3_index1], p3[p3_index2] = p3[p3_index2], p3[p3_index1]

        return 0, None

    @staticmethod
    def __shift(p1, p2, p3):
        size = len(p1)
        index = random.randint(0, size - 1)
        shift_size1 = random.randint(0, size - 1)
        shift_size2 = random.randint(0, size - 1)
        pair = random.randint(1, 3)

        module_ = p1[index]
        if pair == 1:
            p1_index, p2_index = p1.index(module_), p2.index(module_)
            p1_module, p2_module = p1.pop(p1_index), p2.pop(p2_index)
            p1.insert(p1_index + shift_size1, p1_module)
            p2.insert(p2_index + shift_size2, p2_module)
        elif pair == 2:
            p1_index, p3_index = p1.index(module_), p3.index(module_)
            p1_module, p3_module = p1.pop(p1_index), p3.pop(p3_index)
            p1.insert(p1_index + shift_size1, p1_module)
            p3.insert(p3_index + shift_size2, p3_module)
        else:
            p2_index, p3_index = p2.index(module_), p3.index(module_)
            p2_module, p3_module = p2.pop(p2_index), p3.pop(p3_index)
            p2.insert(p2_index + shift_size1, p2_module)
            p3.insert(p3_index + shift_size2, p3_module)

        return 0, None

    @staticmethod
    def __rotate(p1):
        size = len(p1)
        index = random.randint(0, size - 1)
        axis = random.randint(1, 3)
        rotate_module = p1[index]

        if axis == 1:
            if rotate_module.rotate('X'):
                return index, 'X'
        elif axis == 2:
            if rotate_module.rotate('Y'):
                return index, 'Y'
        else:
            if rotate_module.rotate('Z'):
                return index, 'Z'

        return 0, None
