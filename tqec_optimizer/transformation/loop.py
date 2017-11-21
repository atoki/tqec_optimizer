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

    def set_id(self, id_):
        for edge in self._edge_list:
            edge.set_id(id_)

    def add_edge(self, edge):
        self._edge_list.append(edge)

    def add_cross(self, cross_loop_id):
        if cross_loop_id not in self._cross_list:
            self._cross_list.append(cross_loop_id)

    def add_injector(self, injector):
        self._injector_list.append(injector)

    def remove_cross(self, cross_loop_id):
        self._cross_list.remove(cross_loop_id)

    def shift_injector(self, category):
        """
        他のループからインジェクターを移動させてくる
        移す場所は適当

        :param category 移動させるピンの種類
        """
        candidate_edge = self._edge_list[0]
        for edge in self._edge_list:
            if edge.is_injector():
                continue

            if edge.z > candidate_edge.z:
                candidate_edge = edge

            if edge.z == candidate_edge.z:
                if edge.x < candidate_edge.x:
                    candidate_edge = edge

        candidate_edge.set_category(category)
        self._injector_list.append(candidate_edge)

    def debug(self):
        print("-----  loop id: {} -----".format(self._id))
        print("edge list     = {}".format(len(self._edge_list)))
        print("cross list    = {}".format(len(self._cross_list)))
        print("injector list = {}".format(len(self._injector_list)))
