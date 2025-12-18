import json
import time
import random

from model.Config import OSConfig, MemoryConfig, CPUConfig, IOConfig, SpeedConfig, \
    ProcessGenerationConfig, CommandGenerationConfig, RandomConfig, TimeCosts
from abstractions.Speed import Speed
from managers.Scheduler import Scheduler
from devices.CPU import CPU, CPUState
from devices.IOController import IOController, IOControllerState
from managers.MemoryManager import MemoryManager
from abstractions.Process import Process, ProcessCommandsConfig, ProcessMemoryConfig, ProcessState
from utils.RandomFactory import RandomFactory
from devices.Memory import Memory
from managers.InterruptHandler import InterruptHandler
from managers.Dispatcher import Dispatcher
from abstractions.Statistics import Statistics, ProcessTimeStats, ProcessTimeRecordType


class OSModel:
    def __init__(self, config_path: str) -> None:
        """
        Инициализация модели ОС из JSON-файла.
        :param config_path: путь к JSON-файлу с параметрами
        """
        self.running = False

        self.proc_table = dict()  # таблица процессов: dict [int, Process] (Доступ по PID)

        self.config = self.load_config(config_path)
        # статистика
        self.stats = Statistics(self.config.time_costs, self.proc_table)

        # устанавливаем сид для воспроизводимости значений
        if self.config.random.random_seed != -1:
            random.seed(self.config.random.random_seed)

        self.physical_memory = Memory(self.config.memory.total_memory, self.stats)  # структура эмулирующая
        # физическую память процессов
        self.proc_table_size = self.config.memory.proc_table_size  # максимальное число процессов
        self.memory_manager = MemoryManager(self.physical_memory, self.proc_table)  # класс для управления памятью
        # процессов

        # центральные процессоры
        self.cpus = [CPU(self.physical_memory, i, self.config.cpu.quantum_size) for i in range(self.config.cpu.cpus_num)]
        # контроллеры ввода-вывода
        self.io_controllers = [IOController(i) for i in range(self.config.io.ios_num)]

        self.speed_manager = Speed(self.config)  # инициализация параметров, связанных со скоростью
        self.scheduler = Scheduler(self.stats)  # инициализация планировщика и его структур

        # регулировщик
        self.dispatcher = Dispatcher(self.memory_manager, self.cpus, self.io_controllers, self.scheduler, self.stats)
        # обработчик прерываний
        self.interrupt_handler = InterruptHandler(self.cpus, self.io_controllers, self.scheduler,
                                                  self.dispatcher, self.memory_manager, self.stats)

        self.running = True
        return

    def load_config(self, path: str) -> OSConfig:
        """
        Загружает конфиг модели ОС.
        При отсутствии файла или повреждённом JSON — возвращает OSConfig() с дефолтами.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Конфиг не найден или поврежден. Будут загружены значения по умолчанию.")
            return OSConfig()

        def load_section(cls, section_name: str):
            section = data.get(section_name, {})
            if isinstance(section, dict):
                return cls(**{k: section.get(k, getattr(cls(), k)) for k in cls().__dict__.keys()})
            else:
                return cls()

        return OSConfig(
            memory=load_section(MemoryConfig, "memory"),
            cpu=load_section(CPUConfig, "cpu"),
            io=load_section(IOConfig, "io"),
            speed=load_section(SpeedConfig, "speed"),
            process_generation=load_section(ProcessGenerationConfig, "process_generation"),
            command_generation=load_section(CommandGenerationConfig, "command_generation"),
            random=load_section(RandomConfig, "random"),
            time_costs=load_section(TimeCosts, "time_costs")
        )

    @property
    def speed(self) -> float:
        """Геттер для скорости"""
        return self.speed_manager.speed

    def change_speed(self, increase:bool = True):
        """
        Увеличение/уменьшение скорости моделирования (геттер метода speed_manager)
        :param increase: для увеличения - True, Для уменьшения - False
        :return: новое значение скорости (float)
        """
        new_speed = self.speed_manager.change_speed(increase)
        return new_speed

    def calculate_memory_usage(self) -> int:
        """
        Вычисление текущей используемой памяти (выполняется через MemoryManager)
        :return: размер текущей используемой памяти, целое число
        """
        return self.memory_manager.memory_ptr.physical_memory_size - self.memory_manager.available_memory

    def calculate_available_memory(self) -> int:
        """
        Вычисление текущей свободной памяти
        :return: размер текущей свободной памяти, целое число
        """
        return self.memory_manager.available_memory

    def load_new_task(self, process: Process) -> int:
        """
        Загрузка новой задачи, если есть место в таблице процессов и достаточно памяти
        :param process: задача (процесс) на загрузку
        :return: PID загруженного процесса
        """
        if self.memory_manager.get_current_proc_table_size() >= self.proc_table_size:
            raise RuntimeError("Достигнуто максимальное количество загруженных задач.")

        if self.calculate_available_memory() < process.process_memory_config.block_size:
            raise RuntimeError("Недостаточно памяти для загрузки нового процесса.")

        self.memory_manager.load_process(process.pid, process)
        self.scheduler.add_process_to_cpu_queue(process_pid=process.pid)
        process.current_state = ProcessState.READY
        self.stats.add_process_start_time(process.pid)
        return process.pid

    def perform_program_delay(self) -> None:
        """
        Выполнение программной задержки
        """
        if self.speed > 0:
            delay = 1.0 / self.speed
            time.sleep(delay)
        else:
            time.sleep(0.01)
        return

    def terminate(self) -> None:
        """
        Завершение моделирования (очистка структур и установление флага)
        """
        # очистка таблицы процессов
        self.proc_table.clear()

        # очистка планировщика
        self.scheduler.cpu_queue.clear()
        self.scheduler.io_queue.clear()

        # очистка CPU
        for cpu in self.cpus:
            cpu.current_process = None
            cpu.current_state = CPUState.IDLE
            cpu.total_commands_executed = 0
            cpu.current_ticks_executed = 0

        # очистка IO-контроллеров
        for io in self.io_controllers:
            io.current_ticks_executed = 0
            io.total_ticks_executed = 0
            io.current_process = None
            io.current_state = IOControllerState.IDLE

        # очистка памяти (логическая)
        self.physical_memory.physical_memory = [None] * self.physical_memory.physical_memory_size

        # очистка менеджера памяти
        self.memory_manager.memory_map.clear()
        self.memory_manager.available_memory = self.physical_memory.physical_memory_size
        self.running = False
        return

    def fill_processes_if_possible(self) -> None:
        """
        Заполняет память новыми процессами до достижения лимита.
        """
        new_process_memory = RandomFactory.generate_random_int_value(self.config.process_generation.min_memory,
                                                                     self.config.process_generation.max_memory)
        while self.calculate_available_memory() >= new_process_memory \
                and self.memory_manager.get_current_proc_table_size() < self.proc_table_size:
            # генерация параметров
            commands_config = ProcessCommandsConfig()
            commands_config.total_commands_cnt = \
                RandomFactory.generate_random_int_value(self.config.process_generation.total_commands_min,
                                                        self.config.process_generation.total_commands_max)
            commands_config.io_command_ratio = \
                RandomFactory.generate_random_float_value(self.config.process_generation.io_percentage_min,
                                                          self.config.process_generation.io_percentage_max, 1)
            commands_config.min_operand = self.config.command_generation.operand_min
            commands_config.max_operand = self.config.command_generation.operand_max
            commands_config.io_command_duration_min = self.config.process_generation.io_command_duration_min
            commands_config.io_command_duration_max = self.config.process_generation.io_command_duration_max

            memory_config = ProcessMemoryConfig(block_size=new_process_memory)

            new_process = Process(ph_memory_ptr=self.physical_memory,
                                  process_commands_config=commands_config,
                                  process_memory_info=memory_config)

            self.load_new_task(new_process)

            # выделение памяти под процесс
            block_start = self.memory_manager.allocate_memory_for_process(new_process.pid,
                                                                          new_process.process_memory_config.block_size)

            if block_start == -1:
                return

            new_process.process_memory_config.block_start = block_start

            new_process.process_memory_config.result_block_address = block_start + self.config.command_generation.result_block_shift
            new_process.process_memory_config.operands_block_address = block_start + self.config.command_generation.operands_block_shift
            new_process_memory = RandomFactory.generate_random_int_value(self.config.process_generation.min_memory,
                                                                         self.config.process_generation.max_memory)
        return

    def perform_tick(self) -> None:
        """
        Выполняет один такт моделирования. В его ходе:
        - если возможно, генерируются новые процессы в таблице процессов
        - каждый ЦП выполняет такт моделирования
        - каждый IO выполняет такт моделирования
        - обработчик прерываний обрабатывает накопленные прерывания
        - регулировщик проверяет состояния ЦП (на всякий случай)
        - регулировщик проверяет состояния IO (на всякий случай)
        - менеджер памяти освобождает ресурсы завершенных в ходе такта процессов
        """
        self.fill_processes_if_possible()
        self.stats.add_runtime_to_processes(self.proc_table)
        self.stats.add_time_os_multi(1)

        for cpu in self.cpus:
            cpu.execute_tick()

        for io in self.io_controllers:
            io.execute_tick()

        self.interrupt_handler.handle_interrupts()

        for cpu in self.cpus:
            self.dispatcher.dispatch_cpu(cpu)

        for io in self.io_controllers:
            self.dispatcher.dispatch_io(io)

        self.memory_manager.free_resources()

        self.stats.recalc_system_params()
        self.stats.recalc_avg_process_params()

        return
