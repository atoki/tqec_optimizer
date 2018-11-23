#ifndef TQEC_OPTIMIZER_LOOP_FACTORY_HPP
#define TQEC_OPTIMIZER_LOOP_FACTORY_HPP

#include <memory>

#include "../json11/json11.hpp"
#include "loop.hpp"

class LoopFactory {
public:
    using LoopPtr = std::shared_ptr<Loop>;

    LoopFactory() = default;

    Loop Create(const json11::Json& loop);
};

#endif //TQEC_OPTIMIZER_LOOP_FACTORY_HPP