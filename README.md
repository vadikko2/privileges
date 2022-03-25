# Иерархическое представление прав

### Описание

Реализация иерархического представления прав (далее привилегии) на оказание услуг между абонентами.

Перечень предоставляемых услуг приведен ниже:

```python
class EventsBitValues(Enum):
    """Enum с номерами битов в соответствии с операциями"""
    # Input
    inMsg = 0  # получение текстовых сообщений
    inSts = 1  # получение статуса присутствия
    inTel = 2  # получение телефонных звонков
    inVid = 3  # получение видео звонков
    inVis = 4  # видимость в адресной книге
    # Output
    outMsg = 5  # отправка текстовых сообщений
    outSts = 6  # отправка статуса присутствия
    outTel = 7  # отправка телефонных звонков
    outVid = 8  # отправка видео звонков
    outVis = 9  # видимость в адресной книге
```

Привилегии представлены в виде дерева наследования.

Каждый узел дерева наследует привилегии вышестоящего узла, если привилегия текущего узла явно не определена.

Если привилегия не определена вверх до самого корня - значение по-умолчанию `Bit.false`.

### Пример

1. Определяем корневого родителя

```python 
root = Privilege(
    bits=[None, Bit.true, Bit.false, None, Bit.true, Bit.false, Bit.true, None, None, Bit.true],
    uid='ROOT'
)
```

2. Наследуемся от root и переопределяем привилегии

```python 
first_child = Privilege.create_privilege(
    privileges={key: Bit.true for key in EventsBitValues},
    parent_privileges=root, uid='FIRST'
)
```

3. Наследуемся от root, но не переопределяем привилегии

```python 
empty_child = Privilege.create_privilege({}, parent_privileges=root, uid='EMPTY')
```

4.Наследуем от first_child и переопределяем парочку привилегий

```python
second_child = Privilege.create_privilege(
    {key: Bit.false for key in [
        EventsBitValues.inVis,
        EventsBitValues.inVid,
        EventsBitValues.inMsg
    ]}, parent_privileges=first_child, uid='SECOND'
)
```

5. Проводим несколько проверок

```python
# проверяем, что EMPTY совпадает с ROOT 
assert empty_child == root  # True

# если поменять у родителя то, что потомок унаследовал - у потомка тоже изменится
root.set_bit(bit_name=EventsBitValues.outSts, bit=Bit.false)
assert first_child.get_bit(EventsBitValues.outSts) is second_child.get_bit(EventsBitValues.outSts)

# если у потомка было переопределено свое значение, после изменения у родителя - у потомка ничего не изменения
root.set_bit(bit_name=EventsBitValues.inVis, bit=Bit.true)
assert first_child.get_bit(EventsBitValues.inVis) is not second_child.get_bit(EventsBitValues.inVis)
```

6. Выводим на экран дерево наследования привилегий

```python
print(dumps(second_child, indent=4, sort_keys=True, cls=PrivilegesEncoder))
```

```json
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
```

```python
print(dumps(empty_child, indent=4, sort_keys=True, cls=PrivilegesEncoder))
```

```json
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
```

7. Пример уведомления ВСЕХ родительских объектов об изменении ROOT (класс `notify.Notifier`)

```python
def callback(obj: Privilege):
    print('Обновился объект %r' % obj)


Notifier.notify(obj=root, parent_type=Privilege, callback=callback)
```

```text
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
```

```python
Notifier.notify(first_child, parent_type=Privilege, callback=callback)
```

```text
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
```

8. Приведем привилегии к численным значениям, в котором их удобно хранить в базе данных (в виде числа [0..1023], так как
   привилегия кодируется 10 битами)

```python
print(int(first_child))  # 1023
print(int(root))  # 289
```

9. Проверяем результат совместного применения привилегии по правилам:

```text
        Проверяет у одного Input а у другого Output на одни и те же услуги и наоборот.
        Правила разрешения по каждой услуге:
        INPUT  |  OUTPUT  |  RESULT
           0   |    0     |    0
           0   |    1     |    0
           1   |    0     |    0
           1   |    1     |    1
```

```python
print(int(first_child & root))  # 0
```