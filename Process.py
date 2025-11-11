from enum import Enum

class ProcessState(Enum):
    NEW = 0  # только создан ("загружается")
    READY = 1  # готов к выполнению ("готов")
    RUNNING = 2  # выполняется ("активен")
    TERMINATED = 3  # завершен ("отсутствует")
    IO_INIT = 4  # инициализация ввода-вывода
    IO_END = 5  # конец ввода-вывода
    MEM_BLOCKED = 6  # блокирован по обращению к памяти
    IO_BLOCKED = 7  # блокирован по вводу-выводу
    STOPPED = 8  # приостановлен


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
        self.commands_size = regular_commands_size
        self.io_commands_percentage = io_commands_percentage

        self._current_state = ProcessState.NEW

        self.commands_counter = 0
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
        self.commands_counter += 1
        if self.commands_size - self.commands_counter <= 0:
            self.current_state = ProcessState.TERMINATED

