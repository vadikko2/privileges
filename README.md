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
root.set(bit_name=EventsBitValues.outSts, bit=Bit.false)
assert first_child.get(EventsBitValues.outSts) is second_child.get(EventsBitValues.outSts)

# если у потомка было переопределено свое значение, после изменения у родителя - у потомка ничего не изменения
root.set(bit_name=EventsBitValues.inVis, bit=Bit.true)
assert first_child.get(EventsBitValues.inVis) is not second_child.get(EventsBitValues.inVis)
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

7. Пример уведомления ВСЕХ родительских объектов об изменении объекта `Privilege`

Реализуем класс с уведомлениями при помощи декоратора `@Notifier.notify(callback=print_callback)`

```python
class NotifyingPrivileges(Privilege):
    """
    Реализует уведомление всех родительских объектов об изменении привилегии
    """

    @Notifier.notify(callback=print_callback)
    def set(self, *args, **kwargs) -> None:
        """Уведомляет всех родителей при внесении изменений в привилегию"""
        return super(NotifyingPrivileges, self).set(*args, **kwargs)
```

Создаем новые объекты класса `NotifyingPrivileges`. Наследуем друг от друга.

```python
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
```

Изменяем объект `ROOT_`

```python
root_.set(EventsBitValues.inVis, Bit.false)
```

Ловим уведомление об изменении у родительских объектов

```text
Обновился объект ROOT_ {
    "inMsg": false,
    "inSts": true,
    "inTel": false,
    "inVid": false,
    "inVis": false,
    "outMsg": false,
    "outSts": true,
    "outTel": false,
    "outVid": false,
    "outVis": true
}
Обновился объект FIRST_ {
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
Обновился объект SECOND_ {
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
Обновился объект EMPTY_ {
    "inMsg": false,
    "inSts": true,
    "inTel": false,
    "inVid": false,
    "inVis": false,
    "outMsg": false,
    "outSts": true,
    "outTel": false,
    "outVid": false,
    "outVis": true
}
```

Изменяем объект `FIRST_`

```python
first_child_.set(EventsBitValues.inVis, Bit.true)
```

Ловим уведомление об изменении у родительских объектов

```text
Обновился объект FIRST_ {
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
Обновился объект SECOND_ {
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
print(int(root & first_child))  # 289
```

10. Сгенерируем `Privilege` из `int`

```python
from_int = Privilege.from_int(289, uid='FROM INT')
assert root == from_int  # True
print(from_int)
```

```text
FROM INT {
    "inMsg": false,
    "inSts": true,
    "inTel": false,
    "inVid": false,
    "inVis": true,
    "outMsg": false,
    "outSts": false,
    "outTel": false,
    "outVid": false,
    "outVis": true
}
```