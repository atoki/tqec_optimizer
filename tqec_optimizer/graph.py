from .position import Position


class Node:
    def __init__(self, id, type, x, y, z):
        self._id = id
        self._type = type
        self._pos = Position(x, y, z)
        self._edge_list = []
        self._color = 0

    def set_type(self, type):
        self._type = type

    def add_edge(self, edge):
        self._edge_list.append(edge)

    def set_color(self, color):
        self._color = color

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
        return self._pos.x

    @property
    def y(self):
        return self._pos.y

    @property
    def z(self):
        return self._pos.z

    @property
    def edge_list(self):
        return self._edge_list

    def debug(self):
        print("(", self._type, ",", self._pos.x, ",", self._pos.y, ",", self._pos.z, ")")


class Edge:
    def __init__(self, node1, node2, category, id):
        self._id = id
        self._type = node1.type
        self._category = category
        self._node1 = node1
        self._node2 = node2
        self._cross_edge_list = []
        self._color = 0

    def set_id(self, id):
        self._id = id

    def set_type(self, type):
        self._type = type

    def set_color(self, color):
        self._color = color

    def add_cross_edge(self, edge):
        self._cross_edge_list.append(edge)

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def category(self):
        return self._category

    @property
    def color(self):
        return self._color

    @property
    def x(self):
        return (self._node1.x + self._node2.x) / 2

    @property
    def y(self):
        return (self._node1.y + self._node2.y) / 2

    @property
    def z(self):
        return (self._node1.z + self._node2.z) / 2

    @property
    def node1(self):
        return self._node1

    @property
    def node2(self):
        return self._node2

    @property
    def cross_edge_list(self):
        return self._cross_edge_list

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
    def __init__(self, circuit):
        """
        コンストラクタ

        :param circuit Circuit
        """

        self._circuit = circuit
        self._var_node_count = 0
        self._var_loop_count = 0
        self.__create()

    def __create(self):
        self._node_list = []
        self._edge_list = []

        # (ビット列の作成) -> 初期化・入力 -> 演算 -> 観測・出力 の順に実行
        self.__create_bit_lines()
        self.__create_initializations()
        self.__create_inputs()
        self.__create_operations()
        self.__create_measurements()
        self.__create_outputs()

    @property
    def loop_count(self):
        return self._var_loop_count

    @property
    def node_list(self):
        return self._node_list

    @property
    def edge_list(self):
        return self._edge_list

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

    def __create_initializations(self):
        """
        初期化の追加
        初期回路のグラフ化に使用
        """
        for init in self._circuit.initializations:
            if init["type"] == "z":
                loop_id = self.__new_loop_variable()
                node1 = self.__node(init["bit"] * 2, 0, 0)
                node2 = self.__node(init["bit"] * 2, 2, 0)
                self.__new__edge(node1, node2, "bridge", loop_id)
                self.__assign_line_id(init["bit"] * 2, 0, loop_id)

    def __create_measurements(self):
        """
        観測の追加
        初期回路のグラフ化に使用
        """
        for meas in self._circuit.measurements:
            if meas["type"] == "z":
                loop_id = self.__get_front_edge_loop_id(meas["bit"] * 2, self._circuit.length)
                node1 = self.__node(meas["bit"] * 2, 0, self._circuit.length)
                node2 = self.__node(meas["bit"] * 2, 2, self._circuit.length)
                self.__new__edge(node1, node2, "bridge", loop_id)
            else:
                upper_node1 = self.__node(meas["bit"] * 2, 2, self._circuit.length)
                lower_node1 = self.__node(meas["bit"] * 2, 0, self._circuit.length)
                upper_node2 = self.__new_node(upper_node1.type, meas["bit"] * 2, 2, self._circuit.length + 2)
                lower_node2 = self.__new_node(lower_node1.type, meas["bit"] * 2, 0, self._circuit.length + 2)
                self.__new__edge(upper_node1, upper_node2, "line")
                self.__new__edge(lower_node1, lower_node2, "line")

                # X基底の観測直前にZ基底の観測、ピンがなければ閉じていないループの番号を0に上書きする
                remove = True
                for edge in upper_node1.edge_list:
                    if edge.category == "bridge" or edge.category == "pin" or edge.category == "cap":
                        remove = False
                if remove:
                    loop_id = self.__get_front_edge_loop_id(meas["bit"] * 2, self._circuit.length)
                    self.__remove_loop_id(loop_id)

    def __create_inputs(self):
        """
        外部入力の追加
        初期回路のグラフ化に使用
        """
        for x in self._circuit.inputs:
            loop_id = self.__new_loop_variable()
            node1 = self.__node(x * 2, 0, 0)
            node2 = self.__node(x * 2, 2, 0)
            self.__new__edge(node1, node2, "cap", loop_id)
            self.__assign_line_id(x * 2, 0, loop_id)

    def __create_outputs(self):
        """
        外部出力の追加
        初期回路のグラフ化に使用
        """
        for x in self._circuit.outputs:
            loop_id = self.__get_front_edge_loop_id(x * 2, self._circuit.length)
            node1 = self.__node(x * 2, 0, self._circuit.length)
            node2 = self.__node(x * 2, 2, self._circuit.length)
            self.__new__edge(node1, node2, "cap", loop_id)

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
        loop_id = self.__get_front_edge_loop_id(operation["target"] * 2, no * 6)
        node1 = self.__node(operation["target"] * 2, 0, no * 6)
        node2 = self.__node(operation["target"] * 2, 2, no * 6)
        self.__new__edge(node1, node2, "pin", loop_id)
        loop_id = self.__new_loop_variable()
        self.__assign_line_id(operation["target"] * 2, no * 6, loop_id)

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
        loop_id = self.__get_front_edge_loop_id(cbit_no * space, no * 6 + 3 - 1)
        upper = self.__node(cbit_no * space, 2, no * 6 + 3 - 1)
        lower = self.__node(cbit_no * space, 0, no * 6 + 3 - 1)
        self.__new__edge(upper, lower, "line", loop_id)

        loop_id = self.__new_loop_variable()
        upper = self.__node(cbit_no * space, 2, no * 6 + 3 + 1)
        lower = self.__node(cbit_no * space, 0, no * 6 + 3 + 1)
        self.__new__edge(upper, lower, "line", loop_id)
        self.__assign_line_id(cbit_no * space, no * 6 + 3 + 1, loop_id)

        # ブレイディングの作成
        loop_id = self.__new_loop_variable()
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
                self.__new__edge(node, last_node, "edge", loop_id)
            last_node = node
        self.__new__edge(first_node, last_node, "edge", loop_id)

    def __assign_line_id(self, x, z, id):
        """
        辺に対してループの番号を振る
        """
        for edge in self._edge_list:
            if edge.x == x and edge.z > z:
                edge.set_id(id)

    def __get_front_edge_loop_id(self, x, z):
        for edge in self._edge_list:
            if (edge.node1.x == x and edge.node1.z == z and edge.node2.z < z) \
                    or (edge.node2.x == x and edge.node2.z == z and edge.node1.z < z):
                return edge.id

    def __remove_loop_id(self, loop_id):
        for edge in self._edge_list:
            if edge.id == loop_id:
                edge.set_id(0)

    def __node(self, x, y, z, id=0):
        if id == 0:
            for node in self._node_list:
                if node.x == x and node.y == y and node.z == z:
                    return node
        else:
            for node in self._node_list:
                if node.id == id:
                    return node

    def __edge(self, node1, node2):
        for edge in node1.edge_list:
            alt_node = edge.alt_node(node1)
            if alt_node == node2:
                return edge

    def __new_node_variable(self):
        self._var_node_count += 1
        return self._var_node_count

    def __new_loop_variable(self):
        self._var_loop_count += 1
        return self._var_loop_count

    def __new_node(self, type, x, y, z):
        node = Node(self.__new_node_variable(), type, x, y, z)
        self._node_list.append(node)

        return node

    def __new__edge(self, node1, node2, category, id=0):
        edge = Edge(node1, node2, category, id)
        node1.add_edge(edge)
        node2.add_edge(edge)
        self.edge_list.append(edge)

        return edge

    def debug(self):
        for node in self._node_list:
            node.debug()

        for edge in self._edge_list:
            edge.debug()
