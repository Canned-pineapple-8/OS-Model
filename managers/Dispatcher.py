from typing import Dict, List
from abstractions.Process import Process, ProcessState
from devices.CPU import CPU
from devices.IOController import IOController


class Dispatcher:
    def __init__(self, proc_table_ptr: Dict[int, Process], cpus: List[CPU], ios: List[IOController]):
        self.proc_table_ptr = proc_table_ptr
        self.cpus_ptr = cpus
        self.ios_ptr = ios

    def change_process_state(self, process:Process, new_state:ProcessState):
        process.current_state = new_state

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

    def load_task_to_CPU(self, cpu: CPU, process_pid: int) -> None:
        """
        Загружает процесс на исполнение переданному ЦП, выставляет необходимые состояния ЦП и процесса
        :param process_pid: PID процесса для загрузки
        :param cpu: процессор, в который будет загружена задача
        """
        process = self.restore_process_state_word(process_pid)
        cpu.current_process = process
        self.change_process_state(process, ProcessState.RUNNING)

    def load_task_to_IO(self, io: IOController, process_pid: int) -> None:
        """
        Загружает процесс на исполнение переданному ЦП, выставляет необходимые состояния ЦП и процесса
        :param io: контроллер, в который будет загружена задача
        :param process_pid: PID процесса для загрузки
        """
        process = self.restore_process_state_word(process_pid)
        io.current_process = process
        self.change_process_state(process, ProcessState.IO_BLOCKED)

    def unload_task(self, cpu: CPU) -> int:
        """
        Освобождает переданный ЦП от текущего процесса
        :param cpu: процессор для освобождения
        :return: старый выгруженный процесс
        """
        process = cpu.current_process
        self.save_process_state_word(process)
        cpu.current_process = None
        return process.pid

