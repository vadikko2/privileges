from json import dumps

from bits import Bit
from notify import Notifier
from privileges import Privilege, EventsBitValues, PrivilegesEncoder

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
    """
    {
        "parent": {
            "parent": {
                "parent": null,
                "uid": "ROOT",
                "value": {
                    "inMsg": true,
                    "inSts": false,
                    "inTel": true,
                    "inVid": false,
                    "inVis": true,
                    "outMsg": false,
                    "outSts": false,
                    "outTel": false,
                    "outVid": false,
                    "outVis": false
                }
            },
            "uid": "FIRST",
            "value": {
                "inMsg": true,
                "inSts": true,
                "inTel": true,
                "inVid": true,
                "inVis": true,
                "outMsg": true,
                "outSts": true,
                "outTel": true,
                "outVid": true,
                "outVis": true
            }
        },
        "uid": "SECOND",
        "value": {
            "inMsg": false,
            "inSts": true,
            "inTel": true,
            "inVid": false,
            "inVis": false,
            "outMsg": true,
            "outSts": true,
            "outTel": true,
            "outVid": true,
            "outVis": true
        }
    }
    """

    print(dumps(empty_child, indent=4, sort_keys=True, cls=PrivilegesEncoder))
    """
    {
        "parent": {
            "parent": null,
            "uid": "ROOT",
            "value": {
                "inMsg": true,
                "inSts": false,
                "inTel": true,
                "inVid": false,
                "inVis": true,
                "outMsg": false,
                "outSts": false,
                "outTel": false,
                "outVid": false,
                "outVis": false
            }
        },
        "uid": "EMPTY",
        "value": {
            "inMsg": true,
            "inSts": false,
            "inTel": true,
            "inVid": false,
            "inVis": true,
            "outMsg": false,
            "outSts": false,
            "outTel": false,
            "outVid": false,
            "outVis": false
        }
    }
    """


    # Пример уведомления ВСЕХ родительских объектов об изменении ROOT

    def callback(obj: Privilege):
        print('Обновился объект %r' % obj)


    Notifier.notify(obj=root, parent_type=Privilege, callback=callback)
    """
    Обновился объект ROOT {
        "inMsg": true,
        "inSts": false,
        "inTel": true,
        "inVid": false,
        "inVis": true,
        "outMsg": false,
        "outSts": false,
        "outTel": false,
        "outVid": false,
        "outVis": false
    }
    Обновился объект EMPTY {
        "inMsg": true,
        "inSts": false,
        "inTel": true,
        "inVid": false,
        "inVis": true,
        "outMsg": false,
        "outSts": false,
        "outTel": false,
        "outVid": false,
        "outVis": false
    }
    Обновился объект FIRST {
        "inMsg": true,
        "inSts": true,
        "inTel": true,
        "inVid": true,
        "inVis": true,
        "outMsg": true,
        "outSts": true,
        "outTel": true,
        "outVid": true,
        "outVis": true
    }
    Обновился объект SECOND {
        "inMsg": false,
        "inSts": true,
        "inTel": true,
        "inVid": false,
        "inVis": false,
        "outMsg": true,
        "outSts": true,
        "outTel": true,
        "outVid": true,
        "outVis": true
    }
    """

    Notifier.notify(first_child, parent_type=Privilege, callback=callback)

    """
    Обновился объект FIRST {
        "inMsg": true,
        "inSts": true,
        "inTel": true,
        "inVid": true,
        "inVis": true,
        "outMsg": true,
        "outSts": true,
        "outTel": true,
        "outVid": true,
        "outVis": true
    }
    Обновился объект SECOND {
        "inMsg": false,
        "inSts": true,
        "inTel": true,
        "inVid": false,
        "inVis": false,
        "outMsg": true,
        "outSts": true,
        "outTel": true,
        "outVid": true,
        "outVis": true
    }
    """
    # Приводим к числовому формату
    print(int(first_child))  # 1023
    print(int(root))  # 289

    # вычисляем совместное значение привилегии
    print(int(first_child & root))  # 0
