from dataclasses import dataclass, field

# параметры случайных величин
@dataclass
class RandomConfig:
    random_seed: float = 1.0

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
    random: RandomConfig = field(default_factory=RandomConfig)


# временные затраты ОС на выполнение служебных операций (в тактах)
@dataclass
class TimeCosts:
    t_next: float = 1  # затраты на выбор процесса для исполнения
    t_state: float = 1  # затраты на переключение состояния процесса
    t_init_io: float = 1  # затраты на инициализацию ввода-вывода
    t_end_io: float = 1  # затраты по обслуживанию сигнала окончания
    # ввода-вывода
    t_load: float = 1  # затраты на загрузку нового задания
    t_global: float = 1  # затраты на общение с общими данными


# сбор статистики для отображения и вычислений
@dataclass
class OSStats:
    tasks_loaded: int = 0  # число загруженных заданий
    d_system: float = 0  # системные затраты ОС (в процентах)
    t_multi: float = 0  # время работы системы (в тактах) (мультипрограммная система)
    m_multi: float = 0  # число выполненных заданий с момента начала моделирования
    t_proc_avg: float = 0  # оборотное время
    t_mono: float = 0  # время выполнения m_multi Заданий в однопрограммной системе
    m_mono: float = 0  # число заданий, которые могли бы выполниться за время running_time
    # в однопрограммной ОС
    d_multi: float = 0  # производительность модели по сравнению с однопрограммной (в процентах)




