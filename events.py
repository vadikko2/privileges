from enum import Enum


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


class EventReversMeta(type):
    """Метакласс, создающий все необходимые атрибуты для EventReverser"""
    _MIN_INPUT_NUMBER = 0
    _MAX_INPUT_NUMBER = 5

    _MIN_OUTPUT_NUMBER = 5
    _MAX_OUTPUT_NUMBER = 10

    @property
    def input(cls):
        return [event for event in EventsBitValues if cls._MIN_INPUT_NUMBER <= event.value < cls._MAX_INPUT_NUMBER]

    @property
    def output(cls):
        return [event for event in EventsBitValues if cls._MIN_OUTPUT_NUMBER <= event.value < cls._MAX_OUTPUT_NUMBER]

    def __init__(cls, name, bases, attrs, **kwargs):
        cls._reverse_map = {
            **{key: value for key, value in zip(cls.input, cls.output)},
            **{key: value for key, value in zip(cls.output, cls.input)}
        }
        super(EventReversMeta, cls).__init__(name, bases, attrs, **kwargs)

    def get(cls, event: 'EventsBitValues') -> 'EventsBitValues':
        return cls._reverse_map.get(event)


class EventReverser(metaclass=EventReversMeta):
    """
    Переводит номер операции в номер обратной операции.
    Например EventsBitValues.inMsg -> EventsBitValues.outMsg.
    Bли наоборот EventsBitValues.outMsg -> EventsBitValues.inMsg.
    """

    @staticmethod
    def reverse(event: EventsBitValues) -> EventsBitValues:
        return EventReverser.get(event)
