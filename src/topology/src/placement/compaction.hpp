#ifndef TQEC_OPTIMIZER_COMPACTION_HPP
#define TQEC_OPTIMIZER_COMPACTION_HPP

#include <vector>

#include "../module/module.hpp"

class Compaction {
private:
    std::vector<Module>& module_list_;

public:
    Compaction() = default;

    Compaction(std::vector<Module>& module_list)
            : module_list_(module_list) { }

    void Execute();
};


#endif //TQEC_OPTIMIZER_COMPACTION_HPP
