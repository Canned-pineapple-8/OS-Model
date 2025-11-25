from typing import *
from abstractions.Process import *


# класс-перечисление состояний процессора
class IOControllerState(Enum):
    IDLE = 0  # простаивает
    RUNNING = 1  # работает


class IOController:
    def __init__(self, device_id: int):
        """
        Инициализация IO контроллера
        """
        self.device_id = device_id
        self.current_state = IOControllerState.IDLE  # состояние контроллера
        self._current_process:Optional[Process] = None  # текущий исполняемый процесс
        self.current_ticks_executed: int = 0  # количество тактов команды ввода-вывода, которое уже выполнено
        self.total_ticks_executed = 0  # общее количество выполенных тактов контроллером (для статистики)

    @property
    def current_process(self) -> Optional[Process]:
        return self._current_process

    @current_process.setter
    def current_process(self, proc: Optional[Process]) -> None:
        self._current_process = proc
        if proc is None:
            self.current_state = IOControllerState.IDLE
            self.current_ticks_executed = 0

        else:
            self.current_state = IOControllerState.RUNNING

    def execute_tick(self) -> None:
        """
        Выполнение одного такта IO процесса
        """
        if self.current_process is None:
            return
        assert isinstance(self.current_process.current_command, IOCommand)  # для контроля,
        # что работаем над командой ввода-вывода
        if self.current_process.current_command.duration == self.current_ticks_executed:
            self.current_process.current_state = ProcessState.IO_END  # сигнал для планировщика
        else:
            self.current_ticks_executed += 1
            self.total_ticks_executed += 1
