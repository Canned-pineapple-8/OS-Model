from dataclasses import dataclass, field


# параметры памяти
@dataclass
class MemoryConfig:
    total_memory: int = 1024
    proc_table_size: int = 64


# параметры ЦПр
@dataclass
class CPUConfig:
    cpus_num: int = 3
    quantum_size: int = 5


# параметры IO
@dataclass
class IOConfig:
    ios_num: int = 3


# параметры скорости
@dataclass
class SpeedConfig:
    speed: float = 1.0
    speed_multiplier: float = 0.1
    min_speed: float = 0.1
    max_speed: float = 10.0


# генерация процессов
@dataclass
class ProcessGenerationConfig:
    min_memory: int = 3
    max_memory: int = 10
    total_commands_min: int = 1
    total_commands_max: int = 10
    io_percentage_min: float = 0.0
    io_percentage_max: float = 0.5
    io_command_duration_min: int = 1
    io_command_duration_max: int = 5


# генерация команд
@dataclass
class CommandGenerationConfig:
    operand_min: int = 1
    operand_max: int = 10
    operands_block_shift: int = 0
    result_block_shift: int = 2


# основная структура-конфигурация
@dataclass
class OSConfig:
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    cpu: CPUConfig = field(default_factory=CPUConfig)
    io: IOConfig = field(default_factory=IOConfig)
    speed: SpeedConfig = field(default_factory=SpeedConfig)
    process_generation: ProcessGenerationConfig = field(default_factory=ProcessGenerationConfig)
    command_generation: CommandGenerationConfig = field(default_factory=CommandGenerationConfig)


# временные затраты ОС на выполнение служебных операций (в тактах)
@dataclass
class TimeCosts:
    choose_process_time: int = 0  # затраты на выбор процесса для исполнения
    change_process_state_to_io_time: int = 0  # затраты на изменение состояния
    # процесса по обращению к вводу-выводу
    change_process_state_to_io_end_time: int = 0  # затраты по обслуживанию сигнала окончания
    # ввода-вывода
    load_process_time: int = 0  # затраты на загрузку нового задания
    data_request_time: int = 0  # затраты на общение с общими данными

# сбор статистики для отображения и вычислений
@dataclass
class OSStats:
    tasks_loaded: int = 0  # число загруженных заданий
    system_costs: float = 0  # системные затраты ОС (в процентах)
    running_time: int = 0  # время работы системы (в тактах)
    tasks_finished_multi: int = 0  # число выполненных заданий с момента начала моделирования
    average_task_processing_time: float = 0  # оборотное время
    tasks_finished_single: int = 0  # число заданий, которые могли бы выполниться за время running_time
    # в однопрограммной ОС
    system_performance: float = 0  # производительность модели по сравнению с однопрограммной (в процентах)




