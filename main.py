#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from lib.circuit_reader import CircuitReader
from lib.circuit import Circuit
from lib.graph import Graph
from lib.circuit_writer import CircuitWriter


def main():
    file_name = sys.argv[1]
    circuit = CircuitReader().read_circuit(file_name)
    circuit.debug()
    graph = Graph(circuit, 2)
    # graph.debug()
    writer = CircuitWriter(graph)
    writer.write()


if __name__ == '__main__':
    main()
