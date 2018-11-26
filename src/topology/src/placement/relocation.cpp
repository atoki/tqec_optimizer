#include <limits>

#include "relocation.hpp"
#include "sequence_triple.hpp"
#include "../module/module.hpp"

void Relocation::Execute() {
    const double initial_t = 100.0;
    const double final_t = 0.01;
    const double cool_rate = 0.99;
    const int limit = 1000;

    // 各モジュールの配置を初期化
    CreateInitialPlacement();

    double current_cost = Evaluate(module_list_);
    std::cout <<"初期評価値: " << current_cost << std::endl;
    double current_t = initial_t;
    SequenceTripe seq_tripe = SequenceTripe(module_list_);

//    while (current_t > final_t) {
//        for (int n = 0; n < limit; ++n) {
//            seq_tripe.CreateNeighborhood();
//            std::vector<Module> candidate = seq_tripe.RecalculateCoordinate();
//
//            if (!isValid()) {
//                seq_tripe.Recover();
//                continue;
//            }
//
//            double new_cost = Evaluate(candidate);
//
//            if (shouldChange(new_cost - current_cost, current_t)) {
//                current_cost = new_cost;
//                seq_tripe.Apply();
//            }
//            else {
//                seq_tripe.Recover();
//            }
//        }
//        current_t *= cool_rate;
//    }

    return;
}

void Relocation::CreateInitialPlacement() {
    Vector3D pos = Vector3D(0, 0, 0);
    for (Module& module : module_list_) {
        module.set_pos(pos, true);
        pos.z += module.depth();
    }
    return;
}

double Relocation::Evaluate(const std::vector<Module>& module_list) {
    double cost = 0.0;
    double inf = std::numeric_limits<double>::infinity();
    double min_x = inf, min_y = inf, min_z = inf;
    double max_x = -inf, max_y = -inf, max_z = -inf;
    double width, height, depth;

    for (const Module& module : module_list) {
        for (const auto& node : module.frame_nodes()) {
            min_x = std::min(node->pos().x, min_x);
            min_y = std::min(node->pos().y, min_y);
            min_z = std::min(node->pos().z, min_z);
            max_x = std::max(node->pos().x, max_x);
            max_y = std::max(node->pos().y, max_y);
            max_z = std::max(node->pos().z, max_z);
        }
        for (const auto& node : module.cross_nodes()) {
            min_x = std::min(node->pos().x, min_x);
            min_y = std::min(node->pos().y, min_y);
            min_z = std::min(node->pos().z, min_z);
            max_x = std::max(node->pos().x, max_x);
            max_y = std::max(node->pos().y, max_y);
            max_z = std::max(node->pos().z, max_z);
        }
    }

    width = (max_x - min_x) / 2 - 1;
    height = (max_y - min_y) / 2 - 1;
    depth = (max_z - min_z) / 2 - 1;

    cost = width + height + depth;

    return cost;
}

bool Relocation::isValid() {
    return false;
}