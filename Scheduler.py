from collections import deque
from Process import Process, ProcessState
from CPU import CPU, CPUState
from typing import Optional


class Scheduler:
    def __init__(self, proc_table: dict, quantum_size:int) -> None:
        """
        Инициализация планировщика (пустой очереди процессов)
        """
        self.process_queue = deque()  # очередь на исполнение процессов: deque [Process]
        self.proc_table_ptr = proc_table # ссылка на таблицу процессов
        self.quantum_size = quantum_size
        return

    def change_process_state(self, process: Process, new_process_state: ProcessState):
        process.current_state = new_process_state

    def add_process_to_queue(self, process_pid: int) -> None:
        """
        Добавляет новый процесс в очередь. Проверки на допустимое количество процессов нет, т.к. это возлагается
        на вызывающий метод
        :param process: процесс для добавления
        """
        # ??? process = ready
        self.process_queue.append(process_pid)
        return

    def get_process_from_queue(self) -> Optional[int]:
        """
        Извлекает следующий на исполнение процесс из головы очереди
        :return:
        """
        if not self.process_queue:
            return None
        process_pid = self.process_queue.popleft()
        return process_pid

    def save_process_state_word(self, process_pid:int, process_state_word: Process) -> None:
        self.proc_table_ptr[process_pid] = process_state_word
        return

    def restore_process_state_word(self, process_pid:int) -> Process:
        return self.proc_table_ptr[process_pid]

    def load_task(self, cpu:CPU, process_pid:int) -> None:
        """
        Загружает процесс на исполнение переданному ЦП, выставляет необходимые состояния ЦП и процесса
        :param cpu: процессор, в который будет загружена задача
        :param process: процесс для загрузки
        """
        process = self.restore_process_state_word(process_pid)
        cpu.current_process = process
        self.change_process_state(process, ProcessState.RUNNING)
        cpu.current_state = CPUState.RUNNING
        return

    def unload_task(self, cpu:CPU) -> int:
        """
        Освобождает переданный ЦП от текущего процесса
        :param cpu: процессор для освобождения
        :return: старый выгруженный процесс
        """
        process = cpu.current_process
        self.save_process_state_word(process.pid, process)
        cpu.current_process = None
        cpu.current_state = CPUState.IDLE
        return process.pid

    def dispatch(self, cpu:CPU) -> None:
        """
        Проверяет состояние процессора и загружает его новым процессом при необходимости
        :param cpu: ЦП для проверки
        """
        if cpu.current_state is CPUState.RUNNING and cpu.ticks_executed >= self.quantum_size:
            self.change_process_state(cpu.current_process, ProcessState.READY)
            unloaded_process_pid = self.unload_task(cpu)
            self.add_process_to_queue(unloaded_process_pid)
            cpu.ticks_executed = 0
        if cpu.current_state is CPUState.IDLE and self.process_queue:
            next_process = self.get_process_from_queue()
            self.load_task(cpu, next_process)



