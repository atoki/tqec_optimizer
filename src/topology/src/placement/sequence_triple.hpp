#ifndef TQEC_OPTIMIZER_SEQUENCE_TRIPLE_HPP
#define TQEC_OPTIMIZER_SEQUENCE_TRIPLE_HPP

#include <vector>
#include <map>

#include "../module/module.hpp"

class SequenceTripe {
private:
    std::vector<Module> module_list_;

    std::vector<int> permutation1_;
    std::vector<int> permutation2_;
    std::vector<int> permutation3_;
    std::vector<int> c_permutation1_;
    std::vector<int> c_permutation2_;
    std::vector<int> c_permutation3_;

    std::map<int, std::vector<int>> rotate_map_;
    std::map<int, std::vector<int>> c_rotate_map_;

    std::map<int, Module> module_map_;

public:
    SequenceTripe() = default;

    SequenceTripe(std::vector<Module> module_list);

    void Apply();

    void Recover();

    void CreateNeighborhood();

    std::vector<Module> RecalculateCoordinate();

private:
    void Swap();

    void Shift();

    void Rotate();

    double FindX();
    double FindY();
    double FindZ();
};

#endif //TQEC_OPTIMIZER_SEQUENCE_TRIPLE_HPP
