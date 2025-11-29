from abstractions.Process import Process, ProcessState
from abstractions.Command import *
from devices.Memory import *
from devices.ALU import ALU
from managers.InterruptHandler import Interrupt, InterruptHandler, InterruptType


# класс-перечисление состояний процессора
class CPUState(Enum):
    IDLE = 0  # простаивает
    RUNNING = 1  # работает


class CPU:
    def __init__(self, memory_ptr: Memory, device_id: int, quantum_size: int) -> None:
        self.device_id = device_id  # ID устройства
        self.current_state = CPUState.IDLE  # состояние ЦП
        self._current_process: Optional[Process] = None  # текущий процесс ЦП

        self.ticks_executed = 0  # текущее количество выполненных тактов (для отслеживания кванта)
        self.total_commands_executed = 0  # общее количество выполненных команд (для статистики)

        self.memory_ptr = memory_ptr  # указатель на память

        self.interrupt_handler: Optional[InterruptHandler] = None  # указатель на обработчик прерываний
        self.quantum_size = quantum_size  # размер кванта времени в тактах моделирования

        return

    @property
    def current_process(self) -> Optional[Process]:
        """
        Геттер для процесса
        """
        return self._current_process

    @current_process.setter
    def current_process(self, proc: Optional[Process]) -> None:
        """
        Сеттер для процесса. Выставляет соответствующее состояние для ЦП
        :param proc: процесс для выставления на ЦП
        """
        self._current_process = proc
        if proc is None:
            self.current_state = CPUState.IDLE
            self.ticks_executed = 0

        else:
            self.current_state = CPUState.RUNNING

    def read_operand(self, addr: int) -> int:
        """
        Чтение операнда из памяти по адресу
        :param addr: адрес операнда
        :return: операнд
        """
        return self.memory_ptr.read(addr)

    def write_result(self, value: int, addr: int) -> None:
        """
        Записывает результат операции в память
        :param value: значение результата
        :param addr: адрес для записи
        """
        self.memory_ptr.write(value, addr)

    def execute_tick(self) -> None:
        """
        Выполняет один такт текущего процесса
        """
        if self.current_process is None or self.current_process.current_state == ProcessState.TERMINATED:
            return
        self.total_commands_executed += 1
        self.ticks_executed += 1
        if self.ticks_executed == self.quantum_size:
            interrupt = Interrupt(InterruptType.QUANTUM_ENDED, self.current_process.pid, self.device_id)
            self.interrupt_handler.raise_interrupt(interrupt)
            return
        command = self.current_process.generate_command()
        match command:
            case ALUCommand(addr1=addr1, addr2=addr2, opType=opType):
                op_1 = self.read_operand(addr1)
                op_2 = self.read_operand(addr2)
                result = ALU.execute_operation(operation_type=opType, operand_1=op_1, operand_2=op_2)
                self.write_result(result, self.current_process.process_memory_config.result_block_address)
                self.current_process.process_statistics.total_commands_counter += 1
            case ExitCommand():
                interrupt = Interrupt(InterruptType.PROCESS_TERMINATED,
                                      self.current_process.pid, self.device_id)
                self.interrupt_handler.raise_interrupt(interrupt)
            case IOCommand():
                self.current_process.process_statistics.io_commands_counter += 1
                self.current_process.process_statistics.total_commands_counter += 1
                interrupt = Interrupt(InterruptType.PROCESS_IO_INIT,
                                      self.current_process.pid, self.device_id)
                self.interrupt_handler.raise_interrupt(interrupt)
            case _:
                raise RuntimeError("Неизвестный тип команды")