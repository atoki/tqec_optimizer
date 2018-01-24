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
    def bits(self):
        return self._bits

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
        cnot_length, injector_length = 0, 0
        injector_target = {}
        last_operation = None
        for operation in self._operations:
            if operation["type"] == "cnot":
                cnot_length += 1
                injector_target.clear()
            else:
                if operation["target"] in injector_target:
                    injector_length += 1
                    injector_target.clear()
                injector_target[operation["target"]] = operation["type"]
            last_operation = operation

        # 最後の演算がS or Tで外部出力がある場合は回路を一段階伸ばす
        expand_length = 0
        for output in self._outputs:
            if last_operation["type"] != "cnot" and last_operation["target"] == output:
                expand_length += 2

        self._length = cnot_length * 6 + injector_length * 2 + expand_length
        self._width = len(self._bits) * 2

    def dump(self):
        print("bits :", self._bits)
        print("inputs :", self._inputs)
        print("outputs :", self._outputs)
        print("initializations :", self._initializations)
        print("measurements :", self._measurements)
        print("operations :", self._operations)
