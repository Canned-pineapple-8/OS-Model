from dataclasses import dataclass


# ---------------- MEMORY ----------------

@dataclass
class MemoryConfig:
    total_memory: int = 1024
    proc_table_size: int = 64


# ---------------- CPU ----------------

@dataclass
class CPUConfig:
    cpus_num: int = 1
    quantum_size: int = 5


# ---------------- IO ----------------

@dataclass
class IOConfig:
    ios_num: int = 1


# ---------------- SPEED ----------------

@dataclass
class SpeedConfig:
    speed: float = 1.0
    speed_multiplier: float = 0.1
    min_speed: float = 0.1
    max_speed: float = 10.0


# ---------------- PROCESS GENERATION ----------------

@dataclass
class ProcessGenerationConfig:
    min_memory: int = 10
    total_commands_min: int = 1
    total_commands_max: int = 10
    io_percentage_min: float = 0.0
    io_percentage_max: float = 0.5


# ---------------- COMMAND GENERATION ----------------

@dataclass
class CommandGenerationConfig:
    operand_min: int = 1
    operand_max: int = 10


# ---------------- ROOT CONFIG ----------------

@dataclass
class OSConfig:
    memory: MemoryConfig = MemoryConfig()
    cpu: CPUConfig = CPUConfig()
    io: IOConfig = IOConfig()
    speed: SpeedConfig = SpeedConfig()
    process_generation: ProcessGenerationConfig = ProcessGenerationConfig()
    command_generation: CommandGenerationConfig = CommandGenerationConfig()
