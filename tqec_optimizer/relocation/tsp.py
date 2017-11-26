from collections import defaultdict


class TSP:
    def __init__(self, joint_pair_list):
        self._joint_pair_list = joint_pair_list
        self._end_map = {}
        self._route_pair = {}

        self.__create_end_map()

    def search(self):
        joint_map = defaultdict(list)
        for joint_pair in self._joint_pair_list:
            for i in range(0, 2):
                if joint_pair[i] in self._end_map:
                    joint_map[joint_pair[i].id].append(joint_pair[i])

        for id_, joint_list in joint_map.items():
            self.__assign_target_node(joint_list)

        return self._route_pair

    def __assign_target_node(self, joint_list):
        if len(joint_list) == 2:
            joint_list[0].set_target_node(joint_list[1])
            joint_list[1].set_target_node(joint_list[0])
            self._route_pair[joint_list[0]] = joint_list[1]
            return

        current_joint = joint_list[0]
        first_joint = end_joint = current_joint
        joint_list.remove(current_joint)
        while len(joint_list) != 0:
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
        self._route_pair[end_joint] = first_joint

    def __create_end_map(self):
        for end_pair in self._joint_pair_list:
            if end_pair[0] in self._end_map:
                self._end_map[end_pair[1]] = self._end_map[end_pair[0]]
                self._end_map[self._end_map[end_pair[0]]] = end_pair[1]
                del self._end_map[end_pair[0]]
            else:
                self._end_map[end_pair[0]] = end_pair[1]
                self._end_map[end_pair[1]] = end_pair[0]




