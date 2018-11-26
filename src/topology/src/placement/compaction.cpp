#include "compaction.hpp"
#include "relocation.hpp"

void Compaction::Execute() {
    /*
     * 1. relocation of modules
     * 2. allocation of labels
     * 3. allocation of connecting parts
     * 4. routing
     */

    Relocation(module_list_).Execute();

    return;
}
