from .module import Module
from .sequence_triple import SequenceTriple

from ..graph import Graph


class Relocation:
    """
    モジュールへの切断と再配置による最適化を行う
    """
    def __init__(self, graph):
        self._graph = graph
        self._primal_module_list = []
        self._dual_module_list = []

    def execute(self):
        """
        1.グラフ情報を用いてモジュールを作成
        2.モジュール単位で再配置を行う
        3.再配置したモジュールの再接続を行う
        4.コストが減少しなくなるまで 2.3 を繰り返す
        """
        self.__generate_module()
        self.__color_module()

        # primal defect
        # place = SequenceTriple("primal", self._primal_module_list, (6, 6, 20))
        # place.build_permutation()
        # module_list = place.recalculate_coordinate()

        # dual defect
        # place = SequenceTriple("dual", self._dual_module_list, (6, 6, 20))
        # place.build_permutation()
        # module_list = place.recalculate_coordinate()
        #
        # graph = self.__module_to_graph(module_list)
        #
        # return graph

    def __generate_module(self):
        """
        モジュールを生成する
        """
        for loop_id in range(1, self._graph.loop_count + 1):
            module_ = Module(loop_id)

            # ループを構成している辺をモジュールに追加する
            for edge in self._graph.edge_list:
                if edge.id == loop_id:
                    module_.add_edge(edge)
                    # ループを構成している辺と交差している辺をモジュールに追加する
                    for cross_edge in edge.cross_edge_list:
                        if cross_edge in self._graph.edge_list:
                            module_.add_cross_edge(cross_edge)

            if len(module_.edge_list) == 0:
                continue

            type_ = module_.edge_list[0].type

            # モジュールを構成する全ての辺から座標とサイズ情報を更新する
            module_.update()

            # モジュールの中身があればリストに追加
            if type_ == "primal":
                self._primal_module_list.append(module_)
            else:
                self._dual_module_list.append(module_)

    def __module_to_graph(self, module_list):
        """
        モジュールを構成するノードと辺の情報をもとにグラフクラスを作成する

        :param module_list グラフ化するモジュールのリスト
        """
        graph = Graph()
        for module_ in module_list:
            for edge in module_.edge_list + module_.cross_edge_list:
                graph.add_edge(edge)
                graph.add_node(edge.node1)
                graph.add_node(edge.node2)

        return graph

    def __color_module(self):
        """
        モジュールに色付けをして可視化する
        """
        for module_ in self._dual_module_list:
            id_ = module_.id
            color = self.__generate_random_color(id_)
            for edge in module_.edge_list + module_.cross_edge_list:
                edge.set_color(color)
                edge.node1.set_color(color)
                edge.node2.set_color(color)

    @staticmethod
    def __generate_random_color(loop_id):
        colors = [0xffdead, 0x808080, 0x191970, 0x00ffff, 0x008000,
                  0x00ff00, 0xffff00, 0x8b0000, 0xff1493, 0x800080]
        return colors[loop_id % 10]

    def debug(self):
        print("--- primal module list ---")
        for module_ in self._primal_module_list:
            module_.debug()
        print("--- dual module list ---")
        for module_ in self._dual_module_list:
            module_.debug()
