#include <limits>

#include "module.hpp"

void Module::update() {
    double max_x, max_y, max_z;
    double min_x, min_y, min_z;
    max_x = max_y = max_z = std::numeric_limits<double>::min();
    min_x = min_y = min_z = std::numeric_limits<double>::max();

    for (const Node& node : frame_nodes_) {
        min_x = std::min(node.pos().x - 1, min_x);
        min_y = std::min(node.pos().y - 1, min_y);
        min_z = std::min(node.pos().z - 1, min_z);
        max_x = std::max(node.pos().x + 1, max_x);
        max_y = std::max(node.pos().y + 1, max_y);
        max_z = std::max(node.pos().z + 1, max_z);
    }
    inner_pos_.assign(min_x, min_y, min_z);
    inner_size_.assign(max_x - min_x, max_y - min_y, max_z - min_z);

    for (const Node& node : cross_nodes_) {
        min_x = std::min(node.pos().x, min_x);
        min_y = std::min(node.pos().y, min_y);
        min_z = std::min(node.pos().z, min_z);
        max_x = std::max(node.pos().x, max_x);
        max_y = std::max(node.pos().y, max_y);
        max_z = std::max(node.pos().z, max_z);
    }
    pos_.assign(min_x, min_y, min_z);
    size_.assign(max_x - min_x, max_y - min_y, max_z - min_z);
}

bool Module::rotate(const Axis axis) {
    Vector3D center(pos_.x + (size_.w() / 2.0), pos_.y + (size_.h() / 2.0), pos_.z + (size_.d() / 2.0));

    switch (axis) {
        case Axis::X: {
            for (auto& node : frame_nodes_) {
                double rel_x, rel_y, rel_z;
                std::tie(rel_x, rel_y, rel_z) = std::make_tuple(node.pos().x - center.x,
                                                                node.pos().y - center.y,
                                                                node.pos().z - center.z);
                Vector3D relative_pos(rel_x, -rel_z, rel_y);
                if (invalidate_rotate(rel_y, relative_pos.y)) return false;
                node.pos().assign(relative_pos.x + center.x, relative_pos.y + center.y, relative_pos.z + center.z);
            }
            update();
            break;
        }
        case Axis::Y: {
            for (auto& node : frame_nodes_) {
                double rel_x, rel_y, rel_z;
                std::tie(rel_x, rel_y, rel_z) = std::make_tuple(node.pos().x - center.x,
                                                                node.pos().y - center.y,
                                                                node.pos().z - center.z);
                Vector3D relative_pos(rel_z, rel_y, -rel_x);
                if (invalidate_rotate(rel_x, relative_pos.x)) return false;
                node.assign(relative_pos.x + center.x, relative_pos.y + center.y, relative_pos.z + center.z);
            }
            update();
            break;
        }
        case Axis::Z: {
            for (auto& node : frame_nodes_) {
                double rel_x, rel_y, rel_z;
                std::tie(rel_x, rel_y, rel_z) = std::make_tuple(node.pos().x - center.x,
                                                                node.pos().y - center.y,
                                                                node.pos().z - center.z);
                Vector3D relative_pos(-rel_y, rel_x, rel_z);
                if (invalidate_rotate(rel_x, relative_pos.x)) return false;
                node.assign(relative_pos.x + center.x, relative_pos.y + center.y, relative_pos.z + center.z);
            }
            update();
            break;
        }
    }

    return true;
}