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
        self._max_x = len(circuit._bits) * 2 - 1 + space
        self._min_x = -1 - space
        self._max_y = 3 + space
        self._min_y = -1 - space
        self._max_z = len(circuit._operations) * 2 + space
        self._min_z = 0 - space
        self.__create()

    def __create(self):
        self._node_list = []
        self._edge_list = []

        self.__create_bit_lines()
        self.__create_bridges()
        self.__create_injectors()
        self.__create_operations()

    def __create_bit_lines(self):
        """
        primal型 qubit defect pair
        初期回路のグラフ化に使用
        """
        upper = 2
        lower = 0
        type = "primal"
        print("width: ", self._circuit.width)
        print("length:", self._circuit.length)

        # prepare controlled not operation
        cnots = []
        for operation in self._circuit.operations:
            if operation["type"] == "cnot":
                cnots.append(operation)

        for x in range(0, self._circuit.width, 2):
            last_upper_node = None
            last_lower_node = None
            for z in range(0, self._circuit.length + 1, 2):

                # CNOTの箇所は切断する
                skip = False
                for no, cnot in enumerate(cnots):
                    if x == cnot["control"] * 2 and z == no * 6 + 4:
                        skip = True

                upper_node = self.__new_node(type, x, upper, z)
                lower_node = self.__new_node(type, x, lower, z)
                if last_upper_node is not None or last_lower_node is not None:
                    if not skip:
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
            if init["type"] == "z":
                node1 = self.__new_node(type, init["bit"] * 2, 0, 0)
                node2 = self.__new_node(type, init["bit"] * 2, 2, 0)
                self.__new__edge(node1, node2, "bridge")

        for meas in self._circuit.measurements:
            if meas["type"] == "z":
                node1 = self.__new_node(type, meas["bit"] * 2, 0, self._circuit.length)
                node2 = self.__new_node(type, meas["bit"] * 2, 2, self._circuit.length)
                self.__new__edge(node1, node2, "bridge")
            else:
                upper_node1 = Node(type, meas["bit"] * 2, 2, self._circuit.length)
                lower_node1 = Node(type, meas["bit"] * 2, 0, self._circuit.length)
                upper_node2 = self.__new_node(type, meas["bit"] * 2, 2, self._circuit.length + 2)
                lower_node2 = self.__new_node(type, meas["bit"] * 2, 0, self._circuit.length + 2)
                self.__new__edge(upper_node1, upper_node2, "line")
                self.__new__edge(lower_node1, lower_node2, "line")


    def __create_injectors(self):
        """
        外部入出力の追加
        初期回路のグラフ化に使用
        """
        type = "primal"
        for x in self._circuit.inputs:
            node1 = self.__new_node(type, x * 2, 0, 0)
            node2 = self.__new_node(type, x * 2, 2, 0)
            self.__new__edge(node1, node2, "cap")

        for x in self._circuit.outputs:
            node1 = self.__new_node(type, x * 2, 0, self._circuit.length)
            node2 = self.__new_node(type, x * 2, 2, self._circuit.length)
            self.__new__edge(node1, node2, "cap")

    def __create_operations(self):
        """
        CNOTとState Injectionを追加する
        初期回路のグラフ化に使用
        """
        no = 0
        for operation in self._circuit.operations:
            if operation["type"] == "cnot":
                self.__create_braidings(no, operation)
                no += 1
            else:
                self.__create_state_injection(no, operation)

    def __create_state_injection(self, no, operation):
        """
        State Injectionの追加
        初期回路のグラフ化に使用
        """
        type = "primal"
        node1 = Node(type, operation["target"] * 2, 0, no * 6)
        node2 = Node(type, operation["target"] * 2, 2, no * 6)
        self.__new__edge(node1, node2, "pin")

    def __create_braidings(self, no, cnot):
        """
        ブレイディング(Controlled NOT)の追加
        初期回路のグラフ化に使用
        左回りに作る
        """

        type = "dual"
        # ノード間の距離
        space = 2
        node_array = []
        tbit_no_array = cnot["targets"]
        cbit_no = cnot["control"]
        bit_no_array = tbit_no_array
        bit_no_array.append(cbit_no)
        max_bit_no = max(bit_no_array)
        min_bit_no = min(bit_no_array)
        d = 1.0 if (cbit_no < tbit_no_array[0]) else -1.0

        # ループを閉じる為のEdgeを作成
        upper = Node("primal", cbit_no * space, 2, no * 6 + 3 - 1)
        lower = Node("primal", cbit_no * space, 0, no * 6 + 3 - 1)
        self.__new__edge(upper, lower, "line")

        upper = Node("primal", cbit_no * space, 2, no * 6 + 3 + 1)
        lower = Node("primal", cbit_no * space, 0, no * 6 + 3 + 1)
        self.__new__edge(upper, lower, "line")

        node = self.__new_node(type, cbit_no * space - 1 * d, 1, no * 6 + 3 - space * d)
        node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
        node.pos.incx(space * d)
        node_array.append(self.__new_node(node.type, node.x, node.y, node.z))

        start = min_bit_no if (cbit_no < tbit_no_array[0]) else max_bit_no
        x = start + 1 * d
        limit = max_bit_no if (cbit_no < tbit_no_array[0]) else min_bit_no
        while x != limit + 1 * d:
            if x in tbit_no_array:
                if node.y != 1:
                    node.pos.decy(space)
                    node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
                node.pos.incx(space * d)
                node_array.append(self.__new_node(node.type, node.x, node.y, node.z))

            else:
                if node.y == 1:
                    node.pos.incy(space)
                    node_array.append(self.__new_node(node.type, node.x, node.y, node.z))

                node.pos.incx(space * d)
                node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
            x += 1 * d

        node.pos.incy(space)
        node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
        node.pos.incz(space * d)
        node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
        node.pos.incz(space * d)
        node_array.append(self.__new_node(node.type, node.x, node.y, node.z))

        x = max_bit_no if (cbit_no < tbit_no_array[0]) else min_bit_no
        while x != cbit_no:
            node.pos.decx(space * d)
            node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
            x -= 1 * d

        node.pos.decy(space)
        node_array.append(self.__new_node(node.type, node.x, node.y, node.z))
        node.pos.decx(space * d)
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
