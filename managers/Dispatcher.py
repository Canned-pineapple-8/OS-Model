from abstractions.Process import Process, ProcessState
from abstractions.Statistics import Statistics, ProcessTimeRecordType


# класс, моделирующий работу регулировщика
class Dispatcher:
    def __init__(self, memory_manager, cpus, ios, scheduler, stats: Statistics):
        self.memory_manager = memory_manager  # указатель на менеджера памяти
        self.cpus_ptr = cpus  # указатель на центральные процессоры
        self.ios_ptr = ios  # указатель на контроллеры ввода-вывода
        self.scheduler = scheduler  # указатель на планировщика
        self.stats = stats

    def change_process_state(self, process_pid:int, new_state:ProcessState) -> None:
        """
        Изменение состояния процесса
        :param process_pid: PID процесса
        :param new_state: новое состояние
        """
        process = self.memory_manager.get_process(process_pid)
        if process:
            if process.current_state != new_state:
                self.stats.add_time_os_multi(self.stats.time_costs.t_state)
                self.stats.add_sys_time_os_multi(self.stats.time_costs.t_global)

            process.current_state = new_state

    def save_process_state_word(self, process_state_word: Process) -> None:
        """
        Сохраняет слово состояния процесса
        :param process_state_word: слово состояния процесса
        """
        self.memory_manager.load_process(process_state_word.pid, process_state_word)

    def restore_process_state_word(self, process_pid: int) -> Process:
        """
        Восстанавливает слово состояния процесса
        :param process_pid: PID процесса
        :return: слово состояния процесса
        """
        return self.memory_manager.get_process(process_pid)

    def load_task_to_CPU(self, cpu, process_pid: int) -> None:
        """
        Загружает процесс на исполнение переданному ЦП, выставляет необходимые состояния ЦП и процесса
        :param process_pid: PID процесса для загрузки
        :param cpu: процессор, в который будет загружена задача
        """
        process = self.restore_process_state_word(process_pid)
        cpu.current_process = process
        self.change_process_state(process_pid, ProcessState.RUNNING)
        self.stats.add_time_process(process_pid, ProcessTimeRecordType.T_SYS_MONO, self.stats.time_costs.t_load)
        self.stats.add_time_os_multi(self.stats.time_costs.t_load)
        self.stats.add_sys_time_os_multi(self.stats.time_costs.t_global)



    def load_task_to_IO(self, io, process_pid: int) -> None:
        """
        Загружает процесс на исполнение переданному ЦП, выставляет необходимые состояния ЦП и процесса
        :param io: контроллер, в который будет загружена задача
        :param process_pid: PID процесса для загрузки
        """
        process = self.restore_process_state_word(process_pid)
        io.current_process = process
        self.change_process_state(process_pid, ProcessState.IO_RUNNING)

    def unload_task(self, device) -> int:
        """
        Освобождает переданный ЦП от текущего процесса
        :param device: устройство для освобождения
        :return: старый выгруженный процесс
        """
        process = device.current_process
        self.save_process_state_word(process)
        device.current_process = None
        return process.pid

    def dispatch_io(self, io_controller) -> None:
        """
        Проверить состояние контроллера IO, распределить процессы при необходимости
        :param io_controller: IO контроллер
        """
        from devices.IOController import IOControllerState
        if io_controller.current_state == IOControllerState.IDLE:
            # если контроллер простаивает - назначаем ему задачу
            if self.scheduler.io_queue:
                self.load_task_to_IO(io_controller, self.scheduler.get_process_from_io_queue())

    def dispatch_cpu(self, cpu) -> None:
        """
        Проверить состояние ЦПр, распределить процессы при необходимости
        :param cpu: ЦПр для проверки
        """
        from devices.CPU import CPUState
        if cpu.current_state is CPUState.IDLE:
            # если ЦП простаивает - загружаем процесс
            if self.scheduler.cpu_queue:
                self.load_task_to_CPU(cpu, self.scheduler.get_process_from_cpu_queue())

