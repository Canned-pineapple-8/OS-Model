from enum import Enum
from Memory import Memory
from RandomFactory import RandomFactory
from Command import *
from typing import *

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

    def __init__(self, ph_memory_ptr: Memory, memory: int = 10, regular_commands_size: int = 10, io_commands_percentage: float = 0.5) -> None:
        """
        Инициализация процесса
        :param pid: идентификатор процесса (целое неотрицательное число)
        :param memory: минимальная память, необходимая для процесса (целое неотрицательное число)
        """
        self.memory_ptr = ph_memory_ptr
        self.pid = Process.free_pid  # свободное значение PID Для новых процессов
        Process.free_pid += 1
        self.memory = memory
        self.commands_size = regular_commands_size
        self.io_commands_percentage = io_commands_percentage

        self._current_state = ProcessState.NEW

        self.commands_counter = 0
        self.io_commands_counter = 0

        self.current_command: Optional[Command] = None

        self.command_result_address = -1
        self.block_start_address = -1
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

    def generate_command(self) -> Command:
        if self.commands_size - self.commands_counter <= 0:
            self.current_command = ExitCommand()
        percent = RandomFactory.generate_random_float_value(0.0, 1.0)
        if percent < self.io_commands_percentage:
            io_command_length = RandomFactory.generate_random_int_value(3, 5)
            self.current_command = IOCommand(io_command_length)
        else:
            op_1_address = self.block_start_address
            op_2_address = self.block_start_address + 1

            op_1 = RandomFactory.generate_random_int_value(1, 10)
            op_2 = RandomFactory.generate_random_int_value(1, 10)
            self.memory_ptr.write(op_1, op_1_address)
            self.memory_ptr.write(op_2, op_2_address)

            op_type = RandomFactory.generate_random_int_value(0, len(OpType) - 1)

            self.current_command = ALUCommand(op_1_address, op_2_address, OpType(op_type))
        return self.current_command


