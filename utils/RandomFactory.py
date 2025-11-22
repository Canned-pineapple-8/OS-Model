import random


class RandomFactory:
    """
    Фабрика для генерации случайных параметров (процессов/команд).
    """
    @staticmethod
    def generate_random_int_value(min_value: int, max_value: int) -> int:
        """
        Генерация случайного int-значения в диапазоне [min_value, max_value]
        :param min_value: нижняя граница диапазона
        :param max_value: верхняя граница диапазона
        :return: сгенерированное значение
        """
        return random.randint(min_value, max_value)

    @staticmethod
    def generate_random_float_value(min_value:float, max_value: float, round_cnt:int = 2) -> float:
        """
        Генерация случайного float-значения в диапазоне [min_value, max_value] с округлением до round_cnt знаков
        :param min_value: нижняя граница диапазона
        :param max_value: верхняя граница диапазона
        :param round_cnt: точность
        :return: сгенерированное значение
        """
        return round(random.uniform(min_value, max_value), round_cnt)

