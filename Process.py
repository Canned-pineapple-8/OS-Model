class Process:
    def __init__(self, pid: int, memory: int = 10):
        """
        Инициализация процесса
        :param pid: идентификатор процесса (целое неотрицательное число)
        :param memory: минимальная память, необходимая для процесса (целое неотрицательное число)
        """
        self.pid = pid
        self.memory = memory
        self.command_counter = 0

    def execute_tick(self):
        """
        Выполнить такт процесса (увеличение счётчика команд процесса на единицу)
        :return:
        """
        self.command_counter += 1