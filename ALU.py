from typing import *
from Process import OpType


class ALU:
    def execute_operation(self, operation_type: OpType, operand_1: int, operand_2: int) -> int:
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
