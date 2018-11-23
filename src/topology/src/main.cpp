#include <iostream>
#include <fstream>
#include <memory>

#include "json11/json11.hpp"
#include "graph/node.hpp"
#include "graph/edge.hpp"
#include "module/loop_factory.hpp"
#include "module/module_factory.hpp"


json11::Json input(const std::string& filename) {
    auto ifs = std::ifstream(filename);

    assert(!ifs.fail());

    auto buf = std::string();
    auto str = std::string();
    auto err = std::string();

    while (std::getline(ifs, str)) buf += str;

    ifs.close();

    return json11::Json::parse(buf, err);
}

int main() {
    const auto filename = std::string("test.json");
    const auto json = input(filename);
    const auto& loops = json["loops"];

    std::vector<Loop> loop_list;
    for (const json11::Json& l : loops.array_items()) {
        const auto loop = LoopFactory().Create(l);
        loop_list.push_back(loop);
        std::cout << loop << std::endl;
    }

    std::vector<Module> module_list;
    for (const Loop& loop : loop_list) {
        const auto module = ModuleFactory().Create(loop);
        module_list.push_back(module);
        std::cout << module << std::endl;
    }

    return 0;
}
