from enum import Enum, auto
from Process import Process, ProcessState
from typing import Optional


# класс-перечисления состояний процессора
class CPUState(Enum):
    IDLE = 0  # простаивает
    RUNNING = 1  # работает
    WAITING = 2  # ожидает (на будущее, возможно, ожидание команд ввода-вывода)


class CPU:
    def __init__(self) -> None:
        self.current_state = CPUState.IDLE
        self.current_process: Optional[Process] = None

        self.ticks_executed = 0
        self.total_commands_executed = 0
        return

    def execute_tick(self) -> None:
        """
        Выполняет один такт текущего процесса (вызывает соответствующий метод процесса)
        :return: количество оставшихся команд процесса (для отслеживания, выполнен он или нет)
        """
        if self.current_process is None or self.current_process.current_state == ProcessState.TERMINATED:
            return
        self.current_process.execute_tick()
        self.total_commands_executed += 1
        self.ticks_executed += 1

    def is_process_finished(self) -> bool:
        """
        Проверяет, выполнен ли текущий процесс ЦП
        :return: bool (True если выполнен/не загружен)
        """
        if self.current_process is None:
            return True
        if self.current_process.current_state == ProcessState.TERMINATED:
            return True
        return False
