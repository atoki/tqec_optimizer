#! /usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """
Usage:
    {f} [-n | --number <n>]
    {f} -h | --help

Options:
    -n --number=<n>     
""".format(f=__file__)


import json
from collections import OrderedDict
from docopt import docopt


def main():
    write()


def write():
    args = docopt(__doc__)
    qubit = 16
    qc_num = int(args['--number'][0])
    bits = []
    inputs = []
    outputs = []
    initializations = []
    measurements = []
    operations = []

    # bits
    for n in range(0, qubit * qc_num):
        bits.append(n)

    # outputs
    output = 15
    for n in range(0, qc_num):
        outputs.append(output)
        output = output + 16

    # initialization
    type_list = ["x", "x", "z", "x", "z",
                 "z", "z", "x", "z", "z",
                 "z", "z", "z", "z", "z", "x"]
    base = 0
    for i in range(0, qc_num):
        for j in range(0, 16):
            dic = {"bit": base + j,
                   "type": type_list[j]}
            initializations.append(dic)
        base = base + 16

    # measurement
    base = 0
    for i in range(0, qc_num):
        for j in range(0, 15):
            dic = {"bit": base + j,
                   "type": "x"}
            measurements.append(dic)
        base = base + 16

    # operation
    base = 0
    for i in range(0, qc_num):
        cnot1 = {"type": "cnot", "control": base + 15, "targets": [base + 14]}
        operations.append(cnot1)
        cnot2 = {"type": "cnot",
                 "control": base + 7,
                 "targets": [base + 8, base + 9, base + 10, base + 11, base + 12, base + 13, base + 14]}
        operations.append(cnot2)
        cnot3 = {"type": "cnot",
                 "control": base + 3,
                 "targets": [base + 4, base + 5, base + 6, base + 11, base + 12, base + 13, base + 14]}
        operations.append(cnot3)
        cnot4 = {"type": "cnot",
                 "control": base + 1,
                 "targets": [base + 2, base + 5, base + 6, base + 9, base + 10, base + 13, base + 14]}
        operations.append(cnot4)
        cnot5 = {"type": "cnot",
                 "control": base + 0,
                 "targets": [base + 2, base + 4, base + 6, base + 8, base + 10, base + 12, base + 14]}
        operations.append(cnot5)
        cnot6 = {"type": "cnot",
                 "control": base + 14,
                 "targets": [base + 2, base + 4, base + 5, base + 8, base + 9, base + 11]}
        operations.append(cnot6)

        for j in range(0, 15):
            injection = {"type": "t", "target": base + j}
            operations.append(injection)
        for j in range(0, 15):
            injection = {"type": "t", "target": base + j}
            operations.append(injection)
        base = base + 16

    data = OrderedDict()
    data["bits"] = bits
    data["inputs"] = inputs
    data["outputs"] = outputs
    data["initializations"] = initializations
    data["measurements"] = measurements
    data["operations"] = operations

    output_file = "./data/a-" + str(qc_num) + ".json"
    with open(output_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)


if __name__ == '__main__':
    main()
