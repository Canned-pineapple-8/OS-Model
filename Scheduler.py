from collections import deque
from Process import Process, ProcessState
from CPU import CPU, CPUState
from typing import Optional


class Scheduler:
    def __init__(self) -> None:
        """
        Инициализация планировщика (пустой очереди процессов)
        """
        self.process_queue = deque()  # очередь на исполнение процессов: deque [Process]
        return

    def add_process_to_queue(self, process: Process) -> None:
        """
        Добавляет новый процесс в очередь. Проверки на допустимое количество процессов нет, т.к. это возлагается
        на вызывающий метод
        :param process: процесс для добавления
        """
        if process.current_state != ProcessState.TERMINATED:
            process.current_state = ProcessState.READY
            self.process_queue.append(process)
        return

    def get_process_from_queue(self) -> Optional[Process]:
        """
        Извлекает следующий на исполнение процесс из головы очереди
        :return:
        """
        if not self.process_queue:
            return None
        process = self.process_queue.popleft()
        return process

    def load_task(self, cpu:CPU, process: Process) -> None:
        """
        Загружает процесс на исполнение переданному ЦП, выставляет необходимые состояния ЦП и процесса
        :param cpu: процессор, в который будет загружена задача
        :param process: процесс для загрузки
        """
        cpu.current_process = process
        cpu.current_process.current_state = ProcessState.RUNNING
        cpu.current_state = CPUState.RUNNING
        return

    def unload_task(self, cpu:CPU) -> Process:
        """
        Освобождает переданный ЦП от текущего процесса
        :param cpu: процессор для освобождения
        :return: старый выгруженный процесс
        """
        cpu.current_process.current_state = ProcessState.TERMINATED
        old_process = cpu.current_process
        cpu.current_process = None
        cpu.current_state = CPUState.IDLE
        return old_process

    def dispatch(self, cpu:CPU) -> None:
        """
        Проверяет состояние процессора и загружает его новым процессом при необходимости
        :param cpu: ЦП для проверки
        """
        if cpu.current_state is CPUState.IDLE and self.process_queue:
            next_process = self.get_process_from_queue()
            self.load_task(cpu, next_process)