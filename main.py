from json import dumps

from bits import Bit
from callbacks import print_callback
from events import EventsBitValues
from notify import Notifier
from privileges import Privilege, PrivilegesEncoder


class NotifyingPrivileges(Privilege):
    """
    Реализует уведомление всех родительских объектов об изменении привилегии
    """

    @Notifier.notify(callback=print_callback)
    def set_bit(self, *args, **kwargs) -> None:
        """Уведомляет всех родителей при внесении изменений в привилегию"""
        return super(NotifyingPrivileges, self).set_bit(*args, **kwargs)


if __name__ == '__main__':
    # определяем корневого родителя
    root = Privilege(
        bits=[None, Bit.true, Bit.false, None, Bit.true, Bit.false, Bit.true, None, None, Bit.true],
        uid='ROOT'
    )

    # Наследуемся от root и переопределяем привилегии
    first_child = Privilege.create_privilege(
        privileges={key: Bit.true for key in EventsBitValues},
        parent_privileges=root, uid='FIRST'
    )

    # Наследуемся от root, но не переопределяем привилегии
    empty_child = Privilege.create_privilege({}, parent_privileges=root, uid='EMPTY')
    assert empty_child == root  # True

    # Наследуем от first_child и переопределяем парочку привилегий
    second_child = Privilege.create_privilege(
        {key: Bit.false for key in [
            EventsBitValues.inVis,
            EventsBitValues.inVid,
            EventsBitValues.inMsg
        ]}, parent_privileges=first_child, uid='SECOND'
    )

    # если поменять у родителя то, что потомок унаследовал - у потомка тоже изменится
    root.set_bit(bit_name=EventsBitValues.outSts, bit=Bit.false)
    assert first_child.get_bit(EventsBitValues.outSts) is second_child.get_bit(EventsBitValues.outSts)

    # если у потомка было переопределено свое значение, после изменения у родителя - у потомка ничего не изменения
    root.set_bit(bit_name=EventsBitValues.inVis, bit=Bit.true)
    assert first_child.get_bit(EventsBitValues.inVis) is not second_child.get_bit(EventsBitValues.inVis)

    print(dumps(second_child, indent=4, sort_keys=True, cls=PrivilegesEncoder))
    print(dumps(empty_child, indent=4, sort_keys=True, cls=PrivilegesEncoder))

    # Пример уведомления ВСЕХ родительских объектов об изменении ROOT

    root_ = NotifyingPrivileges(
        bits=[None, Bit.true, Bit.false, None, Bit.true, Bit.false, Bit.true, None, None, Bit.true],
        uid='ROOT_'
    )
    first_child_ = NotifyingPrivileges.create_privilege(
        privileges={key: Bit.true for key in EventsBitValues},
        parent_privileges=root_, uid='FIRST_'
    )
    second_child_ = NotifyingPrivileges.create_privilege(
        {key: Bit.false for key in [
            EventsBitValues.inVis,
            EventsBitValues.inVid,
            EventsBitValues.inMsg
        ]}, parent_privileges=first_child_, uid='SECOND_'
    )
    empty_child_ = NotifyingPrivileges.create_privilege({}, parent_privileges=root_, uid='EMPTY_')

    root_.set_bit(EventsBitValues.inVis, Bit.false)
    first_child_.set_bit(EventsBitValues.inVis, Bit.true)
    # Приводим к числовому формату
    print(int(first_child))  # 1023
    print(int(root))  # 289

    # вычисляем совместное значение привилегии
    print(int(root & first_child))  # 289

    # сгенерируем Privilege из int
    from_int = Privilege.from_int(289, uid='FROM INT')
    assert root == from_int
    print(from_int)
