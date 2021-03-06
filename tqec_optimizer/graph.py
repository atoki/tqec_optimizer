import copy

from .vector3d import Vector3D
from .node import Node
from .edge import Edge


class Graph:
    """
    TQEC回路をグラフ問題として定式化する
    座標系はtqec_viewerに準拠(=OpenGL(右手座標系))
    """
    def __init__(self, circuit=None):
        """
        コンストラクタ

        :param circuit Circuit
        """

        self._circuit = circuit
        self._node_list = []
        self._edge_list = []
        self._var_node_count = 0
        self._var_loop_count = 0

        if circuit is not None:
            self.__create()

    def __create(self):
        """
        (ビット列の作成) -> 初期化・入力 -> 演算 -> 観測・出力 の順にグラフ化する
        """

        self.__create_bit_lines()
        self.__create_initializations()
        self.__create_inputs()
        self.__create_operations()
        self.__create_measurements()
        self.__create_outputs()

        self.__update_cross_info()
        self.__adjust_cross_edge()

    @property
    def loop_count(self):
        return self._var_loop_count

    @property
    def node_list(self):
        return self._node_list

    @property
    def edge_list(self):
        return self._edge_list

    @property
    def var_node_count(self):
        return self._var_node_count

    def set_loop_count(self, loop_count):
        self._var_loop_count = loop_count

    def add_node(self, node):
        self._node_list.append(node)

    def add_edge(self, edge):
        self._edge_list.append(edge)

    def __create_bit_lines(self):
        """
        primal型 qubit defect pair
        初期回路のグラフ化に使用
        """

        (upper, lower, type) = (2, 0, "primal")
        print("width: ", self._circuit.width)
        print("length:", self._circuit.length)

        for x in range(0, self._circuit.width, 2):
            last_upper_node = None
            last_lower_node = None
            for z in range(0, self._circuit.length + 1, 2):

                # CNOT 箇所は切断する
                skip = False
                cnot_x, cnot_z = 0, 0
                injector_target = {}
                for no, operation in enumerate(self._circuit.operations):
                    if operation["type"] == "cnot":
                        injector_target.clear()
                        cnot_x = operation["control"] * 2
                        cnot_z += 6
                    else:
                        if len(injector_target) > 0 and operation["target"] in injector_target:
                            cnot_z += 2
                            injector_target.clear()
                        injector_target[operation["target"]] = operation["type"]
                        cnot_x = -1

                    if x == cnot_x and z == cnot_z - 2:
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
                    if edge.category == "bridge" or edge.is_injector():
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
        z = 0
        injector_target = {}
        for operation in self._circuit.operations:
            if operation["type"] == "cnot":
                self.__create_braidings(z, operation)
                injector_target.clear()
                z += 6
            else:
                if len(injector_target) > 0:
                    if operation["target"] in injector_target:
                        z += 2
                        self.__create_state_injection(z, operation)
                        injector_target.clear()
                    else:
                        self.__create_state_injection(z, operation)
                else:
                    self.__create_state_injection(z, operation)
                injector_target[operation["target"]] = operation["type"]

    def __create_state_injection(self, z, operation):
        """
        State Injectionの追加
        初期回路のグラフ化に使用

        :param z State Injectionを設置するz座標
        :param operation
        """
        loop_id = self.__get_front_edge_loop_id(operation["target"] * 2, z)
        node1 = self.__node(operation["target"] * 2, 0, z)
        node2 = self.__node(operation["target"] * 2, 2, z)
        self.__new__edge(node1, node2, "pin", loop_id)

    def __create_braidings(self, z, cnot):
        """
        ブレイディング(Controlled NOT)の追加
        初期回路のグラフ化に使用
        左回りに作る

        :param z CNOT gate を設置するz座標
        :param cnot
        """
        (type, space) = ("dual", 2)
        node_array = []

        tbit_no_array = copy.deepcopy(cnot["targets"])
        cbit_no = cnot["control"]
        bit_no_array = tbit_no_array
        bit_no_array.append(cbit_no)
        max_bit_no = max(bit_no_array)
        min_bit_no = min(bit_no_array)
        d = 1.0 if (cbit_no < tbit_no_array[0]) else -1.0

        # ループを閉じる為のEdgeを作成
        loop_id = self.__get_front_edge_loop_id(cbit_no * space, z + 3 - 1)
        upper = self.__node(cbit_no * space, 2, z + 3 - 1)
        lower = self.__node(cbit_no * space, 0, z + 3 - 1)
        primal_edge1 = self.__new__edge(upper, lower, "line", loop_id)

        loop_id = self.__new_loop_variable()
        upper = self.__node(cbit_no * space, 2, z + 3 + 1)
        lower = self.__node(cbit_no * space, 0, z + 3 + 1)
        primal_edge2 = self.__new__edge(upper, lower, "line", loop_id)
        self.__assign_line_id(cbit_no * space, z + 3 + 1, loop_id)

        # ブレイディングの作成
        loop_id = self.__new_loop_variable()
        pos = Vector3D(cbit_no * space - 1 * d, 1, z + 3 - space * d)
        node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))
        pos.incx(space * d)
        node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))

        start = min_bit_no if (cbit_no < tbit_no_array[0]) else max_bit_no
        x = start + 1 * d
        limit = max_bit_no if (cbit_no < tbit_no_array[0]) else min_bit_no
        while x != limit + 1 * d:
            if x in tbit_no_array:
                if pos.y != 1:
                    pos.decy(space)
                    node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))
                pos.incx(space * d)
                node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))

            else:
                if pos.y == 1:
                    pos.incy(space)
                    node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))

                pos.incx(space * d)
                node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))
            x += 1 * d

        pos.incy(space)
        node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))
        pos.incz(space * d)
        node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))
        pos.incz(space * d)
        node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))

        x = max_bit_no if (cbit_no < tbit_no_array[0]) else min_bit_no
        while x != cbit_no:
            pos.decx(space * d)
            node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))
            x -= 1 * d

        pos.decy(space)
        node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))
        pos.decx(space * d)
        node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))
        pos.decz(space * d)
        node_array.append(self.__new_node(type, pos.x, pos.y, pos.z))

        first_node = node_array[0]
        last_node = None
        left = 1 if (cbit_no < tbit_no_array[0]) else len(node_array) - 2
        right = len(node_array) - 2 if (cbit_no < tbit_no_array[0]) else 1
        for no, node in enumerate(node_array):
            if last_node is not None:
                edge = self.__new__edge(node, last_node, "edge", loop_id)
                # 交差するedgeを追加する
                if no == left:
                    edge.add_cross_edge(primal_edge1)
                    primal_edge1.add_cross_edge(edge)
                if no == right:
                    edge.add_cross_edge(primal_edge2)
                    primal_edge2.add_cross_edge(edge)
            last_node = node
        self.__new__edge(first_node, last_node, "edge", loop_id)

    def __adjust_cross_edge(self):
        """
        ある辺に交差した辺のidが0だった場合、
        その辺を交差した辺を保持する配列から削除する
        """
        for edge in self._edge_list:
            del_edge_index = []
            for no, cross_edge in enumerate(edge.cross_edge_list):
                if cross_edge.id == 0:
                    del_edge_index.append(no)

            del_edge_index.sort()
            del_edge_index.reverse()

            for index in del_edge_index:
                del edge.cross_edge_list[index]

    def __update_cross_info(self):
        """
        CNOTのtargetとbit列の交差情報を更新する
        """
        z = 0
        injector_target = {}
        for no, operation in enumerate(self._circuit.operations):
            if operation["type"] == "cnot" and operation["control"] < operation["targets"][0]:
                for target in operation["targets"]:
                    x = target * 2
                    primal_node1 = self.__node(x, 2, z + 2)
                    primal_node2 = self.__node(x, 2, z)
                    primal_edge = self.__edge(primal_node1, primal_node2)
                    dual_node1 = self.__node(x - 1, 1, z + 1)
                    dual_node2 = self.__node(x + 1, 1, z + 1)
                    dual_edge = self.__edge(dual_node1, dual_node2)
                    primal_edge.add_cross_edge(dual_edge)
                    dual_edge.add_cross_edge(primal_edge)

            if operation["type"] == "cnot" and operation["control"] > operation["targets"][0]:
                for target in operation["targets"]:
                    x = target * 2
                    primal_node1 = self.__node(x, 2, z + 6)
                    primal_node2 = self.__node(x, 2, z + 4)
                    primal_edge = self.__edge(primal_node1, primal_node2)
                    dual_node1 = self.__node(x - 1, 1, z + 5)
                    dual_node2 = self.__node(x + 1, 1, z + 5)
                    dual_edge = self.__edge(dual_node1, dual_node2)
                    primal_edge.add_cross_edge(dual_edge)
                    dual_edge.add_cross_edge(primal_edge)

            if operation["type"] == "cnot":
                z += 6
                injector_target.clear()
            else:
                if len(injector_target) > 0:
                    if operation["target"] in injector_target:
                        z += 2
                        injector_target.clear()
                injector_target[operation["target"]] = operation["type"]

    def __assign_line_id(self, x, z, id):
        """
        x列のz座標より置くの辺に対してループの番号idを振る

        :param x 列
        :param z この座標から奥のビットにidを振る
        :param id 構成する辺に振る番号
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

    def __node(self, x, y, z, id_=0):
        if id_ == 0:
            for node in self._node_list:
                if node.x == x and node.y == y and node.z == z:
                    return node
        else:
            for node in self._node_list:
                if node.id == id_:
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

    def __new_node(self, type_, x, y, z):
        node = Node(x, y, z, self.__new_node_variable(), type_)
        self._node_list.append(node)

        return node

    def __new__edge(self, node1, node2, category, id_=0):
        edge = Edge(node1, node2, category, id_)
        node1.add_edge(edge)
        node2.add_edge(edge)
        self.edge_list.append(edge)

        return edge

    def dump(self):
        for node in self._node_list:
            node.dump()

        for edge in self._edge_list:
            edge.dump()
