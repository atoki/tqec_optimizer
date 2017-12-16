class LocalSearch:
    def __init__(self, route_list, invalidate_pair):
        self._route = route_list
        self._invalidate_pair = invalidate_pair
        self._dist_table = {}

        self.__create_dist_table()

    def execute(self):
        size = len(self._route)
        if size == 2:
            route = {self._route[0]: self._route[1]}
            return route

        while True:
            improved = self.__opt2()
            if not improved:
                break

        route = {}
        for index in range(0, size - 1):
            if self._invalidate_pair[self._route[index]] == self._route[index + 1]:
                continue
            route[self._route[index]] = self._route[index + 1]
        if self._invalidate_pair[self._route[size - 1]] != self._route[0]:
            route[self._route[size - 1]] = self._route[0]

        return route

    def __opt2(self):
        size = len(self._route)
        cost_diff_best = 0.0
        i_best, j_best = None, None

        for i in range(0, size - 2):
            for j in range(i + 2, size):
                if i == 0 and j == size - 1:
                    continue

                if self._invalidate_pair[self._route[i]] == self._route[int((i + 1) % size)] \
                        or self._invalidate_pair[self._route[j]] == self._route[int((j + 1) % size)]:
                    continue

                cost_diff = self.__calculate_exchange_cost(i, j)

                if cost_diff < cost_diff_best:
                    cost_diff_best = cost_diff
                    i_best, j_best = i, j

        if cost_diff_best < 0.0:
            self.__apply_exchange(i_best, j_best)
            return True
        else:
            return False

    def __calculate_exchange_cost(self, i, j):
        size = len(self._route)
        a, b = i, int((i + 1) % size)
        c, d = j, int((j + 1) % size)

        cost_before = self._dist_table[(self._route[a], self._route[b])] \
                        + self._dist_table[(self._route[c], self._route[d])]
        cost_after = self._dist_table[(self._route[a], self._route[c])] \
                        + self._dist_table[(self._route[b], self._route[d])]

        return cost_after - cost_before

    def __apply_exchange(self, i, j):
        tmp = self._route[i + 1: j + 1]
        tmp.reverse()
        self._route[i + 1: j + 1] = tmp

    def __create_dist_table(self):
        size = len(self._route)
        for i in range(0, size):
            for j in range(i, size):
                if i == j:
                    continue
                else:
                    dist = self._route[i].dist(self._route[j])
                    self._dist_table[(self._route[i], self._route[j])] = dist
                    self._dist_table[(self._route[j], self._route[i])] = dist


