from abstractions.Process import Process, ProcessState
from abstractions.Command import *
from devices.Memory import *
from devices.ALU import ALU


# класс-перечисление состояний процессора
class CPUState(Enum):
    IDLE = 0  # простаивает
    RUNNING = 1  # работает
    WAITING = 2  # ожидает (на будущее, возможно, ожидание команд ввода-вывода)


class CPU:
    def __init__(self, memory_ptr: Memory) -> None:
        self.current_state = CPUState.IDLE
        self.current_process: Optional[Process] = None

        self.ticks_executed = 0
        self.total_commands_executed = 0

        self.memory_ptr = memory_ptr
        return

    def read_operand(self, addr: int) -> int:
        return self.memory_ptr.read(addr)

    def write_result(self, value: int, addr: int) -> None:
        self.memory_ptr.write(value, addr)

    def execute_tick(self) -> None:
        """
        Выполняет один такт текущего процесса (вызывает соответствующий метод процесса)
        :return: количество оставшихся команд процесса (для отслеживания, выполнен он или нет)
        """
        if self.current_process is None or self.current_process.current_state == ProcessState.TERMINATED:
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
                self.current_process.current_state = ProcessState.TERMINATED
            case IOCommand():
                self.current_process.current_state = ProcessState.IO_INIT
                self.current_process.process_statistics.total_commands_counter += 1

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
