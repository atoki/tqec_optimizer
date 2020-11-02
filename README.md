# TQEC Optimizer
This program generates a TQEC circuit from an arbitrary quantum circuit and optimizes it automatically.

## Requirements
* Python 3.0 or later
* docopt

## Usage
With the JSON file representing an arbitrary quantum circuit as input, the output is a JSON file in the input format of tqec_viewer.
```
$ python3 main.py -i [file.json] -o [file.json] -t [primal or dual]
```
The following commands are used to execute the braidpack method
```
$ python3 main.py -b -i [file.json] -o [file.json]
```

## Example
The following is an example of an experiment using a Y-state distillation circuit.
```
$ python3 main.py -i y.json -o out.json
```
The output JSON file can be visualized using [tqec_viewer](https://github.com/atoki/tqec_viewer).

## Project layout
```
.
├── data                # Benchmark data for experiments
└── tqec_optimizer      
    ├── braidpack       # Braidpack method
    ├── relocation      # Reducing Loops 
    └── transformation  # Proposed method
```