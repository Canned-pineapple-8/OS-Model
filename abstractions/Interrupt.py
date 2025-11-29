from enum import Enum


# тип прерывания
class InterruptType(Enum):
    QUANTUM_ENDED = 0  # завершился квант времени процесса
    PROCESS_TERMINATED = 1   # завершился процесс
    PROCESS_IO_INIT = 2  # процесс требует ввода-вывода
    PROCESS_IO_END = 3  # операция ввода-вывода процесса завершилась


class Interrupt:
    def __init__(self, type: InterruptType, pid_process: int, device_called_id: int):
        self.pid_process = pid_process  # PID процесса, вызвавшего прерывание
        self.type = type  # тип прерывания
        self.device_called_id = device_called_id  # ID устройства, вызвавшего прерывание
