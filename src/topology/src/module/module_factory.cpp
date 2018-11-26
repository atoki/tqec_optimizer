#include "module_factory.hpp"

Module ModuleFactory::Create(const Loop& loop) {
    std::vector<NodePtr> frame_nodes, cross_nodes;
    std::vector<EdgePtr> frame_edges, cross_edges;

    CreateFrame(loop, frame_nodes, frame_edges);
    CreateCross(loop, cross_nodes, cross_edges);

    return Module(loop.id(), loop.cross_list(),
                  frame_nodes, cross_nodes,
                  frame_edges, cross_edges);
}

void ModuleFactory::CreateFrame(const Loop& loop,
                                std::vector<NodePtr>& frame_nodes,
                                std::vector<EdgePtr>& frame_edges) {
    const int id = loop.id();
    const std::string type = loop.type();
    const int cross_edge_num = std::max(1, static_cast<int>(loop.cross_list().size()));
    const int injector_num = loop.pin_num() + loop.cap_num();
    const int frame_length = cross_edge_num + std::max(0, injector_num - 1);

    NodePtr upper_node1, upper_node2, lower_node1, lower_node2;
    Vector3D upper_pos = Vector3D(0, 2, 0);
    Vector3D lower_pos = Vector3D(0, 0, 0);

    // create frame
    frame_nodes.push_back(upper_node1 = std::make_shared<Node>(id, upper_pos, type));
    frame_nodes.push_back(lower_node1 = std::make_shared<Node>(id, lower_pos, type));
    frame_edges.push_back(std::make_shared<Edge>(id, "edge", upper_node1, lower_node1));

    for (int n = 0; n < frame_length; ++n) {
        upper_pos.z += 2;
        lower_pos.z += 2;
        upper_node2 = upper_node1;
        lower_node2 = lower_node1;
        frame_nodes.push_back(upper_node1 = std::make_shared<Node>(id, upper_pos, type));
        frame_nodes.push_back(lower_node1 = std::make_shared<Node>(id, lower_pos, type));
        frame_edges.push_back(std::make_shared<Edge>(id, "edge", upper_node1, upper_node2));
        frame_edges.push_back(std::make_shared<Edge>(id, "edge", lower_node1, lower_node2));
        if (injector_num > 0 && n >= cross_edge_num - 1) {
            frame_edges.push_back(std::make_shared<Edge>(id, "injector", upper_node1, lower_node1));
        }
    }

    return;
}

void ModuleFactory::CreateCross(const Loop& loop,
                                std::vector<NodePtr>& cross_nodes,
                                std::vector<EdgePtr>& cross_edges) {
    const std::string type = (loop.type() == "primal") ? "dual" : "primal";
    Vector3D pos1 = Vector3D(1, 1, 1);
    Vector3D pos2 = Vector3D(-1, 1, 1);
    NodePtr joint1, joint2;
    for (const int cross_id : loop.cross_list()) {
        cross_nodes.push_back(joint1 = std::make_shared<Node>(cross_id, pos1, type));
        cross_nodes.push_back(joint2 = std::make_shared<Node>(cross_id, pos2, type));
        cross_edges.push_back(std::make_shared<Edge>(cross_id, "edge", joint1, joint2));
        pos1.add(0, 0, 1);
        pos2.add(0, 0, 1);
    }

    return;
}