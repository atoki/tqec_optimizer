#! /usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """
Usage:
    {f} [-q | --qubit <qubit>] [-g | --gate <gate>] [-o | --output <output_file>]
    {f} {f} [-q | --qubit <qubit>] [-g | --gate <gate>]
    {f} -h | --help

Options:
    -q --qubit=<qubit>          number of qubit
    -g --gate=<gate>            number of gate
    -o --output=<output_file>   output file     [default: circuit.json]
    
""".format(f=__file__)


from docopt import docopt


def main():
    args = docopt(__doc__)
    n_qubit = args['--qubit'][0]
    n_gate = args['--gate'][0]
    output_file = args['--output'][0]

    

if __name__ == '__main__':
    main()