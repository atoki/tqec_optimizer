class NeighborhoodGenerator:
    def generator(self):
        pass


class SwapNeighborhoodGenerator(NeighborhoodGenerator):
    def __init__(self, permutations):
        self._permutation1 = permutations[0]
        self._permutation2 = permutations[1]
        self._permutation3 = permutations[2]

    def generator(self):
        permutations_list = []
        for s1 in range(len(self._permutation1)):
            for s2 in range(s1, len(self._permutation1)):
                permutations_list.append(self.__swap(s1, s2))

        return permutations_list

    def __swap(self, s1, s2):
        module1, module2 = self._permutation1[s1], self._permutation1[s2]
        p1_index1, p1_index2 = self._permutation1.index(module1), self._permutation1.index(module2)
        p2_index1, p2_index2 = self._permutation2.index(module1), self._permutation2.index(module2)
        p3_index1, p3_index2 = self._permutation3.index(module1), self._permutation3.index(module2)

        p1 = self._permutation1[:]
        p2 = self._permutation2[:]
        p3 = self._permutation3[:]

        # permutation swap
        p1[p1_index1], p1[p1_index2] = p1[p1_index2], p1[p1_index1]
        p2[p2_index1], p2[p2_index2] = p2[p2_index2], p2[p2_index1]
        p3[p3_index1], p3[p3_index2] = p3[p3_index2], p3[p3_index1]

        return p1, p2, p3


class ShiftNeighborhoodGenerator(NeighborhoodGenerator):
    def __init__(self, permutations):
        self._permutation1 = permutations[0]
        self._permutation2 = permutations[1]
        self._permutation3 = permutations[2]

    def generator(self):
        permutations_list = []
        for index in range(len(self._permutation1)):
            for shift_size1 in range(len(self._permutation1)):
                for shift_size2 in range(len(self._permutation1)):
                    permutations_list.append(self.__shift(index, shift_size1, shift_size2, 12))
                    permutations_list.append(self.__shift(index, shift_size1, shift_size2, 13))
                    permutations_list.append(self.__shift(index, shift_size1, shift_size2, 23))

        return permutations_list

    def __shift(self, index, shift_size1, shift_size2, targets):
        p1 = self._permutation1[:]
        p2 = self._permutation2[:]
        p3 = self._permutation3[:]

        module_ = self._permutation1[index]
        if targets == 12:
            p1_index, p2_index = self._permutation1.index(module_), self._permutation2.index(module_)
            p1_module, p2_module = p1.pop(p1_index), p2.pop(p2_index)
            p1.insert(p1_index + shift_size1, p1_module)
            p2.insert(p2_index + shift_size2, p2_module)
        elif targets == 13:
            p1_index, p3_index = self._permutation1.index(module_), self._permutation3.index(module_)
            p1_module, p3_module = p1.pop(p1_index), p3.pop(p3_index)
            p1.insert(p1_index + shift_size1, p1_module)
            p3.insert(p3_index + shift_size2, p3_module)
        else:
            p2_index, p3_index = self._permutation2.index(module_), self._permutation3.index(module_)
            p2_module, p3_module = p2.pop(p2_index), p3.pop(p3_index)
            p2.insert(p2_index + shift_size1, p2_module)
            p3.insert(p3_index + shift_size2, p3_module)

        return p1, p2, p3
