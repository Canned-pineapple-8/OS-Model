from typing import *
from abstractions.Process import *


# класс-перечисление состояний процессора
class IOControllerState(Enum):
    IDLE = 0  # простаивает
    RUNNING = 1  # работает


class IOController:
    def __init__(self):
        """
        Инициализация IO контроллера
        """
        self.current_state = IOControllerState.IDLE
        self.current_process:Optional[Process] = None
        self.current_ticks_executed: int = 0
        self.total_ticks_executed = 0

    def execute_tick(self) -> None:
        """
        Выполнение одного такта IO процесса
        """
        if self.current_process is None:
            return
        assert isinstance(self.current_process.current_command, IOCommand)
        self.current_ticks_executed += 1
        self.total_ticks_executed += 1
        if self.current_process.current_command.duration == self.current_ticks_executed:
            self.current_process.process_statistics.total_commands_counter += 1
            self.current_process.process_statistics.io_commands_counter += 1
            self.current_process.current_state = ProcessState.IO_END
