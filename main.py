#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt

from tqec_optimizer.circuit_reader import CircuitReader
from tqec_optimizer.graph import Graph
from tqec_optimizer.circuit_writer import CircuitWriter

from tqec_optimizer.transformation.transformation import Transformation
from tqec_optimizer.relocation.relocation import Relocation
from tqec_optimizer.relocation.tqec_evaluator import TqecEvaluator


def usage():
    print("usage:", sys.argv[0],)
    print("""
        -h|--help
        -i|--input  FILE
        -o|--output FILE
        """)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:i:o:", ["help", "input=", "output="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    input_file = None
    output_file = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-i", "--input"):
            input_file = a
        if o in ("-o", "--output"):
            output_file = a

    if output_file is None:
        output_file = "result.json"

    # preparation
    circuit = CircuitReader().read_circuit(input_file)
    graph = Graph(circuit)
    CircuitWriter(graph).write("1-init.json")
    print("first cost: {}".format(len(graph.node_list)))

    # optimization of non topology
    Transformation(graph).execute()
    CircuitWriter(graph).write("2-transform.json")

    # optimization of topology
    graph = Relocation(graph).execute()
    print("result cost: {}".format(len(graph.node_list)))

    # output
    CircuitWriter(graph).write(output_file)


if __name__ == '__main__':
    main()
