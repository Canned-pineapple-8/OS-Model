from enum import Enum, auto
from Process import Process, ProcessState
from typing import Optional
from EventBus import *


# класс-перечисления состояний процессора
class CPUState(Enum):
    IDLE = 0  # простаивает
    RUNNING = 1  # работает
    WAITING = 2  # ожидает (на будущее, возможно, ожидание команд ввода-вывода)
    STOPPED = 3  # остановлен (не работает)


class CPU:
    def __init__(self, event_bus: EventBus) -> None:
        self.current_state = CPUState.IDLE
        self.current_process: Optional[Process] = None
        self.total_commands_executed = 0
        self.event_bus = event_bus
        return

    def load_task(self, process:Process) -> None:
        """
        Загружает процесс на исполнение и переходит в состояние RUNNING
        :param process: процесс для загрузки
        """
        self.current_process = process
        self.current_process.current_state = ProcessState.RUNNING
        self.current_state = CPUState.RUNNING
        return

    def unload_task(self) -> None:
        """
        Сбрасывает текущий процесс и переходит в состояние IDLE
        """
        self.current_process = None
        self.current_state = CPUState.IDLE
        return

    def execute_tick(self) -> None:
        """
        Выполняет один такт текущего процесса.
        Увеличивает счетчик команд, обновляет состояние процесса и освобождает CPU,
        если процесс завершен.
        """
        if self.current_process is None or self.current_process.current_state == ProcessState.TERMINATED:
            return
        self.current_process.execute_tick()
        self.total_commands_executed += 1
        if self.current_process.current_state == ProcessState.TERMINATED:
            self.event_bus.emit(EventType.PROCESS_TERMINATED, process_pid=self.current_process.pid)
            self.unload_task()
        return

    def get_current_process(self) -> Process:
        """
        Возвращает текущий исполняемый процесс
        :return:
        """
        return self.current_process
