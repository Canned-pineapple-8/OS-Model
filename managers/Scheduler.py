from collections import deque
from typing import Optional, Deque
from abstractions.Statistics import Statistics, ProcessTimeRecordType


class Scheduler:
    def __init__(self, stats: Statistics) -> None:
        """
        Инициализация планировщика
        """
        self.stats: Statistics = stats
        self.cpu_queue: Deque[int] = deque()
        self.io_queue: Deque[int] = deque()
        return

    def add_process_to_cpu_queue(self, process_pid: int) -> None:
        """
        Добавляет процесс в конец очереди.
        """
        self.stats.add_time_os_multi(self.stats.time_costs.t_global)
        self.stats.add_sys_time_os_multi(self.stats.time_costs.t_global)

        self.cpu_queue.append(process_pid)

    def get_process_from_cpu_queue(self) -> Optional[int]:
        """
        Извлекает процесс из головы очереди и возвращает PID или возвращает None, если пуста
        :return: int
        """
        if not self.cpu_queue:
            return None
        self.stats.add_time_os_multi(self.stats.time_costs.t_next)
        self.stats.add_time_os_multi(self.stats.time_costs.t_global)
        self.stats.add_sys_time_os_multi(self.stats.time_costs.t_global + self.stats.time_costs.t_next)

        return self.cpu_queue.popleft()

    def add_process_to_io_queue(self, process_pid: int) -> None:
        """
        Добавляет процесс в конец очереди.
        """
        self.io_queue.append(process_pid)
        self.stats.add_time_os_multi(self.stats.time_costs.t_global)
        self.stats.add_sys_time_os_multi(self.stats.time_costs.t_global)

    def get_process_from_io_queue(self) -> Optional[int]:
        """
        Извлекает процесс из головы очереди и возвращает PID или возвращает None, если пуста
        :return: int
        """
        if not self.io_queue:
            return None
        self.stats.add_time_os_multi(self.stats.time_costs.t_global)
        self.stats.add_sys_time_os_multi(self.stats.time_costs.t_global)

        return self.io_queue.popleft()

