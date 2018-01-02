from collections import defaultdict


class Allocation:
    def __init__(self, module_list, id_set):
        self._module_list = module_list
        self._id_set = id_set

        # init
        for module_ in self._module_list:
            for edge in module_.edge_list:
                edge.set_id(0)
                edge.node1.set_id(0)
                edge.node2.set_id(0)

    def execute(self):
        self.__assign_connect_edge()
        self.__assign_isolated_edge()

    def __assign_connect_edge(self):
        edge_map = {}
        connect_edge = defaultdict(list)
        for module_ in self._module_list:
            for joint_pair in module_.joint_pair_list:
                joint1, joint2 = joint_pair[0], joint_pair[1]
                edge = joint_pair[2]

                if joint1 in edge_map and joint2 in edge_map:
                    connect_edge[edge_map[joint1]].extend(connect_edge[edge_map[joint2]])
                    connect_edge[edge_map[joint1]].append(edge)
                    del_edge = edge_map[joint2]

                    for edge in connect_edge[edge_map[joint2]]:
                        node1, node2 = edge.node1, edge.node2
                        edge_map[node1] = edge_map[joint1]
                        edge_map[node2] = edge_map[joint1]

                    del connect_edge[del_edge]

                elif joint1 in edge_map:
                    edge_map[joint2] = edge_map[joint1]
                    connect_edge[edge_map[joint1]].append(edge)

                elif joint2 in edge_map:
                    edge_map[joint1] = edge_map[joint2]
                    connect_edge[edge_map[joint2]].append(edge)

                else:
                    edge_map[joint1] = edge
                    edge_map[joint2] = edge
                    connect_edge[edge].append(edge)

        for key_edge, edge_list in sorted(connect_edge.items(), key=lambda x: len(x[1]), reverse=True):
            if len(edge_list) == 1:
                break

            result = self._id_set[edge_list[0].module_id]
            for edge in edge_list:
                tmp = self._id_set[edge.module_id]
                result = result & tmp

            assign_id = result.pop()
            for edge in edge_list:
                edge.set_id(assign_id)
                edge.fix()
                edge.node1.set_id(assign_id)
                edge.node2.set_id(assign_id)
                self._id_set[edge.module_id].remove(assign_id)

    def __assign_isolated_edge(self):
        for module_ in self._module_list:
            for edge in module_.cross_edge_list:
                if edge.id > 0:
                    continue
                assign_id = self._id_set[edge.module_id].pop()
                edge.set_id(assign_id)
                edge.node1.set_id(assign_id)
                edge.node2.set_id(assign_id)
