class Circuit:
    """
    回路を表すクラス
    量子回路の情報からTQEC回路で必要な情報も生成し, 保持する
    """
    def __init__(self):
        self.bits = []
        self.inputs = []
        self.outputs = []
        self.initializations = []
        self.measurements = []
        self.cnots = []
        self.length = 0

    def add_bits(self, n):
        self.bits.append(n)

    def add_inputs(self, n):
        self.input.append(n)

    def add_outputs(self, n):
        self.outputs.append(n)

    def add_initializations(self, dic):
        self.initializations.append(dic)

    def add_measurements(self, dic):
        self.measurements.append(dic)

    def add_cnots(self, dic):
        self.cnots.append(dic)

    def update(self):
        """
        量子回路情報からTQEC回路に必要な情報を更新する
        """
        self.length = len(self.cnots) * 2

    def debug(self):
        print("bits :", self.bits)
        print("inputs :", self.inputs)
        print("outputs :", self.outputs)
        print("init :", self.initializations)
        print("mesur :", self.measurements)
        print("cnots :", self.cnots)
