import json
from .graph import Graph


class CircuitWriter:
    """
    グラフ情報からtqec_viwerに対応したjsonファイルを作成する
    """

    def __init__(self, graph):
        """
        コンストラクタ
        """
        self._graph = graph
        self._logical_qubits = []
        self._edges = []
        self._injectors = []

    def write(self, output_file):
        self.__make_logical_qubits()
        self.__make_edges_and_injectors()

        data = {"logical_qubits": self._logical_qubits,
                "edges": self._edges,
                "injectors": self._injectors}

        with open(output_file, 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def __make_logical_qubits(self):
        for node in self._graph.node_list:
            dic = {"pos": node.pos.to_array(),
                   "type": node.type}
            self._logical_qubits.append(dic)

    def __make_edges_and_injectors(self):
        for edge in self._graph.edge_list:
            if edge.category == "cap" or edge.category == "pin":
                dic = {"pos1": edge.node1.pos.to_array(),
                       "pos2": edge.node2.pos.to_array(),
                       "type": edge.type,
                       "category": edge.category}
                self._injectors.append(dic)

            else:
                dic = {"pos1": edge.node1.pos.to_array(),
                       "pos2": edge.node2.pos.to_array(),
                       "type": edge.type}
                self._edges.append(dic)
