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
import random
import json


def main():
    args = docopt(__doc__)
    n_qubit = int(args['--qubit'][0])
    n_gate = int(args['--gate'][0])
    output_file = args['--output'][0]

    print("{}qubit  {}gates".format(n_qubit, n_gate))

    qubit_list = [n for n in range(0, n_qubit)]
    output_list = [n for n in range(0, n_qubit)]
    init_list = []
    meas_list = []
    cnot_list = []

    for n in range(0, n_qubit):
        basis = "x" if random.randint(0, 1) == 0 else "z"
        dict = {"bit": n,
                "type": basis}
        init_list.append(dict)

    for n in range(0, n_gate):
        control = random.randint(0, n_qubit - 1)
        target = control
        while target == control:
            target = random.randint(0, n_qubit - 1)
        target_list = [target]
        dict = {"type": "cnot",
                "control": control,
                "targets": target_list}
        cnot_list.append(dict)

    data = {"bits": qubit_list,
            "outputs": output_list,
            "initializations": init_list,
            "measurements": meas_list,
            "operations": cnot_list}

    with open(output_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)


if __name__ == '__main__':
    main()