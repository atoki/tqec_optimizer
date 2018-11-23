#ifndef TQEC_OPTIMIZER_MODULE_FACTORY_HPP
#define TQEC_OPTIMIZER_MODULE_FACTORY_HPP

#include <memory>

#include "module.hpp"
#include "loop.hpp"

class ModuleFactory {
public:
    using NodePtr = std::shared_ptr<Node>;
    using EdgePtr = std::shared_ptr<Edge>;

    ModuleFactory() = default;

    Module Create(const Loop& loop);

private:
    void CreateFrame(const Loop& loop,
                     std::vector<NodePtr>& frame_nodes,
                     std::vector<EdgePtr>& frame_edges);

    void CreateCross(const Loop& loop,
                     std::vector<NodePtr>& cross_nodes,
                     std::vector<EdgePtr>& cross_edges);

    void CreateInjector(const Loop& loop,
                        std::vector<NodePtr>& frame_nodes,
                        std::vector<EdgePtr>& frame_edges);
};

#endif //TQEC_OPTIMIZER_MODULE_FACTORY_HPP
