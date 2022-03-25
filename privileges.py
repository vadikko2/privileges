from json import dumps, JSONEncoder
from typing import Any, Optional, Dict, List
from uuid import uuid4

from bits import Bit
from events import EventsBitValues, EventReverser


class Privilege:
    """
    Привилегия (элемент в цепочке иерархических привилегий).
    Содержит в себе:
    1. Последовательность Bit, задающую правила
    2. UID идентификатор того, на кого эти правила распространяются
    3. Ссылку на родительский объект (вышестоящие правила относительно того же объекта с идентификатором UID)
    Предоставляет:
    1. Фабричные методы создания объектов на основе родителя
    2. API работы с объектом (сравнение, получение совместной привилегии, изменение объекта)
    3. API по получения состояния (отображения) объекта в разных форматах (дерево наследования, обычный JSON,
    для вывода на экран, в числовом формате для записи в базу)
    """
    __slots__ = ('_bits', '_uid', '_parent')

    def __init__(self, bits: List[Optional[Bit]], parent: Optional['Privilege'] = None, uid: Any = uuid4()):
        empty_bits = len(EventsBitValues) - len(bits)
        self._parent = parent
        self._bits = Privilege._fill_none_bits(
            bits_sequence=bits + [Bit.false, ] * empty_bits,
            parent=self._parent
        )[: len(EventsBitValues)]

        self._uid = uid  # на кого ссылается данное правило

    @staticmethod
    def _fill_none_bits(
            bits_sequence: List[Optional[Bit]],
            parent: Optional['Privilege']
    ) -> List[Optional[Bit]]:
        """Заполнение значениями пустых бит"""
        # если есть родитель - берем значения у него
        if isinstance(parent, Privilege):
            return list(map(
                lambda bit: parent.get_bit(bit) if bits_sequence[bit.value] is None else bits_sequence[bit.value],
                EventsBitValues
            ))
        # в противном случае берем дефолтное значение Bit.false
        return list(map(lambda x: Bit.false if x is None else x, bits_sequence))

    def get_bit(self, bit_name: EventsBitValues):
        """Получение бита по номеру"""
        return self.value[bit_name.value]

    def set_bit(self, bit_name: EventsBitValues, bit: Bit) -> None:
        """Установка бита по номеру"""
        self._bits[bit_name.value].bit = bit.bit

    @classmethod
    def create_privilege(
            cls, privileges: Dict[EventsBitValues, Bit],
            parent_privileges: Optional['Privilege'] = None,
            uid: Optional[Any] = None
    ):
        """Фабричный метод создания объекта на основе
        списка Bit объектов и/или родительского объекта"""
        if not privileges and isinstance(parent_privileges, Privilege):
            return cls(
                bits=list(parent_privileges.value),
                uid=parent_privileges.uid if uid is None else uid,
                parent=parent_privileges
            )

        result = [Bit.false] * len(EventsBitValues)
        for bit in EventsBitValues:
            if bit in privileges:
                result[bit.value] = privileges.get(bit)
            else:
                if parent_privileges:
                    result[bit.value] = parent_privileges.get_bit(bit)
        if not uid:
            if isinstance(parent_privileges, Privilege):
                uid = parent_privileges.uid
            else:
                raise ValueError('UID mast be specified if not specified parent_privileges')
        return cls(result, uid=uid, parent=parent_privileges)

    @classmethod
    def from_int(
            cls, value: int,
            uid: Optional[Any]
    ):
        """
        Фабричный метод создания объекта на основе первых 10 бит int числа
        """
        bits = Privilege.int_to_bits(value)
        if not uid:
            raise ValueError('UID mast be specified if not specified parent_privileges')

        return Privilege(bits=bits, uid=uid)

    @staticmethod
    def int_to_bits(value: int) -> List[Bit]:
        bits = [Bit.false] * len(EventsBitValues)  # type: List[Bit]
        bit_string = format(value, '010b')
        for bit in EventsBitValues:
            if bit_string[bit.value] == '1':
                bits[bit.value] = Bit.true
        return bits

    @staticmethod
    def as_json(pr: 'Privilege'):
        """Переводит значение в человеко-читаемый вид"""
        return {
            str(bit.name): pr._bits[bit.value].bit
            for bit in EventsBitValues
        }

    @staticmethod
    def as_tree(pr: Optional['Privilege']):
        """Выстраивает все дерево (вверх) до корня"""
        if pr is None:
            return

        return {
            'parent': Privilege.as_tree(pr.parent),
            'uid': pr.uid,
            'value': Privilege.as_json(pr)
        }

    def __int__(self):
        """Представление в виде числа [0, 1023] (так как задается 10 битами)"""
        return int(''.join(map(lambda bit: str(int(bit.bit)), self.value)), base=2)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '%s %s' % (
            self.uid, dumps(Privilege.as_json(self), indent=4, sort_keys=True)
        )

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other: 'Privilege'):
        return self.value == other.value

    def __and__(self, other: 'Privilege'):
        """
        Складывает два объекта по правилам привилегий.
        Проверяет у одного Input, а у другого Output на одни и те же услуги и наоборот.
        """
        result_bits = [None, ] * len(EventsBitValues)  # type: List[Optional[Bit]]
        for bit in EventsBitValues:
            result_bits[bit.value] = self.get_bit(bit) & other.get_bit(EventReverser.reverse(bit))
        return Privilege(bits=result_bits)

    @property
    def value(self):
        return self._bits

    @property
    def uid(self):
        return self._uid

    @property
    def parent(self):
        return self._parent


class PrivilegesEncoder(JSONEncoder):
    """JSONEncoder для объектов Privilege (чтобы можно было сделать json.dumps)"""

    def default(self, o: Privilege) -> Any:
        return Privilege.as_tree(o)
