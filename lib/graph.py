from .position import Position


class Node:
    def __init__(self, type, x, y, z):
        self.ids = []
        self.type = type
        self.pos = Position(x, y, z)

    def add_id(self, id):
        self.ids.append(id)

    # @property
    # def set_type(self, type):
    #     self.type = type
    #
    # @property
    # def type(self):
    #     return self.type

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y

    @property
    def z(self):
        return self.pos.z

    def debug(self):
        print("(", self.type, ",", self.pos.x, ",", self.pos.y, ",", self.pos.z, ")")


class Edge:
    def __init__(self, node1, node2, category):
        self.ids = []
        self.type = node1.type
        self.type = category
        self.node1 = node1
        self.node2 = node2

    def add_id(self, id):
        self.ids.append(id)

    # @property
    # def set_type(self, type):
    #     self.type = type
    #
    # @property
    # def type(self):
    #     return self.type

    @property
    def category(self):
        return self.category

    # @property
    def node1(self):
        return self.node1

    # @property
    def node2(self):
        return self.node2

    def alt_node(self, node):
        if node == self.node1:
            return self.node2
        elif node == self.node2:
            return self.node1
        else:
            assert False


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

        self.circuit = circuit
        self.space = space
        self.max_x = len(circuit.cnots) * 2 + space
        self.min_x = 0 - space
        self.max_y = 3 + space
        self.min_y = -1 - space
        self.max_z = len(circuit.bits) * 2 - 1 + space
        self.min_z = -1 - space

        self.__create()

    def __create(self):
        self.node_array = [[[self.__new_node(x, y, z)
                             for z in range(self.min_z, self. max_z)] \
                            for y in range(self.min_y, self. max_y)] \
                           for x in range(self.min_x, self. max_x)]

        self.node_list = []
        self.edge_list = []

        self.__create_bit_lines()
        self.__create_bridges()
        self.__create_injectors()
        self.__create_braidings()

    def __create_bit_lines(self):
        """
        primal型 defect
        初期化回路のグラフ化に使用
        """
        upper = 1
        lower = 0
        last_upper_node = None
        last_lower_node = None
        for z in range(0, len(self.circuit.bits) * 2, 2):
            for x in range(0, self.circuit.length, 2):
                upper_node = self.node_array[x][upper][z]
                lower_node = self.node_array[x][lower][z]
                upper_node.type = "primal"
                lower_node.type = "primal"
                self.node_list.append(upper_node)
                self.node_list.append(lower_node)
                if last_upper_node != None or last_lower_node != None:
                    self.edge_list.append(self.__new__edge(upper_node, last_upper_node, "line"))
                    self.edge_list.append(self.__new__edge(lower_node, last_lower_node, "line"))
                last_upper_node = upper_node
                last_lower_node = lower_node

    def __create_bridges(self):
        """
        初期化と観測の追加
        初期化回路のグラフ化に使用
        """
        pass

    def __create_injectors(self):
        """
        インジェクタと外部入出力の追加
        初期化回路のグラフ化に使用
        """
        pass

    def __create_braidings(self):
        """
        ブレイディング(Controlled NOT)の追加
        初期化回路のグラフ化に使用
        """
        pass

    def __new_node(self, x, y, z):
        node = Node("none", x, y, z)

        return node

    def __new__edge(self, node1, node2, category):
        edge = Edge(node1, node2, category)

        return edge

    def debug(self):
        for node in self.node_list:
            node.debug()

