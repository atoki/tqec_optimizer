#ifndef TQEC_OPTIMIZER_RELOCATION_HPP
#define TQEC_OPTIMIZER_RELOCATION_HPP

#include <vector>
#include <random>
#include <cmath>

#include "../module/module.hpp"

class Relocation {
private:
    std::vector<Module>& module_list_;

public:
    Relocation() = default;

    Relocation(std::vector<Module>& module_list)
            : module_list_(module_list) { }

    void Execute();

private:
    void CreateInitialPlacement();

    double Evaluate(const std::vector<Module>& module_list);

    inline bool shouldChange(double delta, double t) {
        std::mt19937 engine ;
        std::uniform_real_distribution<double> distribution(0.0, 1.0);

        if (delta <= 0.0) return true;
        if (distribution(engine) < std::exp(-delta / t)) return true;
        return false;
    }

    bool isValid();
};

#endif //TQEC_OPTIMIZER_RELOCATION_HPP
