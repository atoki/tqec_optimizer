from .position import Position


class Node:
    def __init__(self, type, x, y, z):
        self._ids = []
        self._type = type
        self._pos = Position(x, y, z)

    def add_id(self, id):
        self._ids.append(id)

    def set_type(self, type):
        self._type = type

    @property
    def type(self):
        return self._type

    @property
    def pos(self):
        return self._pos

    @property
    def x(self):
        return self._pos.x

    @property
    def y(self):
        return self._pos.y

    @property
    def z(self):
        return self._pos.z

    def debug(self):
        print("(", self._type, ",", self._pos.x, ",", self._pos.y, ",", self._pos.z, ")")


class Edge:
    def __init__(self, node1, node2, category):
        self._ids = []
        self._type = node1.type
        self._category = category
        self._node1 = node1
        self._node2 = node2

    def add_id(self, id):
        self._ids.append(id)

    def set_type(self, type):
        self._type = type

    @property
    def type(self):
        return self._type

    @property
    def category(self):
        return self._category

    @property
    def node1(self):
        return self._node1

    @property
    def node2(self):
        return self._node2

    def alt_node(self, node):
        if node == self._node1:
            return self._node2
        elif node == self._node2:
            return self._node1
        else:
            assert False

    def debug(self):
        print("type:", self._node1.type, " (", self._node1.x, ",", self._node1.y, ",", self._node1.z, ")", end=" -> ")
        print("(", self._node2.x, ",", self._node2.y, ",", self._node2.z, ")")


class Graph:
    """
    TQEC回路をグラフ問題として定式化する
    座標系はtqec_viewerに準拠(=OpenGL(右手座標系))
    """
    def __init__(self, circuit, space):
        """
        コンストラクタ

        :param circuit Circuit
        :param space 座標系において余分に確保する空間長
        """

        self._circuit = circuit
        self._space = space
        self._max_x = len(circuit._cnots) * 2 + space
        self._min_x = 0 - space
        self._max_y = 3 + space
        self._min_y = -1 - space
        self._max_z = len(circuit._bits) * 2 - 1 + space
        self._min_z = -1 - space

        self.__create()

    def __create(self):
        self._node_list = []
        self._edge_list = []

        self.__create_bit_lines()
        self.__create_bridges()
        self.__create_injectors()
        self.__create_braidings()

    def __create_bit_lines(self):
        """
        primal型 defect
        初期回路のグラフ化に使用
        """
        upper = 2
        lower = 0
        type = "primal"
        print("width: ", self._circuit.width)
        print("length:", self._circuit.length)
        for z in range(0, self._circuit.width, 2):
            last_upper_node = None
            last_lower_node = None
            for x in range(0, self._circuit.length + 1, 2):
                upper_node = self.__new_node(type, x, upper, z)
                lower_node = self.__new_node(type, x, lower, z)
                if last_upper_node is not None or last_lower_node is not None:
                    self.__new__edge(upper_node, last_upper_node, "edge")
                    self.__new__edge(lower_node, last_lower_node, "edge")
                last_upper_node = upper_node
                last_lower_node = lower_node

    def __create_bridges(self):
        """
        初期化と観測の追加
        初期回路のグラフ化に使用
        """
        type = "primal"
        for init in self._circuit.initializations:
            node1 = self.__new_node(type, 0, 0, init["bit"] * 2)
            node2 = self.__new_node(type, 0, 2, init["bit"] * 2)
            self.__new__edge(node1, node2, "bridge")

        for meas in self._circuit.measurements:
            node1 = self.__new_node(type, self._circuit.length, 0, meas["bit"] * 2)
            node2 = self.__new_node(type, self._circuit.length, 2, meas["bit"] * 2)
            self.__new__edge(node1, node2, "bridge")

    def __create_injectors(self):
        """
        インジェクタと外部入出力の追加
        初期回路のグラフ化に使用
        """
        type = "primal"
        for z in self._circuit.inputs:
            node1 = self.__new_node(type, 0, 0, z * 2)
            node2 = self.__new_node(type, 0, 2, z * 2)
            self.__new__edge(node1, node2, "cap")

        for z in self._circuit.outputs:
            node1 = self.__new_node(type, self._circuit.length, 0, z * 2)
            node2 = self.__new_node(type, self._circuit.length, 2, z * 2)
            self.__new__edge(node1, node2, "cap")

    def __create_braidings(self):
        """
        ブレイディング(Controlled NOT)の追加
        初期回路のグラフ化に使用
        左回りに作る

        """

        type = "dual"
        space = 2
        for no, cnot in enumerate(self._circuit.cnots):
            node_array = []
            tbit_no_array = cnot["targets"]
            cbit_no = cnot["control"]
            bit_no_array = tbit_no_array
            bit_no_array.append(cbit_no)
            max_bit_no = max(bit_no_array)
            min_bit_no = min(bit_no_array)
            d = 1.0 if (cbit_no < tbit_no_array[0]) else -1.0

            # add bridge
            upper = Node("primal", no * 4 + 2, 2, cbit_no * 2)
            lower = Node("primal", no * 4 + 2, 0, cbit_no * 2)
            self.__new__edge(upper, lower, "bridge")

            node = self.__new_node(type, no * 4 + 2 - d, 1, cbit_no * 2 - 1 * d)
            node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
            node.pos.incz(space * d)
            node_array.append(self.__new_node(node.type, node.x, node.y, node.z))

            start = min_bit_no if (cbit_no < tbit_no_array[0]) else max_bit_no
            z = start + 1 * d
            limit = max_bit_no if (cbit_no < tbit_no_array[0]) else min_bit_no
            while z != limit + 1 * d:
                if z in tbit_no_array:
                    if node.y != 1:
                        node.pos.decy(space)
                        node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
                    node.pos.incz(space * d)
                    node_array.append(self.__new_node(node.type, node.x, node.y, node.z))

                else:
                    if node.y == 1:
                        node.pos.incy(space)
                        node_array.append(self.__new_node(node.type, node.x, node.y, node.z))

                    node.pos.incz(space * d)
                    node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
                z += 1 * d

            node.pos.incy(space)
            node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
            node.pos.incx(space * d)
            node_array.append(self.__new_node(node.type, node.x, node.y, node.z))

            z = max_bit_no if (cbit_no < tbit_no_array[0]) else min_bit_no
            while z != cbit_no:
                node.pos.decz(space * d)
                node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
                z -= 1 * d

            node.pos.decy(space)
            node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
            node.pos.decz(space * d)
            node_array.append(self.__new_node(node.type, node.x, node.y, node.z))

            first_node = node_array[0]
            last_node = None
            for node in node_array:
                if last_node is not None:
                    self.__new__edge(node, last_node, "edge")
                last_node = node
            self.__new__edge(first_node, last_node, "edge")

    @property
    def node_list(self):
        return self._node_list

    @property
    def edge_list(self):
        return self._edge_list

    def __new_node(self, type, x, y, z):
        node = Node(type, x, y, z)
        self._node_list.append(node)

        return node

    def __new__edge(self, node1, node2, category):
        edge = Edge(node1, node2, category)
        self.edge_list.append(edge)

        return edge

    def debug(self):
        for node in self._node_list:
            node.debug()

        for edge in self._edge_list:
            edge.debug()

