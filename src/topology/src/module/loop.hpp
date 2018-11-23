#ifndef TQEC_OPTIMIZER_LOOP_HPP
#define TQEC_OPTIMIZER_LOOP_HPP

#include <vector>
#include <string>

class Loop {
private:
    int id_;
    std::string type_;
    std::vector<int> cross_list_;
    int pin_num_;
    int cap_num_;

public:
    Loop() = default;

    Loop(const int id,
         const std::string& type,
         const std::vector<int>& cross_list,
         const int pin_num,
         const int cap_num)
            : id_(id),
              type_(type),
              cross_list_(cross_list),
              pin_num_(pin_num),
              cap_num_(cap_num) { }

    int id() const { return id_; }
    std::string type() const { return type_; }
    std::vector<int> cross_list() const { return cross_list_; }
    int pin_num() const { return pin_num_; }
    int cap_num() const { return cap_num_; }
};

inline
std::ostream & operator<<(std::ostream & os, const Loop& l) {
    os << "--- " << l.id() << " ---" << '\n';
    os << "type: " << l.type() << '\n';
    os << "cross list: ";
    for (const auto& e : l.cross_list()) {
        os << e << " ";
    }
    os << '\n';
    os << "pin num: " << l.pin_num() << '\n';
    os << "cap num: " << l.cap_num() << '\n';
    return os;
}

#endif //TQEC_OPTIMIZER_LOOP_HPP
