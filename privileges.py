import collections
from enum import Enum
from json import dumps, JSONEncoder
from typing import List, Any, Optional, Dict, Iterable
from uuid import uuid4

from bits import Bit


class EventsBitValues(Enum):
    """Enum с номерами битов в соответствии с операциями"""
    # Input
    inMsg = 0
    inSts = 1
    inTel = 2
    inVid = 3
    inVis = 4
    # Output
    outMsg = 5
    outSts = 6
    outTel = 7
    outVid = 8
    outVis = 9


class Privilege:
    __slots__ = ('_bits', '_uid', '_parent')

    def __init__(self, bits: List[Optional[Bit]], parent: Optional['Privilege'] = None, uid: Any = uuid4()):
        empty_bits = len(EventsBitValues) - len(bits)
        self._parent = parent
        self._bits = Privilege._fill_none_bits(
            bits_sequence=collections.deque(bits + [Bit.false, ] * empty_bits, maxlen=len(EventsBitValues)),
            parent=self._parent
        )

        self._uid = uid  # на кого ссылается данное правило

    @staticmethod
    def _fill_none_bits(
            bits_sequence: Iterable[Optional[Bit]],
            parent: Optional['Privilege']
    ) -> Iterable[Optional[Bit]]:
        if isinstance(parent, Privilege):
            return list(
                map(lambda x: parent.get_bit(EventsBitValues(x[0])) if x[1] is None else x[1], enumerate(bits_sequence))
            )
        return list(map(lambda x: Bit.false if x is None else x, bits_sequence))

    def get_bit(self, bit_name: EventsBitValues):
        return self._bits[bit_name.value]

    def set_bit(self, bit_name: EventsBitValues, bit: Bit) -> None:
        self._bits[bit_name.value].bit = bit.bit

    @classmethod
    def create_privilege(
            cls, privileges: Dict[EventsBitValues, Bit],
            parent_privileges: Optional['Privilege'] = None,
            uid: Optional[Any] = None
    ):
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
        Проверяет у одного Input а у другого Output на одни и те же услуги и наоборот.
        Правила разрешения по каждой услуге:
        INPUT  |  OUTPUT  |  RESULT
           0   |    0     |    0
           0   |    1     |    0
           1   |    0     |    0
           1   |    1     |    1
        """
        return Privilege(bits=[Bit.false for _ in EventsBitValues])  # todo

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

    def default(self, o: Privilege) -> Any:
        return Privilege.as_tree(o)
