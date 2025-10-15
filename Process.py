from enum import Enum


class ProcessState(Enum):
    NEW = 0
    READY = 1
    RUNNING = 2
    TERMINATED = 3


class Process:
    free_pid = 0

    def __init__(self, memory: int = 10, regular_commands_size: int = 10, io_commands_percentage: float = 0.5, priority: int = 0) -> None:
        """
        Инициализация процесса
        :param pid: идентификатор процесса (целое неотрицательное число)
        :param memory: минимальная память, необходимая для процесса (целое неотрицательное число)
        """
        self.pid = Process.free_pid  # свободное значение PID Для новых процессов
        Process.free_pid += 1
        self.memory = memory
        self.regular_commands_size = regular_commands_size
        self.io_commands_percentage = io_commands_percentage
        self.priority = priority

        self._current_state = ProcessState.NEW

        self.regular_commands_counter = 0
        self.io_commands_counter = 0
        return

    @property
    def current_state(self) -> ProcessState:
        return self._current_state

    @current_state.setter
    def current_state(self, state) -> None:
        if not isinstance(state, ProcessState):
            raise ValueError("Неверное состояние процесса")
        self._current_state = state
        return

    def execute_tick(self) -> None:
        """
        Выполнить такт процесса (увеличение счётчика команд процесса на единицу)
        :return:
        """
        if self.regular_commands_size <= 0:
            self.current_state = ProcessState.TERMINATED
            return
        self.regular_commands_counter += 1
        if self.regular_commands_counter >= self.regular_commands_size:
            self.current_state = ProcessState.TERMINATED
        return

