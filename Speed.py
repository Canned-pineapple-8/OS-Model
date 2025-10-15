import json


class Speed:
    def __init__(self, config: dict) -> None:
        """
        Инициализация параметров скорости (базовая, минимальная/максимальная, множитель)
        :param config: словарь json-параметров, результат работы json.load
        """
        self.speed = config.get("speed", 1.0)  # скорость моделирования
        self.speed_multiplier = config.get("speed_multiplier", 0.05)  # множитель для уменьшения/увеличения скорости
        self.min_speed = config.get("min_speed", 0.1)  # минимальная скорость
        self.max_speed = config.get("max_speed", 1000)  # максимальная скорость
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

