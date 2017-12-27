#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import getopt

from tqec_optimizer.circuit_reader import CircuitReader
from tqec_optimizer.graph import Graph
from tqec_optimizer.circuit_writer import CircuitWriter

from tqec_optimizer.transformation.transformation import Transformation
from tqec_optimizer.relocation.relocation import Relocation


def usage():
    print("usage:", sys.argv[0],)
    print("""
        -h|--help
        -i|--input  FILE
        -o|--output FILE
        """)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:i:o:t:", ["help", "input=", "output=", "type="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    input_file = None
    output_file = None
    type_ = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-i", "--input"):
            input_file = a
        if o in ("-o", "--output"):
            output_file = a
        if o in ("-t", "--type"):
            type_ = a

    if output_file is None:
        output_file = "6-result.json"

    if type_ is None:
        type_ = "dual"

    # preparation
    circuit = CircuitReader().read_circuit(input_file)
    graph = Graph(circuit)
    CircuitWriter(graph).write("1-init.json")
    print("first cost: {}".format(evaluate(graph)))

    # optimization of non topology
    loop_list = Transformation(graph).execute()
    print("transformation cost: {}".format(evaluate(graph)))
    CircuitWriter(graph).write("2-transform.json")

    # optimization of topology
    graph = Relocation(type_, loop_list, graph).execute()
    print("relocation cost: {}".format(evaluate(graph)))

    # output
    CircuitWriter(graph).write(output_file)


def evaluate(graph):
    min_x = min_y = min_z = math.inf
    max_x = max_y = max_z = -math.inf
    for node in graph.node_list:
        if node.type == "primal":
            min_x, min_y, min_z = min(node.x, min_x), min(node.y, min_y), min(node.z, min_z)
            max_x, max_y, max_z = max(node.x, max_x), max(node.y, max_y), max(node.z, max_z)

    width = (max_x - min_x) / 2 + 1
    height = (max_y - min_y) / 2 + 1
    depth = (max_z - min_z) / 2 + 1

    return width * height * depth


if __name__ == '__main__':
    main()
