#ifndef TQEC_OPTIMIZER_MODULE_HPP
#define TQEC_OPTIMIZER_MODULE_HPP

#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <limits>

#include "../graph/node.hpp"
#include "../graph/edge.hpp"

class Module {
public:
    enum class Axis {
        X,
        Y,
        Z
    };

    using NodePtr = std::shared_ptr<Node>;
    using EdgePtr = std::shared_ptr<Edge>;

private:
    int id_;
    int pin_num_;
    int cap_num_;

    std::vector<int> cross_ids_;
    std::vector<NodePtr> nodes_; // <- 注意!使えない!
    std::vector<NodePtr> frame_nodes_;
    std::vector<NodePtr> cross_nodes_;
    std::vector<EdgePtr> edges_; // <- 注意!使えない!
    std::vector<EdgePtr> frame_edges_;
    std::vector<EdgePtr> cross_edges_;

    Vector3D pos_;
    Vector3D inner_pos_;
    Vector3D size_;
    Vector3D inner_size_;

public:
    Module() = default;

    Module(const int id) {
        id_ = id;
        pin_num_ = 0;
        cap_num_ = 0;
    }

    Module(const int id,
           const std::vector<int> cross_ids,
           const std::vector<NodePtr> frame_nodes,
           const std::vector<NodePtr> cross_nodes,
           const std::vector<EdgePtr> frame_edges,
           const std::vector<EdgePtr> cross_edges) {
        id_ = id;
        pin_num_ = 0;
        cap_num_ = 0;
        cross_ids_ = std::move(cross_ids);
        frame_nodes_ = std::move(frame_nodes);
        cross_nodes_ = std::move(cross_nodes);
        frame_edges_ = std::move(frame_edges);
        cross_edges_ = std::move(cross_edges);

//        nodes_.insert(nodes_.begin(), frame_nodes_.begin(), frame_nodes_.end());
//        nodes_.insert(nodes_.end(), cross_nodes_.begin(), cross_nodes_.end());
//        edges_.insert(edges_.begin(), frame_edges_.begin(), frame_edges_.end());
//        edges_.insert(edges_.end(), cross_edges_.begin(), cross_edges_.end());

        // update module position
        update();
    }

    int id() const { return id_; }
    int pin_num() const { return pin_num_; }
    int cap_num() const { return cap_num_; }
    std::vector<NodePtr> nodes() const { return nodes_; }
    std::vector<NodePtr> frame_nodes() const { return frame_nodes_; }
    std::vector<NodePtr> cross_nodes() const { return cross_nodes_; }
    std::vector<EdgePtr> edges() const { return edges_; }
    std::vector<EdgePtr> frame_edges() const { return frame_edges_; }
    std::vector<EdgePtr> cross_edges() const { return cross_edges_; }
    std::vector<int> cross_ids() const { return cross_ids_; }
    Vector3D pos() const { return pos_; }
    Vector3D inner_pos() const { return inner_pos_; }
    Vector3D size() const { return size_; }
    double width() const { return size_.x; }
    double height() const { return size_.y; }
    double depth() const { return size_.z; }
    Vector3D inner_size() const { return  inner_size_; }
    double inner_width() const { return inner_size_.x; }
    double inner_height() const { return inner_size_.y; }
    double inner_depth() const { return inner_size_.z; }

    bool has_pin() const { return pin_num_ > 0; }
    bool cap_pin() const { return cap_num_ > 0; }

    void add_pin() {
        pin_num_++;
    }

    void add_cap() {
        cap_num_++;
    }

    void add_frame_node(const NodePtr node) {
        nodes_.push_back(node);
        frame_nodes_.push_back(node);
    }

    void add_cross_node(const NodePtr node) {
        nodes_.push_back(node);
        cross_nodes_.push_back(node);
    }

    void add_frame_edge(const EdgePtr edge) {
        edges_.push_back(edge);
        frame_edges_.push_back(edge);
    }

    void add_cross_edge(const EdgePtr edge) {
        edges_.push_back(edge);
        cross_edges_.push_back(edge);
    }

    void add_cross_id(const int id) {
        cross_ids_.push_back(id);
    }

    void set_pos(const Vector3D& pos, const bool replace=false) {
        if (replace) {
            const double diff_x = pos.x - pos_.x;
            const double diff_y = pos.y - pos_.y;
            const double diff_z = pos.z - pos_.z;
            for (auto& node : frame_nodes_) {
                node->move(diff_x, diff_y, diff_z);
            }
            for (auto& node : cross_nodes_) {
                node->move(diff_x, diff_y, diff_z);
            }
            update();
        }
        pos_ = pos;
    }

    void set_inner_pos(const Vector3D& inner_pos) {
        inner_pos_ = inner_pos;
    }

    void set_size(const Vector3D& size) {
        size_ = size;
    }

    void set_inner_size(const Vector3D& inner_size) {
        inner_size_ = inner_size;
    }

private:
    bool invalidate_rotate(const double from, const double to){
        return static_cast<int>(from) % 2 != static_cast<int>(to) % 2;
    }

public:
    void update();

    bool rotate(const Axis axis);
};

inline
std::ostream & operator<<(std::ostream & os, const Module& m) {
    os << "--- " << m.id() << " ---" << '\n';
    os << "pos : " << m.pos() << '\n';
    os << "width : " << m.width() << '\n';
    os << "height: " << m.height() << '\n';
    os << "depth : " << m.depth() << '\n';
    return os;
}

#endif //TQEC_OPTIMIZER_MODULE_HPP
