# scheduler_module.py
from collections import deque
from typing import Dict, Optional, Deque
from abstractions.Process import Process, ProcessState
from devices.CPU import CPU, CPUState
from devices.IOController import IOController, IOControllerState
from managers.MemoryManager import MemoryManager


class BaseProcessManager:
    """
    Базовый менеджер очереди процессов (общая функциональность для CPU и IO).
    """
    def __init__(self, proc_table_ptr: Dict[int, Process]) -> None:
        self.processes: Deque[int] = deque()  # очередь PID процессов
        self.proc_table_ptr = proc_table_ptr  # указатель на таблицу процессов

    def add_process_to_queue(self, process_pid: int) -> None:
        """
        Добавляет процесс в конец очереди.
        """
        self.processes.append(process_pid)

    def get_process_from_queue(self) -> Optional[int]:
        """
        Извлекает процесс из головы очереди и возвращает PID или возвращает None, если пуста
        :return: int
        """
        if not self.processes:
            return None
        return self.processes.popleft()

    def save_process_state_word(self, process_state_word: Process) -> None:
        """
        Сохраняет слово состояния процесса
        :param process_state_word: слово состояния процесса
        """
        self.proc_table_ptr[process_state_word.pid] = process_state_word

    def restore_process_state_word(self, process_pid: int) -> Process:
        """
        Восстанавливает слово состояния процесса
        :param process_pid: PID процесса
        :return: слово состояния процесса
        """
        return self.proc_table_ptr[process_pid]

    def load_task_from_queue(self, controller) -> None:
        """
        Извлекает процесс из головы очереди
        :param controller: устройство, которому необходимо загрузить процесс на исполнение
        """
        next_pid = self.get_process_from_queue()
        if next_pid is None:
            self._set_controller_idle(controller)  # устанавливаем в IDLE, если очередь пуста
            return
        self.load_task(controller, next_pid)  # вызываем переопределённый метод наследника

    def load_task(self, controller, process_pid: int) -> None:
        """
        абстрактный метод
        """
        raise NotImplementedError

    def unload_task(self, controller) -> int:
        """
        абстрактный метод
        """
        raise NotImplementedError

    def _set_controller_idle(self, controller) -> None:
        """
        Выставляем контроллер в IDLE
        :param controller: CPU/IOController
        """
        try:
            controller.current_state = controller.current_state.__class__.IDLE  # best-effort
        except Exception:
            pass


class CPUProcessManager(BaseProcessManager):
    # Менеджер процессов для CPU.

    def add_process_to_queue(self, process_pid: int) -> None:
        """
        Добавляет новый процесс в очередь. Проверки на допустимое количество процессов нет, т.к. это возлагается
        на вызывающий метод
        :param process_pid: PID процесса, который требуется добавить в очередь
        """
        self.proc_table_ptr[process_pid].current_state = ProcessState.READY
        super().add_process_to_queue(process_pid)

    def load_task(self, cpu: CPU, process_pid: int) -> None:
        """
        Загружает процесс на исполнение переданному ЦП, выставляет необходимые состояния ЦП и процесса
        :param process_pid: PID процесса для загрузки
        :param cpu: процессор, в который будет загружена задача
        """
        process = self.restore_process_state_word(process_pid)
        cpu.current_process = process
        process.current_state = ProcessState.RUNNING
        cpu.current_state = CPUState.RUNNING

    def unload_task(self, cpu: CPU) -> int:
        """
        Освобождает переданный ЦП от текущего процесса
        :param cpu: процессор для освобождения
        :return: старый выгруженный процесс
        """
        process = cpu.current_process
        self.save_process_state_word(process)
        cpu.current_process = None
        cpu.current_state = CPUState.IDLE
        return process.pid

    def _set_controller_idle(self, controller) -> None:
        try:
            controller.current_state = CPUState.IDLE
        except Exception:
            super()._set_controller_idle(controller)


