from abstractions.Interrupt import InterruptType, Interrupt
from typing import List, Dict
#from devices.CPU import CPU
#from devices.IOController import IOController
#from managers.Scheduler import Scheduler
from managers.MemoryManager import MemoryManager
from managers.Dispatcher import Dispatcher
from abstractions.Process import Process, ProcessState


class InterruptHandler:
    def __init__(self, cpus_ptr, ios_ptr,
                 scheduler_ptr, dispatcher_ptr: Dispatcher, proc_table: Dict[int, Process],
                 memory_manager: MemoryManager):
        self.interrupts_raised: List[Interrupt] = []
        self.cpus = cpus_ptr
        self.ios = ios_ptr
        self.dispatcher = dispatcher_ptr
        self.scheduler = scheduler_ptr
        self.proc_table = proc_table
        self.memory_manager = memory_manager

        for cpu in self.cpus:
            cpu.interrupt_handler = self
        for io in self.ios:
            io.interrupt_handler = self

    def raise_interrupt(self, interrupt: Interrupt):
        self.interrupts_raised.append(interrupt)

    def handle_interrupts(self):
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
                    self.memory_manager.free_memory_from_process(process_pid)
                    self.proc_table.pop(process_pid)
                    if self.scheduler.cpu_queue:
                        self.dispatcher.load_task_to_CPU(self.cpus[device_id],
                                                         self.scheduler.get_process_from_cpu_queue())
                case InterruptType.PROCESS_IO_INIT:
                    self.dispatcher.change_process_state(process_pid, ProcessState.IO_BLOCKED)
                    self.dispatcher.unload_task(self.cpus[device_id])
                    self.scheduler.add_process_to_io_queue(process_pid)
                    if self.scheduler.cpu_queue:
                        self.dispatcher.load_task_to_CPU(self.cpus[device_id],
                                                         self.scheduler.get_process_from_cpu_queue())
                case InterruptType.PROCESS_IO_END:
                    self.dispatcher.change_process_state(process_pid, ProcessState.READY)
                    self.dispatcher.unload_task(self.ios[device_id])
                    self.scheduler.add_process_to_cpu_queue(process_pid)
                    if self.scheduler.io_queue:
                        self.dispatcher.load_task_to_IO(self.ios[device_id],
                                                        self.scheduler.get_process_from_io_queue())
        self.interrupts_raised.clear()
