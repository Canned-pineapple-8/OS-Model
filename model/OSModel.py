import json
import time

from model.Config import OSConfig, MemoryConfig, CPUConfig, IOConfig, SpeedConfig, \
    ProcessGenerationConfig, CommandGenerationConfig
from abstractions.Speed import Speed
from managers.Scheduler import Scheduler
from devices.CPU import CPU, CPUState
from devices.IOController import IOController, IOControllerState
from managers.MemoryManager import MemoryManager
from abstractions.Process import Process, ProcessCommandsConfig, ProcessMemoryConfig
from utils.RandomFactory import RandomFactory
from devices.Memory import Memory


class OSModel:
    def __init__(self, config_path: str) -> None:
        """
        Инициализация модели ОС из JSON-файла.
        :param config_path: путь к JSON-файлу с параметрами
        """
        self.running = False

        self.config = self.load_config(config_path)

        self.physical_memory = Memory(self.config.memory.total_memory)
        self.proc_table = dict()  # таблица процессов: dict [int, Process] (Доступ по PID)
        self.proc_table_size = self.config.memory.proc_table_size  # максимальное число процессов
        self.memory_manager = MemoryManager(self.physical_memory, self.proc_table)

        self.cpus = [CPU(self.physical_memory, i) for i in range(self.config.cpu.cpus_num)]
        self.io_controllers = [IOController(i) for i in range(self.config.io.ios_num)]

        self.speed_manager = Speed(self.config)  # инициализация параметров, связанных со скоростью
        self.scheduler = Scheduler(self.proc_table, self.config.cpu.quantum_size, self.memory_manager)  # инициализация планировщика и его структур

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
            command_generation=load_section(CommandGenerationConfig, "command_generation")
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
        if len(self.proc_table.items()) >= self.proc_table_size:
            raise RuntimeError("Достигнуто максимальное количество загруженных задач.")

        if self.calculate_available_memory() < process.process_memory_config.block_size:
            raise RuntimeError("Недостаточно памяти для загрузки нового процесса.")

        self.proc_table[process.pid] = process
        self.scheduler.cpu_process_manager.add_process_to_queue(process_pid=process.pid)

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
        :return: void
        """
        # очистка таблицы процессов
        self.proc_table.clear()

        # очистка планировщика
        self.scheduler.io_process_manager.processes.clear()
        self.scheduler.cpu_process_manager.processes.clear()

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

    def remove_process_from_process_table(self, process_pid: int) -> None:
        """
        Удаляет процесс из таблицы процессов
        :param process_pid: PID процесса для удаления
        """
        self.proc_table.pop(process_pid, None)
        return

    def fill_processes_if_possible(self) -> None:
        """
        Заполняет память новыми процессами до достижения лимита.
        """
        new_process_memory = self.config.process_generation.min_memory
        while self.calculate_available_memory() >= new_process_memory and len(self.proc_table) < self.proc_table_size:
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

            new_process.process_memory_config.block_start = block_start

            new_process.process_memory_config.result_block_address = block_start + self.config.command_generation.result_block_shift
            new_process.process_memory_config.operands_block_address = block_start + self.config.command_generation.operands_block_shift
        return

    def perform_tick(self) -> None:
        """
        Выполняет один такт моделирования. В его ходе:
        - планировщик распределяет задачи между ЦП (если есть необходимость)
        - каждый ЦП выполняет один такт назначенного ему процесса
        - планировщик распределяет задачи между контроллерами ввода-вывода (если есть необходимость)
        - каждый контроллер ввода-вывода выполняет один такт назначенного ему процесса
        """
        for cpu in self.cpus:
            self.scheduler.dispatch_cpu(cpu)
            cpu.execute_tick()

        for io in self.io_controllers:
            self.scheduler.dispatch_io(io)
            io.execute_tick()
        return