class IOProcessManager(BaseProcessManager):
    # Менеджер очереди для IO контроллеров.

    def load_task(self, controller: IOController, process_pid: int) -> None:
        """
        Загружает процесс на исполнение переданному контроллеру IO, выставляет необходимые состояния контроллера IO и процесса
        :param controller: контроллер ввода-вывода, которому необходимо загрузить процесс
        :param process_pid: PID процесса для загрузки
        """
        process = self.restore_process_state_word(process_pid)
        controller.current_process = process
        controller.current_state = IOControllerState.RUNNING

    def unload_task(self, controller: IOController) -> int:
        """
        Освобождает переданный контроллер IO от текущего процесса
        :param controller: контроллер IO, который необходимо освободить от процесса
        :return: старый выгруженный процесс
        """
        process = controller.current_process
        self.save_process_state_word(process)
        controller.current_process = None
        controller.current_state = IOControllerState.IDLE
        return process.pid

    def _set_controller_idle(self, controller) -> None:
        try:
            controller.current_state = IOControllerState.IDLE
        except Exception:
            super()._set_controller_idle(controller)


class Scheduler:
    def __init__(self, proc_table: Dict[int, Process], quantum_size: int, memory_manager: MemoryManager) -> None:
        """
        Инициализация планировщика
        """
        self.proc_table_ptr = proc_table  # ссылка на таблицу процессов
        self.quantum_size = quantum_size  # размер кванта времени в тактах моделирования

        self.cpu_process_manager: CPUProcessManager = CPUProcessManager(self.proc_table_ptr)  # регулировщик ЦПр
        self.io_process_manager: IOProcessManager = IOProcessManager(self.proc_table_ptr)  # регулировщик контроллеров IO

        self.memory_manager: MemoryManager = memory_manager  # менеджер памяти
        return

    def dispatch_io(self, io_controller: IOController) -> None:
        """
        Проверить состояние контроллера IO, распределить процессы при необходимости
        :param io_controller: IO контроллер
        """
        if io_controller.current_state == IOControllerState.RUNNING:
            # если команда ввода-вывода завершена - возвращаем процесс в очередь ЦПр
            if io_controller.current_process.current_state == ProcessState.IO_END:
                io_controller.current_ticks_executed = 0
                io_controller.current_state = IOControllerState.IDLE
                unloaded_process_pid = self.io_process_manager.unload_task(io_controller)
                self.cpu_process_manager.add_process_to_queue(unloaded_process_pid)
        elif io_controller.current_state == IOControllerState.IDLE:
            # если контроллер простаивает - назначаем ему задачу
            self.io_process_manager.load_task_from_queue(io_controller)

    def dispatch_cpu(self, cpu: CPU) -> None:
        """
        Проверить состояние ЦПр, распределить процессы при необходимости
        :param cpu: ЦПр для проверки
        """
        if cpu.current_state is CPUState.RUNNING:
            # если квант времени истек - выгружаем процесс, загружаем новый
            if cpu.ticks_executed >= self.quantum_size:
                cpu.current_process.current_state = ProcessState.READY
                unloaded_process_pid = self.cpu_process_manager.unload_task(cpu)
                self.cpu_process_manager.add_process_to_queue(unloaded_process_pid)
                cpu.ticks_executed = 0
                self.cpu_process_manager.load_task_from_queue(cpu)

            elif cpu.is_process_finished():
                # если процесс завершен - выгружаем процесс, освобождаем память, загружаем новый процесс
                unloaded_process_pid = self.cpu_process_manager.unload_task(cpu)
                self.memory_manager.free_memory_from_process(unloaded_process_pid)
                self.proc_table_ptr.pop(unloaded_process_pid, None)
                self.cpu_process_manager.load_task_from_queue(cpu)

            elif cpu.current_process.current_state == ProcessState.IO_INIT:
                # если необходимо выполнить команду ввода-вывода - выгружаем из ЦПр и передаем в очередь контроллеров IO
                process_pid = self.cpu_process_manager.unload_task(cpu)
                self.proc_table_ptr[process_pid].current_state = ProcessState.IO_BLOCKED
                self.io_process_manager.add_process_to_queue(process_pid)
                self.cpu_process_manager.load_task_from_queue(cpu)

        elif cpu.current_state is CPUState.IDLE:
            # если ЦП простаивает - загружаем процесс
            self.cpu_process_manager.load_task_from_queue(cpu)
