from collections import deque
from typing import Dict, Optional, Deque
from abstractions.Process import Process
from managers.MemoryManager import MemoryManager


class Scheduler:
    def __init__(self, proc_table: Dict[int, Process], memory_manager: MemoryManager ) -> None:
        """
        Инициализация планировщика
        """
        self.proc_table_ptr = proc_table  # ссылка на таблицу процессов

        self.cpu_queue: Deque[int] = deque()
        self.io_queue: Deque[int] = deque()

        self.memory_manager: MemoryManager = memory_manager  # менеджер памяти
        return

    def add_process_to_cpu_queue(self, process_pid: int) -> None:
        """
        Добавляет процесс в конец очереди.
        """
        self.cpu_queue.append(process_pid)

    def get_process_from_cpu_queue(self) -> Optional[int]:
        """
        Извлекает процесс из головы очереди и возвращает PID или возвращает None, если пуста
        :return: int
        """
        if not self.cpu_queue:
            return None
        return self.cpu_queue.popleft()

    def add_process_to_io_queue(self, process_pid: int) -> None:
        """
        Добавляет процесс в конец очереди.
        """
        self.io_queue.append(process_pid)

    def get_process_from_io_queue(self) -> Optional[int]:
        """
        Извлекает процесс из головы очереди и возвращает PID или возвращает None, если пуста
        :return: int
        """
        if not self.io_queue:
            return None
        return self.io_queue.popleft()

