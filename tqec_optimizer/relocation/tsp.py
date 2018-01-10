from collections import defaultdict

from .sa import SA


class TSP:
    def __init__(self, graph, module_list):
        self._graph = graph
        self._module_list = module_list
        self._joint_pair_list = []
        self._end_map = {}
        self._invalidate_pair = {}
        self._route_list = defaultdict(list)
        self._route_pair = {}
        self._result_pair = {}

        for module_ in module_list:
            self._joint_pair_list.extend(module_.joint_pair_list)

        self.__create_end_map()

    def search(self):
        joint_map = defaultdict(list)
        for joint in self._end_map.keys():
            joint_map[joint.id].append(joint)

        for id_, joint_list in joint_map.items():
            self.__assign_target_node(id_, joint_list)

        route_pair = {}
        for route_list in self._route_list.values():
            route = SA(self._graph, self._module_list, route_list, self._invalidate_pair).execute()
            route_pair.update(route)

        return route_pair

    def __assign_target_node(self, id_, joint_list):
        if len(joint_list) == 2:
            self._route_list[id_].append(joint_list[0])
            self._route_list[id_].append(joint_list[1])
            self._route_pair[joint_list[0]] = joint_list[1]
            return

        current_joint = joint_list[0]
        first_joint = end_joint = current_joint
        joint_list.remove(current_joint)
        while len(joint_list) != 0:
            self._route_list[id_].append(current_joint)
            if current_joint in self._end_map:
                next_joint = self._end_map[current_joint]
                del self._end_map[current_joint]
                del self._end_map[next_joint]
            else:
                next_joint = joint_list[0]
                dist = current_joint.dist(next_joint)
                for joint in joint_list:
                    if dist > joint.dist(current_joint):
                        dist = joint.dist(current_joint)
                        next_joint = joint
                self._route_pair[current_joint] = next_joint
            end_joint = current_joint = next_joint
            joint_list.remove(current_joint)
        self._route_list[id_].append(end_joint)
        self._route_pair[end_joint] = first_joint

    def __create_end_map(self):
        used_pair = {}
        for end_pair in self._joint_pair_list:
            if end_pair[2] in used_pair:
                continue
            elif end_pair[0] in self._end_map and end_pair[1] in self._end_map:
                self._end_map[self._end_map[end_pair[0]]] = self._end_map[end_pair[1]]
                self._end_map[self._end_map[end_pair[1]]] = self._end_map[end_pair[0]]
                del self._end_map[end_pair[0]]
                del self._end_map[end_pair[1]]
                self._invalidate_pair[self._invalidate_pair[end_pair[0]]] = self._invalidate_pair[end_pair[1]]
                self._invalidate_pair[self._invalidate_pair[end_pair[1]]] = self._invalidate_pair[end_pair[0]]
                del self._invalidate_pair[end_pair[0]]
                del self._invalidate_pair[end_pair[1]]
            elif end_pair[0] in self._end_map:
                self._end_map[end_pair[1]] = self._end_map[end_pair[0]]
                self._end_map[self._end_map[end_pair[0]]] = end_pair[1]
                del self._end_map[end_pair[0]]
                self._invalidate_pair[end_pair[1]] = self._invalidate_pair[end_pair[0]]
                self._invalidate_pair[self._invalidate_pair[end_pair[0]]] = end_pair[1]
                del self._invalidate_pair[end_pair[0]]
            elif end_pair[1] in self._end_map:
                self._end_map[end_pair[0]] = self._end_map[end_pair[1]]
                self._end_map[self._end_map[end_pair[1]]] = end_pair[0]
                del self._end_map[end_pair[1]]
                self._invalidate_pair[end_pair[0]] = self._invalidate_pair[end_pair[1]]
                self._invalidate_pair[self._invalidate_pair[end_pair[1]]] = end_pair[0]
                del self._invalidate_pair[end_pair[1]]
            else:
                self._end_map[end_pair[0]] = end_pair[1]
                self._end_map[end_pair[1]] = end_pair[0]
                self._invalidate_pair[end_pair[0]] = end_pair[1]
                self._invalidate_pair[end_pair[1]] = end_pair[0]
            used_pair[end_pair[2]] = True
