from abstractions.Interrupt import InterruptType, Interrupt
from typing import List
from managers.MemoryManager import MemoryManager
from managers.Dispatcher import Dispatcher
from abstractions.Process import ProcessState
from abstractions.Statistics import Statistics, ProcessTimeRecordType


# класс, моделирующий работу обработчика прерываний
class InterruptHandler:
    def __init__(self, cpus_ptr, ios_ptr,
                 scheduler_ptr, dispatcher_ptr: Dispatcher,
                 memory_manager: MemoryManager, stats: Statistics):
        self.interrupts_raised: List[Interrupt] = []  # список прерываний, вызванных за такт
        self.cpus = cpus_ptr  # указатель на центральные процессоры
        self.ios = ios_ptr  # указатель на контроллеры ввода-вывода
        self.dispatcher = dispatcher_ptr  # указатель на регулировщика
        self.scheduler = scheduler_ptr  # указатель на планировщика
        self.memory_manager = memory_manager  # указатель на менеджера памяти
        self.stats = stats

        for cpu in self.cpus:
            cpu.interrupt_handler = self  # выставляем на каждый ЦП указатель на себя
        for io in self.ios:
            io.interrupt_handler = self  # выставляем на каждый IO указатель на себя

    def raise_interrupt(self, interrupt: Interrupt):
        """
        Вызвать прерывание (добавить в соответствующую структуру для их накопления)
        :param interrupt: прерывание
        """
        self.interrupts_raised.append(interrupt)

    def handle_interrupts(self):
        """
        Обработать все накопленные прерывания
        """
        for interrupt in self.interrupts_raised:
            process_pid = interrupt.pid_process
            device_id = interrupt.device_called_id
            match interrupt.type:
                case InterruptType.QUANTUM_ENDED:
                    self.dispatcher.change_process_state(process_pid, ProcessState.READY)
                    self.dispatcher.unload_task(self.cpus[device_id])
                    self.scheduler.add_process_to_cpu_queue(process_pid)
                    if self.scheduler.cpu_queue:
                        self.dispatcher.load_task_to_CPU(self.cpus[device_id],
                                                         self.scheduler.get_process_from_cpu_queue())
                case InterruptType.PROCESS_TERMINATED:
                    self.dispatcher.change_process_state(process_pid, ProcessState.TERMINATED)
                    self.dispatcher.unload_task(self.cpus[device_id])
                    self.memory_manager.schedule_process_to_be_removed(process_pid)
                    self.stats.os_stats.m_multi += 1
                    self.stats.add_process_end_time(process_pid)

                    if self.scheduler.cpu_queue:
                        self.dispatcher.load_task_to_CPU(self.cpus[device_id],
                                                         self.scheduler.get_process_from_cpu_queue())
                case InterruptType.PROCESS_IO_INIT:
                    self.dispatcher.stats.add_time_process(process_pid, ProcessTimeRecordType.T_SYS_MONO,
                                                           self.dispatcher.stats.time_costs.t_init_io)
                    self.stats.add_time_os_multi(self.dispatcher.stats.time_costs.t_init_io)
                    self.stats.add_sys_time_os_multi(self.stats.time_costs.t_init_io)

                    self.dispatcher.change_process_state(process_pid, ProcessState.IO_BLOCKED)
                    self.dispatcher.unload_task(self.cpus[device_id])
                    self.scheduler.add_process_to_io_queue(process_pid)
                    if self.scheduler.cpu_queue:
                        self.dispatcher.load_task_to_CPU(self.cpus[device_id],
                                                         self.scheduler.get_process_from_cpu_queue())
                case InterruptType.PROCESS_IO_END:
                    self.dispatcher.stats.add_time_process(process_pid, ProcessTimeRecordType.T_SYS_MONO,
                                                           self.dispatcher.stats.time_costs.t_end_io)
                    self.stats.add_time_os_multi(self.dispatcher.stats.time_costs.t_end_io)
                    self.stats.add_sys_time_os_multi(self.stats.time_costs.t_end_io)

                    self.dispatcher.change_process_state(process_pid, ProcessState.READY)
                    self.dispatcher.unload_task(self.ios[device_id])
                    self.scheduler.add_process_to_cpu_queue(process_pid)
                    if self.scheduler.io_queue:
                        self.dispatcher.load_task_to_IO(self.ios[device_id],
                                                        self.scheduler.get_process_from_io_queue())
                case InterruptType.PROCESS_STOPPED_CPU:
                    self.dispatcher.change_process_state(process_pid, ProcessState.STOPPED_CPU)
                    self.dispatcher.unload_task(self.cpus[device_id])
                    if self.scheduler.cpu_queue:
                        self.dispatcher.load_task_to_CPU(self.cpus[device_id],
                                                         self.scheduler.get_process_from_cpu_queue())
                case InterruptType.PROCESS_STOPPED_IO:
                    self.dispatcher.stats.add_time_process(process_pid, ProcessTimeRecordType.T_SYS_MONO,
                                                           self.dispatcher.stats.time_costs.t_end_io)
                    self.stats.add_time_os_multi(self.dispatcher.stats.time_costs.t_end_io)
                    self.stats.add_sys_time_os_multi(self.stats.time_costs.t_end_io)

                    self.dispatcher.change_process_state(process_pid, ProcessState.STOPPED_IO)
                    self.dispatcher.unload_task(self.ios[device_id])
                    if self.scheduler.io_queue:
                        self.dispatcher.load_task_to_IO(self.ios[device_id],
                                                        self.scheduler.get_process_from_io_queue())
                case InterruptType.PROCESS_RESUMED_IO:
                    self.dispatcher.stats.add_time_process(process_pid, ProcessTimeRecordType.T_SYS_MONO,
                                                           self.dispatcher.stats.time_costs.t_init_io)
                    self.stats.add_time_os_multi(self.dispatcher.stats.time_costs.t_init_io)
                    self.stats.add_sys_time_os_multi(self.stats.time_costs.t_init_io)

                    self.dispatcher.change_process_state(process_pid, ProcessState.IO_BLOCKED)
                    self.scheduler.add_process_to_io_queue(process_pid)
                case InterruptType.PROCESS_RESUMED_CPU:
                    self.dispatcher.stats.add_time_process(process_pid, ProcessTimeRecordType.T_SYS_MONO,
                                                           self.dispatcher.stats.time_costs.t_end_io)
                    self.stats.add_time_os_multi(self.dispatcher.stats.time_costs.t_end_io)
                    self.stats.add_sys_time_os_multi(self.stats.time_costs.t_end_io)

                    self.dispatcher.change_process_state(process_pid, ProcessState.READY)
                    self.scheduler.add_process_to_cpu_queue(process_pid)
                case InterruptType.PROCESS_KILLED:
                    found = 0
                    for cpu in self.cpus:
                        if cpu.current_process and cpu.current_process.pid == process_pid:
                            found = 1
                            self.dispatcher.change_process_state(process_pid, ProcessState.TERMINATED)
                            self.dispatcher.unload_task(self.cpus[cpu.device_id])
                            self.memory_manager.schedule_process_to_be_removed(process_pid)
                            self.stats.os_stats.m_multi += 1
                            self.stats.add_process_end_time(process_pid)

                            if self.scheduler.cpu_queue:
                                self.dispatcher.load_task_to_CPU(cpu,
                                                                 self.scheduler.get_process_from_cpu_queue())
                    if not found:
                        for io in self.ios:
                            if io.current_process and io.current_process.pid == process_pid:
                                found = 1
                                self.dispatcher.stats.add_time_process(process_pid, ProcessTimeRecordType.T_SYS_MONO,
                                                                       self.dispatcher.stats.time_costs.t_end_io)
                                self.stats.add_time_os_multi(self.dispatcher.stats.time_costs.t_end_io)
                                self.stats.add_sys_time_os_multi(self.stats.time_costs.t_end_io)

                                self.dispatcher.unload_task(self.ios[io.device_id])
                                self.dispatcher.change_process_state(process_pid, ProcessState.TERMINATED)
                                self.memory_manager.schedule_process_to_be_removed(process_pid)
                                self.stats.os_stats.m_multi += 1
                                self.stats.add_process_end_time(process_pid)
                                if self.scheduler.io_queue:
                                    self.dispatcher.load_task_to_IO(io,
                                                                    self.scheduler.get_process_from_io_queue())
                    if not found:
                        self.dispatcher.change_process_state(process_pid, ProcessState.TERMINATED)
                        self.memory_manager.schedule_process_to_be_removed(process_pid)
                        self.stats.os_stats.m_multi += 1
                        self.stats.add_process_end_time(process_pid)

                case _:
                    raise RuntimeError("Неизвестный тип прерывания.")
        self.interrupts_raised.clear()
