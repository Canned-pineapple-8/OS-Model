from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from devices.CPU import CPU, CPUState
from devices.IOController import IOController, IOControllerState


class InterruptType(Enum):
    QUANTUM_ENDED = 0
    PROCESS_TERMINATED = 1
    PROCESS_IO_INIT = 2
    PROCESS_IO_END = 3


class Interrupt:
    def __init__(self, type: InterruptType, pid_process: int, device_called_id: int):
        self.pid_process = pid_process
        self.type = type
        self.device_called_id = device_called_id
