from model.OSModel import OSModel
from abc import ABC, abstractmethod
from typing import Optional

class Instruction(ABC):
    @abstractmethod
    def execute(self, os_model:OSModel, osui) -> str:
        pass


class InstructionExecutor:
    def __init__(self, os_model:OSModel, osui):
        self.os_model = os_model
        self.osui = osui
        self.parser = CommandParser()

    def parse(self, instruction:str):
        command = self.parser.parse(instruction)
        return command

    def execute(self, command: Instruction) -> str:
        result = command.execute(self.os_model, self.osui)
        return result


class CommandParser:
    def parse(self, line: str) -> Optional[Instruction]:
        err_message = "неизвестная команда"
        parts = line.strip().split()
        if not parts:
            return None

        cmd = parts[0].lower()

        if cmd == "help":
            return Help()

        if cmd == "terminate":
            return Terminate()

        if "speed" in cmd:
            if cmd == "speed+":
                return ChangeSpeed(True)
            if cmd == "speed-":
                return ChangeSpeed(False)
            try:
                val = float(parts[1])
            except Exception:
                raise ValueError(err_message)
            return ChangeSpeed(True, val)

        if cmd == "stop":
            if len(parts) < 2:
                raise ValueError(err_message)
            if parts[1].lower() == "loading":
                return StopLoading()
            if parts[1].lower() == "task":
                try:
                    val = int(parts[2])
                except Exception:
                    raise ValueError(err_message)
                return StopTask(val)
            raise ValueError(err_message)

        if cmd == "continue":
            if len(parts) < 2:
                raise ValueError(err_message)
            if parts[1].lower() == "loading":
                return ContinueLoading()
            if parts[1].lower() == "task":
                try:
                    val = int(parts[2])
                except Exception:
                    raise ValueError(err_message)
                return ResumeTask(val)
            raise ValueError(err_message)

        if cmd == "load":
            if len(parts) < 2:
                raise ValueError(err_message)
            if parts[1].lower() == "task":
                return GenerateNewTask()
            raise ValueError(err_message)

        if cmd == "kill":
            if len(parts) < 2:
                raise ValueError(err_message)
            try:
                val = int(parts[1])
            except Exception:
                raise ValueError(err_message)
            return TerminateProcess(val)

        if cmd == "finish":
            return FinishKill()

        if cmd == "seed":
            if len(parts) < 2:
                raise ValueError(err_message)
            try:
                val = int(parts[1])
            except Exception:
                raise ValueError(err_message)
            return SetRandomSeed(val)

        raise ValueError(err_message)


class Terminate(Instruction):
    def execute(self, os_model, osui):
        os_model.terminate()
        osui.close()
        return ""


class TerminateProcess(Instruction):
    def __init__(self, pid: int):
        self.pid = pid

    def execute(self, os_model:OSModel, osui) -> str:
        from abstractions.Interrupt import InterruptType, Interrupt
        if self.pid not in os_model.proc_table:
            return f"Процесса с PID {self.pid} не существует"
        interrupt = Interrupt(InterruptType.PROCESS_KILLED, self.pid, -1)
        os_model.interrupt_handler.raise_interrupt(interrupt)
        return f"Процесса с PID {self.pid} уничтожен"


class ChangeSpeed(Instruction):
    def __init__(self, increase: bool, value: float = None):
        self.increase = increase
        self.value = value

    def execute(self, os_model:OSModel, osui) -> str:
        if self.value is not None:
            speed = os_model.change_speed_to_value(self.value)
            return f"Скорость равна {os_model.speed:.3f}"
        else:
            speed = os_model.change_speed(self.increase)
            return f"Скорость равна {os_model.speed:.3f}"


class StopLoading(Instruction):
    def execute(self, os_model:OSModel, osui) -> str:
        os_model.loading_processes_enabled = False
        return "Загрузка новых процессов приостановлена"


class FinishKill(Instruction):
    def execute(self, os_model:OSModel, osui) -> str:
        os_model.loading_processes_enabled = False
        os_model.kill_on_finishing = True
        return "Загрузка новых процессов приостановлена. После завершения выполнения текущих процессов модель закончит работу."

class ContinueLoading(Instruction):
    def execute(self, os_model:OSModel, osui) -> str:
        os_model.loading_processes_enabled = True
        return "Загрузка новых процессов включена"


