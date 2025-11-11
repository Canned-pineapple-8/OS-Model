import random

class RandomFactory:
    """
    Фабрика для генерации случайных параметров (процессов/команд).
    """
    @staticmethod
    def generate_random_int_value(min_value: int, max_value: int) -> int:
        return random.randint(min_value, max_value)

    @staticmethod
    def generate_random_float_value(min_value:float, max_value: float, round_cnt:int = 2) -> float:
        return round(random.uniform(min_value, max_value), round_cnt)

