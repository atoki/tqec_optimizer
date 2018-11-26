#ifndef TQEC_OPTIMIZER_NODE_HPP
#define TQEC_OPTIMIZER_NODE_HPP

#include <iostream>
#include <string>
#include <cassert>
#include <algorithm>

#include "vector3d.hpp"

class Node {
private:
    int id_;
    std::string type_;
    Vector3D pos_;
    std::vector<Node> connected_nodes_;
    double color_;

public:
    Node() = default;

    Node(const int id,
         const Vector3D pos,
         const std::string type = "none")
            : id_(id),
              type_(type),
              pos_(pos),
              color_(0.0){ }

    bool operator==(const Node& other) const {
        return this->pos_.x == other.pos().x
               && this->pos_.y == other.pos().y
               && this->pos_.z == other.pos().z;
    }

    int id() const { return id_; }
    std::string type() const { return type_; }
    Vector3D pos() const { return pos_; }
    std::vector<Node> connected_nodes() const { return connected_nodes_; }
    double color() const { return  color_; }

    void set_id(const int id) { id_ = id; }
    void set_type(const std::string type) { type_ = type; }
    void set_color(const double color) { color_ = color; }

    void assign(const Vector3D& pos) { pos_ = pos; }
    void assign(const double x, const double y, const double z) { pos_.assign(x, y, z); }

    void add_connect_node(const Node& node) {
        connected_nodes_.push_back(node);
    }

    void remove_connected_node(const Node& node) {
        auto target = std::find_if(connected_nodes_.begin(), connected_nodes_.end(),
                                   [&node](const Node& n) { return node == n; });
        assert(target != connected_nodes_.end());
        connected_nodes_.erase(target);
    }

    double dist(const Node& node) {
        return this->pos_.dist(node.pos());
    }

    void move(const double diff_x, const double diff_y, const double diff_z) {
        pos_.assign(this->pos_.x + diff_x, this->pos_.y + diff_y, this->pos_.z + diff_z);
    }
};

inline
std::ostream & operator<<(std::ostream & os, const Node& n) {
    os << n.type() << ": (" << n.id() << ") " << n.pos();
    return os;
}

#endif //TQEC_OPTIMIZER_NODE_HPP
