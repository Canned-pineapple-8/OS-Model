import random
from Process import Process


class ProcessFactory:
    """
    Фабрика для генерации случайных процессов.
    """
    @staticmethod
    def create(memory=-1, regular_commands_size=-1, io_commands_percentage=-1.0, priority=-1) -> Process:
        if memory == -1:
            memory = random.randint(10, 500)
        if regular_commands_size == -1:
            regular_commands_size = random.randint(5, 10)
        if io_commands_percentage == -1.0:
            io_commands_percentage = round(random.uniform(0.0, 0.5), 2)
        if priority == -1:
            priority = random.randint(0, 10)
        return Process(memory, regular_commands_size, io_commands_percentage, priority)
