class Circuit:
    """
    回路を表すクラス
    量子回路の情報からTQEC回路で必要な情報も生成し, 保持する
    """
    def __init__(self):
        self._bits = []
        self._inputs = []
        self._outputs = []
        self._initializations = []
        self._measurements = []
        self._operations = []
        self._length = 0
        self._width = 0

    @property
    def length(self):
        return self._length

    @property
    def width(self):
        return self._width

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def initializations(self):
        return self._initializations

    @property
    def measurements(self):
        return self._measurements

    @property
    def operations(self):
        return self._operations

    def add_bits(self, n):
        self._bits.append(n)

    def add_inputs(self, n):
        self._inputs.append(n)

    def add_outputs(self, n):
        self._outputs.append(n)

    def add_initializations(self, dic):
        self._initializations.append(dic)

    def add_measurements(self, dic):
        self._measurements.append(dic)

    def add_operations(self, dic):
        self._operations.append(dic)

    def update(self):
        """
        量子回路情報からTQEC回路に必要な情報を更新する
        """
        length = 0
        for operation in self._operations:
            if operation["type"] == "cnot":
                length += 1

        self._length = length * 4
        self._width = len(self._bits) * 2

    def debug(self):
        print("bits :", self._bits)
        print("inputs :", self._inputs)
        print("outputs :", self._outputs)
        print("init :", self._initializations)
        print("mesur :", self._measurements)
        print("operations :", self._operations)
