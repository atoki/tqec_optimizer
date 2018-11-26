#include <algorithm>
#include <random>

#include "sequence_triple.hpp"

SequenceTripe::SequenceTripe(std::vector<Module> module_list){
    std::vector<int> axis(3, 0);
    for (Module& module : module_list_) {
        permutation1_.push_back(module.id());
        permutation2_.push_back(module.id());
        permutation3_.push_back(module.id());
        rotate_map_[module.id()] = axis;
        c_rotate_map_[module.id()] = axis;
        module_map_[module.id()] = module;
    }

    // Z軸方向にソート
    sort(permutation3_.begin(), permutation3_.end(), [&](int id1, int id2) {
        return (module_map_[id1].pos().z == module_map_[id2].pos().z )
               ? module_map_[id1].pos().x < module_map_[id2].pos().x
               : module_map_[id1].pos().z < module_map_[id2].pos().z;
    });
    sort(permutation2_.begin(), permutation2_.end(), [&](int id1, int id2) {
        return (module_map_[id1].pos().z == module_map_[id2].pos().z )
               ? module_map_[id1].pos().x < module_map_[id2].pos().x
               : module_map_[id1].pos().z < module_map_[id2].pos().z;
    });
    sort(permutation1_.begin(), permutation1_.end(), [&](int id1, int id2) {
        return (module_map_[id1].pos().z == module_map_[id2].pos().z )
               ? module_map_[id1].pos().x < module_map_[id2].pos().x
               : module_map_[id1].pos().z < module_map_[id2].pos().z;
    });

    // X軸方向にソート
    sort(permutation2_.begin(), permutation2_.end(), [&](int id1, int id2) {
        return (module_map_[id1].pos().x == module_map_[id2].pos().x )
               ? module_map_[id1].pos().z < module_map_[id2].pos().z
               : module_map_[id1].pos().x > module_map_[id2].pos().x;
    });

    c_permutation1_ = permutation1_;
    c_permutation2_ = permutation2_;
    c_permutation3_ = permutation3_;
}

/*
 * SA用の近傍を生成する
 * 1. swap近傍
 * 2. shift近傍
 * 3. rotate近傍
 以上の3つを等確率で一つ採用
*/
void SequenceTripe::CreateNeighborhood() {
    std::mt19937 engine;
    std::uniform_int_distribution<int> distribution(1,3);
    int strategy = distribution(engine);

    c_permutation1_ = permutation1_;
    c_permutation2_ = permutation2_;
    c_permutation3_ = permutation3_;
    c_rotate_map_ = rotate_map_;

    if (strategy == 1) Swap();
    else if (strategy == 2) Shift();
    else Rotate();

    return;
}

void SequenceTripe::Swap() {
    const int size = permutation1_.size();
    std::mt19937 engine;
    std::uniform_int_distribution<int> distribution(0, size - 1);
    const int s1 = distribution(engine);
    const int s2 = distribution(engine);
    const int id1 = c_permutation1_[s1];
    const int id2 = c_permutation1_[s2];

    auto iter = std::find(c_permutation1_.begin(), c_permutation1_.end(), id1);
    size_t p1_index1 = std::distance(c_permutation1_.begin(), iter);
    iter = std::find(c_permutation1_.begin(), c_permutation1_.end(), id2);
    size_t p1_index2 = std::distance(c_permutation1_.begin(), iter);

    iter = std::find(c_permutation2_.begin(), c_permutation2_.end(), id1);
    size_t p2_index1 = std::distance(c_permutation2_.begin(), iter);
    iter = std::find(c_permutation2_.begin(), c_permutation2_.end(), id2);
    size_t p2_index2 = std::distance(c_permutation2_.begin(), iter);

    iter = std::find(c_permutation3_.begin(), c_permutation3_.end(), id1);
    size_t p3_index3 = std::distance(c_permutation3_.begin(), iter);
    iter = std::find(c_permutation3_.begin(), c_permutation3_.end(), id2);
    size_t p3_index2 = std::distance(c_permutation3_.begin(), iter);

    std::swap(c_permutation1_[p1_index1], c_permutation1_[p1_index2]);
    std::swap(c_permutation2_[p1_index1], c_permutation2_[p1_index2]);
    std::swap(c_permutation3_[p1_index1], c_permutation3_[p1_index2]);

    return;
}

