from typing import *
from Command import OpType


class ALU:
    """
    Класс-реализация АЛУ
    """
    def execute_operation(self, operation_type: OpType, operand_1: int, operand_2: int) -> int:
        """
        Выполнение арифметической операции над двумя операндами
        :param operation_type: тип операции
        :param operand_1: первый операнд (int)
        :param operand_2: второй операнд (int)
        :return: результат операции
        """
        match operation_type:
            case OpType.ADD:
                return operand_1 + operand_2
            case OpType.SUB:
                return operand_1 - operand_2
            case OpType.MUL:
                return operand_1 * operand_2
            case OpType.DIV:
                return operand_1 // operand_2
            case _:
                raise RuntimeError(f"Передан неизвестный тип операции {operation_type}")
