from enum import Enum


# тип команды
class CommandType(Enum):
    ALU = 1  # арифметическая
    IO = 2  # ввод-вывод
    EXIT = 3  # завершение команды


# тип арифметической операции
class OpType(Enum):
    ADD = 0  # сложение
    SUB = 1  # вычитание
    DIV = 2  # целочисленное деление
    MUL = 3  # умножение


class Command:
    """
    Базовый класс-команда
    """
    def __init__(self, command_type: CommandType):
        self.type = command_type  # тип команды


class ALUCommand(Command):
    """
    Арифметическая операция
    """
    def __init__(self, addr1: int, addr2: int, opType: OpType):
        super().__init__(CommandType.ALU)
        self.addr1 = addr1  # адреса операндов в памяти
        self.addr2 = addr2
        self.opType = opType  # тип арифметической операции


class IOCommand(Command):
    """
    Команда ввода-вывода
    """
    def __init__(self, duration: int):
        super().__init__(CommandType.IO)
        self.duration = duration  # длительность операции ввода-вывода в тактах


class ExitCommand(Command):
    """
    Команда завершения процесса
    """
    def __init__(self):
        super().__init__(CommandType.EXIT)