void SequenceTripe::Shift() {
    const int size = permutation1_.size();
    std::mt19937 engine;
    std::uniform_int_distribution<int> distribution(0, size - 1);
    std::uniform_int_distribution<int> pd(1, 3);
    const int index = distribution(engine);
    int shift_size1 = distribution(engine);
    int shift_size2 = distribution(engine);
    const int pair = pd(engine);

    const int element = c_permutation1_[index];
    if (pair == 1) {
        auto iter1 = std::find(c_permutation1_.begin(), c_permutation1_.end(), element);
        int p1_index = std::distance(c_permutation1_.begin(), iter1);
        auto iter2 = std::find(c_permutation2_.begin(), c_permutation2_.end(), element);
        int p2_index = std::distance(c_permutation2_.begin(), iter2);

        // elementを右シフト in c_permutation1
        if (p1_index + shift_size1 > size) {
            shift_size2 -= std::max(0, (p1_index + shift_size1) - size);
        }
        int x = std::move(c_permutation1_[p1_index]);
        c_permutation1_.erase(c_permutation1_.begin() + p1_index);
        c_permutation1_.insert(c_permutation1_.begin() + shift_size1, element);

        // elementを右シフト in c_permutation2
        if (p2_index + shift_size2 > size) {
            shift_size2 -= std::max(0, (p2_index + shift_size2) - size);
        }
        x = std::move(c_permutation2_[p2_index]);
        c_permutation2_.erase(c_permutation2_.begin() + p2_index);
        c_permutation2_.insert(c_permutation2_.begin() + shift_size2, element);
    }
    else if (pair == 2) {
        auto iter1 = std::find(c_permutation1_.begin(), c_permutation1_.end(), element);
        int p1_index = std::distance(c_permutation1_.begin(), iter1);
        auto iter2 = std::find(c_permutation3_.begin(), c_permutation3_.end(), element);
        int p3_index = std::distance(c_permutation3_.begin(), iter2);

        // elementを右シフト in c_permutation1
        if (p1_index + shift_size1 > size) {
            shift_size2 -= std::max(0, (p1_index + shift_size1) - size);
        }
        int x = std::move(c_permutation1_[p1_index]);
        c_permutation1_.erase(c_permutation1_.begin() + p1_index);
        c_permutation1_.insert(c_permutation1_.begin() + shift_size1, element);

        // elementを右シフト in c_permutation3
        if (p3_index + shift_size2 > size) {
            shift_size2 -= std::max(0, p3_index + shift_size2 - size);
        }
        x = std::move(c_permutation3_[p3_index]);
        c_permutation3_.erase(c_permutation3_.begin() + p3_index);
        c_permutation3_.insert(c_permutation3_.begin() + shift_size2, element);
    }
    else {
        auto iter1 = std::find(c_permutation1_.begin(), c_permutation2_.end(), element);
        int p2_index = std::distance(c_permutation2_.begin(), iter1);
        auto iter2 = std::find(c_permutation3_.begin(), c_permutation3_.end(), element);
        int p3_index = std::distance(c_permutation3_.begin(), iter2);

        // elementを右シフト in c_permutation2
        if (p2_index + shift_size1 > size) {
            shift_size2 -= std::max(0, p2_index + shift_size1 - size);
        }
        int x = std::move(c_permutation2_[p2_index]);
        c_permutation2_.erase(c_permutation2_.begin() + p2_index);
        c_permutation2_.insert(c_permutation2_.begin() + shift_size1, element);

        // elementを右シフト in c_permutation3
        if (p3_index + shift_size2 > size) {
            shift_size2 -= std::max(0, p3_index + shift_size2 - size);
        }
        x = std::move(c_permutation3_[p3_index]);
        c_permutation3_.erase(c_permutation3_.begin() + p3_index);
        c_permutation3_.insert(c_permutation3_.begin() + shift_size2, element);
    }

    return;
}

void SequenceTripe::Rotate() {
    return;
}

