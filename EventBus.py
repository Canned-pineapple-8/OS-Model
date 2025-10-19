from enum import Enum, auto
from typing import Callable


class EventType(Enum):
    PROCESS_CREATED = 0
    PROCESS_TERMINATED = 1


class EventBus:
    def __init__(self) -> None:
        self._listeners = {}
        return

    def subscribe(self, event_type: EventType, callback: Callable[..., None]) -> None:
        """
        Подписка на событие event_type.
        callback: функция, которая будет вызвана при событии с аргументами kwargs.
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
        return

    def emit(self, event_type: EventType, **kwargs) -> None:
        """
        Отправка события. Все подписанные на него функции будут выполнены.
        :param event_type: тип события
        :param kwargs: аргументы для вызываемых функций
        """
        for callback in self._listeners.get(event_type, []):
            try:
                callback(**kwargs)
            except Exception as e:
                print(f"Ошибка в callback EventBus: {e}")
        return