class GenerateNewTask(Instruction):
    def execute(self, os_model:OSModel, osui) -> str:
        process = os_model.generate_process()
        if process is None:
            return "Генерация нового задания невозможна"
        try:
            os_model.load_new_task(process)
        except Exception:
            return "Генерация нового задания невозможна"
        return f"Загружено новое задание с PID {process.pid}"


class StopTask(Instruction):
    def __init__(self, pid: int):
        self.pid = pid

    def execute(self, os_model:OSModel, osui) -> str:
        from abstractions.Process import Process, ProcessState
        from abstractions.Interrupt import InterruptType, Interrupt
        if self.pid not in os_model.proc_table:
            return f"Процесса с PID {self.pid} не существует"
        if os_model.proc_table[self.pid].current_state == ProcessState.RUNNING:
            for cpu in os_model.cpus:
                if cpu.current_process and cpu.current_process.pid == self.pid:
                    interrupt = Interrupt(InterruptType.PROCESS_STOPPED_CPU, self.pid, cpu.device_id)
                    os_model.interrupt_handler.raise_interrupt(interrupt)
            return f"Процесс с PID {self.pid} остановлен"
        if os_model.proc_table[self.pid].current_state == ProcessState.IO_RUNNING:
            for io in os_model.io_controllers:
                if io.current_process and io.current_process.pid == self.pid:
                    interrupt = Interrupt(InterruptType.PROCESS_STOPPED_IO, self.pid, io.device_id)
                    os_model.interrupt_handler.raise_interrupt(interrupt)
            return f"Процесс с PID {self.pid} остановлен"
        return f"Процесс с PID {self.pid} не выполняется"


class ResumeTask(Instruction):
    def __init__(self, pid: int):
        self.pid = pid

    def execute(self, os_model:OSModel, osui) -> str:
        from abstractions.Process import Process, ProcessState
        from abstractions.Interrupt import InterruptType, Interrupt
        if self.pid not in os_model.proc_table:
            return f"Процесса с PID {self.pid} не существует"
        if os_model.proc_table[self.pid].current_state == ProcessState.STOPPED_CPU:
            interrupt = Interrupt(InterruptType.PROCESS_RESUMED_CPU, self.pid, -1)
            os_model.interrupt_handler.raise_interrupt(interrupt)
            return f"Процесс с PID {self.pid} возобновлен"
        if os_model.proc_table[self.pid].current_state == ProcessState.STOPPED_IO:
            interrupt = Interrupt(InterruptType.PROCESS_RESUMED_IO, self.pid, -1)
            os_model.interrupt_handler.raise_interrupt(interrupt)
            return f"Процесс с PID {self.pid} возобновлен"
        return f"Процесс с PID {self.pid} не был остановлен"

class SetRandomSeed(Instruction):
    def __init__(self, seed: int):
        self.seed = seed

    def execute(self, os_model: OSModel, osui) -> str:
        import random
        random.seed(self.seed)
        os_model.config.random.random_seed = self.seed
        return f"Генератор случайных чисел инициализирован значением {self.seed}"

class Help(Instruction):
    def execute(self, os_model: OSModel, osui) -> str:
        return (
            "Доступные команды:\n\n"
            "terminate\n"
            "    Немедленно завершить работу модели и закрыть интерфейс.\n\n"
            "speed+\n"
            "    Увеличить скорость моделирования на шаг.\n\n"
            "speed-\n"
            "    Уменьшить скорость моделирования на шаг.\n\n"
            "speed <value>\n"
            "    Установить скорость моделирования в указанное значение (float).\n\n"
            "stop loading\n"
            "    Приостановить автоматическую загрузку новых заданий.\n\n"
            "continue loading\n"
            "    Возобновить автоматическую загрузку новых заданий.\n\n"
            "load task\n"
            "    Загрузить одно новое задание вручную.\n\n"
            "stop task <pid>\n"
            "    Приостановить выполнение процесса с указанным PID.\n\n"
            "continue task <pid>\n"
            "    Возобновить ранее приостановленный процесс.\n\n"
            "kill <pid>\n"
            "    Уничтожить процесс с указанным PID.\n\n"
            "finish\n"
            "    Приостановить загрузку новых заданий и завершить модель\n"
            "    после выполнения всех текущих процессов.\n\n"
            "seed <value>\n"
            "    Инициализировать генератор случайных чисел указанным значением (int).\n"
            "    Влияет только на будущие задания.\n\n"
            "help\n"
            "    Показать эту справку."
        )
