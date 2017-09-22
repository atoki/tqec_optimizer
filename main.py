#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from lib.circuit_reader import CircuitReader
from lib.circuit import Circuit
from lib.graph import Graph


def main():
    file_name = "y.json"
    circuit = CircuitReader().read_circuit(file_name)
    graph = Graph(circuit, 2)


if __name__ == '__main__':
    main()
