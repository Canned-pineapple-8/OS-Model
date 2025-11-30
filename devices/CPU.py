from abstractions.Process import Process, ProcessState
from abstractions.Command import *
from devices.Memory import *
from devices.ALU import ALU


# класс-перечисление состояний процессора
class CPUState(Enum):
    IDLE = 0  # простаивает
    RUNNING = 1  # работает


class CPU:
    def __init__(self, memory_ptr: Memory) -> None:
        self.current_state = CPUState.IDLE  # текущее состояние ЦП
        self.current_process: Optional[Process] = None  # текущий процесс на исполнении

        self.ticks_executed = 0  # текущее количество выполненных тактов кванта
        self.total_commands_executed = 0  # общее количество выполненных команд (для статистики)

        self.memory_ptr = memory_ptr  # указатель на память
        return

    def read_operand(self, addr: int) -> Optional[int]:
        """
        Считать значение из памяти по адресу addr
        :param addr: адрес
        :return: считанное значение (int)
        """
        return self.memory_ptr.read(addr)

    def write_result(self, value: int, addr: int) -> None:
        """
        Записывает значение value в память по адресу addr
        :param value: значение для записи
        :param addr: адрес для записи
        """
        self.memory_ptr.write(value, addr)

    def execute_tick(self) -> None:
        """
        Выполняет один такт текущего процесса
        """
        if self.current_process is None or self.current_process.current_state == ProcessState.TERMINATED:
            return
        command = self.current_process.generate_command()  # генерация командф
        match command:
            case ALUCommand(addr1=addr1, addr2=addr2, opType=opType):  # арифметическая команда
                op_1 = self.read_operand(addr1)
                op_2 = self.read_operand(addr2)
                result = ALU.execute_operation(operation_type=opType, operand_1=op_1, operand_2=op_2)
                self.write_result(result, self.current_process.process_memory_config.result_block_address)
                self.current_process.process_statistics.total_commands_counter += 1
            case ExitCommand():  # команда завершения
                self.current_process.current_state = ProcessState.TERMINATED
            case IOCommand():  # команда ввода-вывода
                self.current_process.current_state = ProcessState.IO_INIT
            case _:
                raise RuntimeError("Неизвестный тип команды")
        self.total_commands_executed += 1
        self.ticks_executed += 1

    def is_process_awaits_IO(self) -> bool:
        if self.current_process is None:
            return False
        if self.current_process.current_state == ProcessState.IO_INIT:
            return True
        return False

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
