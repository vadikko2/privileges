class BitMeta(type):
    """Метакласс, реализующий фабричные property методы."""

    @property
    def true(cls):
        return cls(True)

    @property
    def false(cls):
        return cls(False)


class Bit(metaclass=BitMeta):
    """Значение бита. Нужно для того, чтобы менять значение привилегии,
    не заменяя объект на новый (чтобы обновлять потомков вместе с родителями)"""
    __slots__ = ('_value',)

    def __init__(self, value: bool):
        self._value = value

    @property
    def bit(self):
        return self._value

    @bit.setter
    def bit(self, value):
        if not isinstance(value, bool):
            raise ValueError('Value must be bool')
        self._value = value

    def __eq__(self, other: 'Bit'):
        return self.bit == other.bit

    def __and__(self, other: 'Bit'):
        """
        Правила разрешения:
        LEFT   |  RIGHT   |  RESULT
           0   |    0     |    0
           0   |    1     |    0
           1   |    0     |    0
           1   |    1     |    1
        """
        if self.bit and other.bit:
            return Bit.true
        else:
            return Bit.false
