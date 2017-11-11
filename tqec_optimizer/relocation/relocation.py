from .module import Module


class Relocation:
    """
    モジュールへの切断と再配置による最適化を行う
    """
    def __init__(self, graph):
        self._graph = graph
        self._module_list = []

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

            if len(module_.edge_list) == 0:
                continue

            # ループを構成している辺と交差している辺をモジュールに追加する
            for edge in module_.edge_list:
                if len(edge.cross_edge_list) == 0:
                    continue

                for cross_edge in edge.cross_edge_list:
                    self._module_list.append(cross_edge)

            # モジュールを構成する全ての辺から座標とサイズ情報を更新する
            module_.update()

            # モジュールの中身があればリストに追加
            self._module_list.append(module_)

    def execute(self):
        """
        1.グラフ情報を用いてモジュールを作成
        2.モジュール単位で再配置を行う
        3.再配置したモジュールの再接続を行う
        4.コストが減少しなくなるまで 2.3 を繰り返す
        """
        self.__generate_module()
        # self.__color_module()

        return self._graph

    def __color_module(self):
        """
        モジュールに色付けをして可視化する
        """
        for module_ in self._module_list:
            id = module_.id
            color = self.__generate_random_color(id)
            for edge in module_.edge_list:
                edge.set_color(color)
                edge.node1.set_color(color)
                edge.node2.set_color(color)

    @staticmethod
    def __generate_random_color(loop_id):
        colors = [0xffdead, 0x808080, 0x191970, 0x0000ff, 0x00ffff, 0x008000,
                  0x00ff00, 0xffff00, 0x8b0000, 0xff1493, 0x800080]
        return colors[loop_id % 11]

    def debug(self):
        for module_ in self._module_list:
            module_.debug()
