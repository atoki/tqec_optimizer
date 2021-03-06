#! /usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """
Usage:
    {f} [-i | --input <input_file>] [-o | --output <output_file>] [-t | --type <type>]
    {f} [-b | --bp] [-i | --input <input_file>] [-o | --output <output_file>]
    {f} -h | --help

Options:
    -i --input=<input_file>     input file
    -o --output=<output_file>   output file     [default: result.json]
    -t --type=<type>            split type      [default: primal]
    -h --help                   show this screen
""".format(f=__file__)


import math
import time
from docopt import docopt

from tqec_optimizer.circuit_reader import CircuitReader
from tqec_optimizer.graph import Graph
from tqec_optimizer.circuit_writer import CircuitWriter

from tqec_optimizer.braidpack.braid_pack import Braidpack
from tqec_optimizer.transformation.transformation import Transformation
from tqec_optimizer.relocation.relocation import Relocation


def main():
    args = docopt(__doc__)
    input_file = args['--input'][0]
    output_file = args['--output'][0]
    type_ = args['--type'][0]
    braid_pack = args['-b'] or args['--bp']

    # preparation
    circuit = CircuitReader().read_circuit(input_file)
    graph = Graph(circuit)
    CircuitWriter(graph).write("init.json")
    print("first cost: {}".format(evaluate(graph)))
    start = time.time()

    if braid_pack:
        # braid pack
        graph = Braidpack(graph).execute()
    else:
        # optimization of non topology
        loop_list = Transformation(graph).execute()

        # optimization of topology
        graph = Relocation(type_, loop_list, graph).execute()

    elapsed_time = time.time() - start
    print("result cost: {}".format(evaluate(graph)))
    print("total time: {}".format(elapsed_time))

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
