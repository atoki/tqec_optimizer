#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getopt

from lib.circuit_reader import CircuitReader
from lib.circuit import Circuit
from lib.graph import Graph
from lib.circuit_writer import CircuitWriter

from lib.relocation.relocation import Relocation


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
        output_file = "sample.json"

    # preparation
    circuit = CircuitReader().read_circuit(input_file)
    circuit.debug()
    graph = Graph(circuit, 2)
    # graph.debug()

    # optimization of topology
    optimization = Relocation(graph)
    optimization.execute()
    # optimization.debug()

    # output
    writer = CircuitWriter(graph)
    writer.write(output_file)


if __name__ == '__main__':
    main()
