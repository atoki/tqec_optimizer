#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import getopt

from tqec_optimizer.circuit_reader import CircuitReader
from tqec_optimizer.graph import Graph
from tqec_optimizer.circuit_writer import CircuitWriter

from tqec_optimizer.braidpack.braid_pack import Braidpack
from tqec_optimizer.transformation.transformation import Transformation
from tqec_optimizer.relocation.relocation import Relocation


def usage():
    print("usage:", sys.argv[0],)
    print("""
        -h|--help
        -b|--bp execute braid pack
        -i|--input  FILE
        -o|--output FILE
        -t|--type   module type (dual or primal)
        """)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:b:i:o:t:", ["help", "bp", "input=", "output=", "type="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    should_bp = False
    input_file = None
    output_file = None
    type_ = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-b", "--bp"):
            should_bp = True
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

    if should_bp:
        # braid pack
        graph = Braidpack(graph).execute()
    else:
        # optimization of non topology
        loop_list = Transformation(graph).execute()
        CircuitWriter(graph).write("2-transform.json")

        # optimization of topology
        graph = Relocation(type_, loop_list, graph).execute()

    print("result cost: {}".format(evaluate(graph)))
    # output
    CircuitWriter(graph).write(output_file)


def evaluate(graph):
    p_max_x = p_max_y = p_max_z = d_max_x = d_max_y = d_max_z = -math.inf
    p_min_x = p_min_y = p_min_z = d_min_x = d_min_y = d_min_z = math.inf
    for node in graph.node_list:
        if node.type == "primal":
            p_max_x, p_max_y, p_max_z = max(node.x, p_max_x), max(node.y, p_max_y), max(node.z, p_max_z)
            p_min_x, p_min_y, p_min_z = min(node.x, p_min_x), min(node.y, p_min_y), min(node.z, p_min_z)
        else:
            d_max_x, d_max_y, d_max_z = max(node.x, d_max_x), max(node.y, d_max_y), max(node.z, d_max_z)
            d_min_x, d_min_y, d_min_z = min(node.x, d_min_x), min(node.y, d_min_y), min(node.z, d_min_z)

    width = (p_max_x - p_min_x) / 2 + 1
    height = (p_max_y - p_min_y) / 2 + 1
    depth = (p_max_z - p_min_z) / 2 + 1

    width += int((d_max_x - p_max_x) / 2) + int(abs(d_min_x) / 2)
    height += int((d_max_y - p_max_y) / 2) + int(abs(d_min_y) / 2)
    depth += int((d_max_z - p_max_z) / 2) + int(abs(d_min_z) / 2)

    return width * height * depth


if __name__ == '__main__':
    main()
