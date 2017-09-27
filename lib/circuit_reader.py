import json
from .circuit import Circuit

path = '/Users/Askt/Study/tqec_optimizer/data/'


class CircuitReader:
    """
    量子回路を表したJSONファイルを読み込むためのパーサークラス
    """

    def __init__(self):
        """
        コンストラクタ
        """
        self.circuit = Circuit()

    def read_circuit(self, file_name):
        """
        指定されたJSONファイルを読み込む

        :param string file_name: 読み込むファイル名.
        :return: Circuitクラス
        """

        input_file = path + file_name

        with open(input_file, 'r') as fin:
            data = json.load(fin)

        for key, value in data.items():
            if self.__read_bits(key, value):
                continue

            if self.__read_inputs(key, value):
                continue

            if self.__read_outputs(key, value):
                continue

            if self.__read_initializations(key, value):
                continue

            if self.__read_measurements(key, value):
                continue

            if self.__read_cnots(key, value):
                continue

            self.error('syntax error')

        self.circuit.update()

        return self.circuit

    def __read_bits(self, key, value):
        if key != "bits":
            return False

        for element in value:
            self.circuit.add_bits(element)

        return True

    def __read_inputs(self, key, value):
        if key != "inputs":
            return False

        for element in value:
            self.circuit.add_inputs(element)

        return True

    def __read_outputs(self, key, value):
        if key != "outputs":
            return False

        for element in value:
            self.circuit.add_outputs(element)

        return True

    def __read_initializations(self, key, value):
        if key != "initializations":
            return False

        for element in value:
            self.circuit.add_initializations(element)

        return True

    def __read_measurements(self, key, value):
        if key != "measurements":
            return False

        for element in value:
            self.circuit.add_measurements(element)

        return True

    def __read_cnots(self, key, value):
        if key != "cnots":
            return False

        for element in value:
            self.circuit.add_cnots(element)

        return True
