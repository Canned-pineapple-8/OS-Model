import json
from Config import *

class Speed:
    def __init__(self, config: OSConfig) -> None:
        """
        Инициализация параметров скорости (базовая, минимальная/максимальная, множитель)
        :param config: словарь json-параметров, результат работы json.load
        """
        self.speed = config.speed.speed                        # скорость моделирования
        self.speed_multiplier = config.speed.speed_multiplier  # множитель для уменьшения/увеличения скорости
        self.min_speed = config.speed.min_speed                # минимальная скорость
        self.max_speed = config.speed.max_speed                # максимальная скорость
        return

    def change_speed(self, increase: bool) -> float:
        """
        Увеличение/уменьшение скорости моделирования
        :param increase: для увеличения - True, Для уменьшения - False
        :return: новое значение скорости (float)
        """
        new_speed = self.speed
        if increase:
            new_speed += self.speed_multiplier * new_speed
        else:
            new_speed -= self.speed_multiplier * new_speed

        if new_speed > self.max_speed:
            new_speed = self.max_speed
        elif new_speed < self.min_speed:
            new_speed = self.min_speed

        self.speed = new_speed
        return self.speed

