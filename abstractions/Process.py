from enum import Enum
from devices.Memory import Memory
from utils.RandomFactory import RandomFactory
from abstractions.Command import Command, IOCommand, ExitCommand, ALUCommand, OpType
from dataclasses import dataclass
from abstractions.Statistics import ProcessTimeStats

class ProcessState(Enum):
    NEW = 0  # только создан ("загружается")
    READY = 1  # готов к выполнению ("готов")
    RUNNING = 2  # выполняется ("активен")
    TERMINATED = 3  # завершен ("отсутствует")
    IO_INIT = 4  # инициализация ввода-вывода
    IO_END = 5  # конец ввода-вывода
    STOPPED_IO = 6  # приостановлен (был на IO)
    IO_BLOCKED = 7  # блокирован по вводу-выводу
    STOPPED_CPU = 8  # приостановлен (был на CPU)
    IO_RUNNING = 9  # команда ввода-вывода активно выполняется


@dataclass
class ProcessMemoryConfig:
    """
    Класс-хранилище для параметров процесса, связанных с памятью
    """
    block_start: int = -1  # адрес начало блока памяти, выделенного под процесс
    block_size: int = -1  # размер блока памяти, выделенного под процесс
    operands_block_address: int = -1  # адрес внутри блока памяти процесса, куда записываются операнды
    result_block_address: int = -1  # адрес внутри блока памяти процесса, куда записывается результат


@dataclass
class ProcessStatistics:
    """
    Класс-хранилище для статистики по количеству выполненных команд процесса
    """
    total_commands_counter: int = 0  # общее количество выполненных команд (обычные + IO)
    io_commands_counter: int = 0  # количество выполненных команд ввода-вывода


@dataclass
class ProcessCommandsConfig:
    """
    Класс-хранилище для параметров процесса, связанных с командами
    """
    total_commands_cnt: int = 10  # общее количество команд процесса (обычные + IO)
    io_command_ratio: float = 0.5  # вероятность встретить IO-команду
    io_command_duration_min: int = 1  # минимальная длительность IO-команды
    io_command_duration_max: int = 5  # максимальная длительность IO-команды
    min_operand: int = 1  # минимальное значение операнда для команд ALU
    max_operand: int = 10  # максимальное количество операнда для команд ALU


class Process:
    free_pid = 0

    def __init__(self, ph_memory_ptr: Memory, process_memory_info: ProcessMemoryConfig = None,
                 process_statistics: ProcessStatistics = None,
                 process_commands_config: ProcessCommandsConfig = None
                 ) -> None:
        """
        Инициализация процесса
        :param ph_memory_ptr: указатель на физическую память ОС
        :param process_memory_info: класс-хранилище информации о процессе, связанной с его расположением в памяти
        :param process_statistics: класс-хранилище статистик процесса
        :param process_commands_config: класс-хранилище информации о процессе, связанной с количеством и параметрами команд
        """
        self.memory_ptr = ph_memory_ptr
        self.pid = Process.free_pid  # свободное значение PID Для новых процессов
        Process.free_pid += 1
        self.current_state = ProcessState.NEW # изначальное состояние процесса

        self.process_memory_config = (
            process_memory_info if process_memory_info is not None else ProcessMemoryConfig()
        )
        self.process_statistics = (
            process_statistics if process_statistics is not None else ProcessStatistics()
        )
        self.process_commands_config = (
            process_commands_config if process_commands_config is not None else ProcessCommandsConfig()
        )

        self.stats = ProcessTimeStats()  # статистика
        self.current_command = None  # текущая команда процесса
        return

    def generate_command(self) -> Command:
        """
        Генерация команды
        В случае ALU-команды записывает операнды в память, чтобы в дальнейшем ЦПр мог их оттуда прочитать
        :return: сгенерированная команда
        """
        commands_size = self.process_commands_config.total_commands_cnt
        io_commands_percentage = self.process_commands_config.io_command_ratio
        commands_counter = self.process_statistics.total_commands_counter
        operands_address = self.process_memory_config.operands_block_address

        # если счетчик выполненных команд достиг количества команд процесса -
        # генерируем команду завершения
        if commands_size - commands_counter == 0:
            self.current_command = ExitCommand()
            return self.current_command

        # с заданной вероятностью генерируем IO-команду, иначе - арифметическую
        percent = RandomFactory.generate_random_float_value(0.0, 1.0)
        if percent < io_commands_percentage:
            io_command_length = RandomFactory.generate_random_int_value(self.process_commands_config.io_command_duration_min,
                                                                        self.process_commands_config.io_command_duration_max)
            self.current_command = IOCommand(io_command_length)
        else:
            min_operand, max_operand = self.process_commands_config.min_operand, self.process_commands_config.max_operand
            op_1_address = operands_address
            op_2_address = operands_address + 1

            op_1 = RandomFactory.generate_random_int_value(min_operand, max_operand)
            op_2 = RandomFactory.generate_random_int_value(min_operand, max_operand)
            self.memory_ptr.write(op_1, op_1_address)
            self.memory_ptr.write(op_2, op_2_address)

            op_type = RandomFactory.generate_random_int_value(0, len(OpType) - 1)

            self.current_command = ALUCommand(op_1_address, op_2_address, OpType(op_type))
        return self.current_command


