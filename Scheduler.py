from collections import deque
from Process import Process, ProcessState
from CPU import CPU, CPUState
from EventBus import *
from typing import Optional

class Scheduler:
    def __init__(self, cpus: list[CPU], event_bus: EventBus) -> None:
        """
        Инициализация параметров планировщика (скорость исполнения и ее размер)
        :param config: словарь json-параметров, результат работы json.load
        """
        self.process_queue = deque()  # очередь на исполнение процессов: deque [Process]
        self.cpus = cpus
        self.event_bus = event_bus
        event_bus.subscribe(EventType.PROCESS_CREATED, self.add_to_queue)
        # event_bus.subscribe(EventType.PROCESS_TERMINATED, self.dispatch)
        return

    def add_to_queue(self, process: Process) -> None:
        """
        Добавляет новый процесс в очередь. Проверки на допустимое количество процессов нет, т.к. это возлагается
        на вызывающий метод
        :param process: процесс для добавления
        """
        if process.current_state != ProcessState.TERMINATED:
            process.current_state = ProcessState.READY
            self.process_queue.append(process)
        return

    def _remove_from_queue(self) -> Optional[Process]:
        """
        Удаляет процесс из очереди.
        :return: экземпляр удалённого из очереди Process
        """
        if not self.process_queue:
            return None
        process = self.process_queue.popleft()
        return process

    def dispatch(self) -> None:
        """
        Проверяет, все ли процессоры заняты. Если есть свободные, назначет им новый процесс на исполнение.
        """
        for cpu in self.cpus:
            if cpu.current_state is CPUState.IDLE and self.process_queue:
                next_process = self._remove_from_queue()
                cpu.load_task(next_process)
        return


