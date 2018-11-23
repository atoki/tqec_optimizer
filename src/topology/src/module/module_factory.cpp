#include "module_factory.hpp"

Module ModuleFactory::Create(const Loop& loop) {
    std::vector<NodePtr> frame_nodes, cross_nodes;
    std::vector<EdgePtr> frame_edges, cross_edges;

    CreateFrame(loop, frame_nodes, frame_edges);
    CreateCross(loop, cross_nodes, cross_edges);
    CreateInjector(loop, frame_nodes, frame_edges);

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
    const int injector_num = std::max(0, (loop.pin_num() + loop.cap_num() - 1));
    const int frame_length = cross_edge_num + injector_num;
    NodePtr node1, node2;
    Vector3D pos = Vector3D(0, 0, 0);

    // create frame
    frame_nodes.push_back(node1 = std::make_shared<Node>(id, pos, type));
    pos.add(0, 2, 0);
    node2 = node1;
    frame_nodes.push_back(node1 = std::make_shared<Node>(id, pos, type));
    frame_edges.push_back(std::make_shared<Edge>(id, "edge", node1, node2));
    for (int n = 0; n < frame_length; ++n) {
        pos.add(0, 0, 2);
        node2 = node1;
        frame_nodes.push_back(node1 = std::make_shared<Node>(id, pos, type));
        frame_edges.push_back(std::make_shared<Edge>(id, "edge", node1, node2));
    }
    pos.add(0, -2, 0);
    node2 = node1;
    frame_nodes.push_back(node1 = std::make_shared<Node>(id, pos, type));
    frame_edges.push_back(std::make_shared<Edge>(id, "edge", node1, node2));
    for (int n = 0; n < frame_length - 1; ++n) {
        pos.add(0, 0, -2);
        node2 = node1;
        frame_nodes.push_back(node1 = std::make_shared<Node>(id, pos, type));
        frame_edges.push_back(std::make_shared<Edge>(id, "edge", node1, node2));
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

void ModuleFactory::CreateInjector(const Loop& loop,
                                   std::vector<NodePtr>& frame_nodes,
                                   std::vector<EdgePtr>& frame_edges) {
    const int id = loop.id();
    const std::string type = loop.type();
    const int cross_edge_num = std::max(1, static_cast<int>(loop.cross_list().size()));
    const int injector_num = std::max(0, (loop.pin_num() + loop.cap_num() - 1));
    const int length = 2 * (cross_edge_num + injector_num);
    Vector3D pos1 = Vector3D(0, 0, length);
    Vector3D pos2 = Vector3D(0, 2, length);

    for (int n = 1; n < injector_num + 1; ++n) {
        pos1.add(0, 0, -n * 2);
        pos2.add(0, 2, -n * 2);
        auto node1 = std::find_if(frame_nodes.begin(), frame_nodes.end(),
                                  [&pos1](const auto& node) { return node->pos() == pos1; });
        auto node2 = std::find_if(frame_nodes.begin(), frame_nodes.end(),
                                  [&pos2](const auto& node) { return node->pos() == pos2; });
        assert(node1 == frame_nodes.end() || node2 == frame_nodes.end());
        frame_edges.push_back(std::make_shared<Edge>(id, "injector", **node1, **node2));
    }

    return;
}