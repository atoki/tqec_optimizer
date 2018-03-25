#ifndef TQEC_OPTIMIZER_EDGE_HPP
#define TQEC_OPTIMIZER_EDGE_HPP

#include <iostream>
#include <cassert>

#include "node.hpp"

class Edge {
public:
    enum class Category {
        Pin,
        Cap,
    };

private:
    int id_;
    std::string type_;
    std::string category_;
    std::string dir_;
    Vector3D pos_;
    Node node1_;
    Node node2_;
    std::vector<Edge> cross_edges_;
    double color_;

public:
    Edge() = default;

    Edge(int id, const std::string& category,
         const Node& node1, const Node& node2) {
        id_ = id;
        type_ = node1.type();
        category_ = category;
        dir_ = calc_dir();
        node1_ = node1;
        node2_ = node2;
        pos_ = Vector3D((node1.pos().x + node2.pos().x) / 2.0,
                        (node1.pos().y + node2.pos().y) / 2.0,
                        (node1.pos().z + node2.pos().z) / 2.0);
        color_ = 0;
    }

    bool operator==(const Edge& other) {
        return this->pos_.x == other.pos().x
               && this->pos_.y == other.pos().y
               && this->pos_.z == other.pos().z;
    }

    int id() const { return id_; }
    std::string type() const { return type_; }
    std::string category() const { return category_; }
    std::string dir() const { return dir_; }
    Vector3D pos() const { return pos_; }
    double color() const { return color_; }
    Node node1() const { return node1_; }
    Node node2() const { return node2_; }
    std::vector<Edge> edges() { return cross_edges_; }

    void set_id(int id) { id_ = id; }
    void set_type(const std::string& type) { type_ = type; }
    void set_category(const std::string& category) { category_ = category; }
    void set_color(double color) { color_ = color; }

    void add_edge(const Edge& edge) {
        cross_edges_.push_back(edge);
    }

    bool is_pin() { return type_ == "pin"; }
    bool is_cap() { return type_ == "cap"; }
    bool is_injector() { return type_ == "pin" || type_ == "cap"; }

    Node& AltNode(const Node& node) {
        if (node == node1_) return node2_;
        else if (node == node2_) return node1_;
        else assert(true);
    }

private:
    std::string calc_dir() {
        if (node1_.pos().x != node2_.pos().x) return  "X";
        else if (node1_.pos().y != node2_.pos().y) return "Y";
        else return "Z";
    }
};

inline
std::ostream & operator<<(std::ostream & os, const Edge& e) {
    os << e.type() << ": (" << e.id() << ") " << e.node1().pos() << " -> " << e.node2().pos();
    return os;
}

#endif //TQEC_OPTIMIZER_EDGE_HPP
