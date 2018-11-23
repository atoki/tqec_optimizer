#include <iostream>
#include <algorithm>

#include "loop_factory.hpp"

Loop LoopFactory::Create(const json11::Json& loop) {
    const int id = loop["id"].int_value();
    const std::string type = loop["type"].string_value();
    const int array_size = loop["cross"].array_items().size();
    std::vector<int> cross_list(array_size);
    int index = -1;
    std::generate(cross_list.begin(), cross_list.end(), [&index, &loop]() {
        index++;
        return loop["cross"][index].int_value();
    });
    const int pin_num = loop["pins"].int_value();
    const int cap_num = loop["caps"].int_value();

    return Loop(id, type, cross_list, pin_num, cap_num);
}
