#!/bin/sh

qubits=(5 10 15 20)
gates=(5 10 15 20 25 30)

for q in ${qubits[@]}
do
    for g in ${gates[@]}
    do
        for i in {1..3}
        do
            echo "------------------------" >> result_table
            cd ./data
            python3 circuit_generator.py -q $q -g $g >> ../result_table
            cd ..
            python3 main.py -i circuit.json >> result_table
            echo "" >> result_table
        done
    done
done