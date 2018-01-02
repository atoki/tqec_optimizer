class Vector3D:
    def __init__(self, x=0, y=0, z=0):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    def set(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    def incx(self, n=1):
        self._x += n

    def decx(self, n=1):
        self._x -= n

    def incy(self, n=1):
        self._y += n

    def decy(self, n=1):
        self._y -= n

    def incz(self, n=1):
        self._z += n

    def decz(self, n=1):
        self._z -= n

    def to_array(self):
        return [self._x, self._y, self._z]

    def debug(self):
        print("pos (", self._x, ",", self._y, ",", self.z, ")")
