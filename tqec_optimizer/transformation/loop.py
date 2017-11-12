class Loop:
    """
    ループクラス
    """
    def __init__(self, loop_id):
        """
        コンストラクタ

        :param loop_id モジュールを構成する閉路の番号
        """
        self._id = loop_id
        self._edge_list = []
        self._cross_list = []
        self._injector_list = []

    @property
    def id(self):
        return self._id

    @property
    def edge_list(self):
        return self._edge_list

    @property
    def cross_list(self):
        return self._cross_list

    @property
    def injector_list(self):
        return self._injector_list

    def add_edge(self, edge):
        self._edge_list.append(edge)

    def add_cross(self, cross_loop_id):
        if cross_loop_id not in self._cross_list:
            self._cross_list.append(cross_loop_id)

    def add_injector(self, injector):
        self._injector_list.append(injector)
