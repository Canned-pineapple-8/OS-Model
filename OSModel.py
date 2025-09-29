from collections import deque
from Process import Process
import json
import os
import time


class OSModel:
    def __init__(self, config_path: str):
        """
        Инициализация модели ОС из JSON-файла.
        :param config_path: путь к JSON-файлу с параметрами
        """
        self.running = False

        if not os.path.exists(config_path):
            print(f"Файл конфигурации '{config_path}' не найден. Будут загружены значения по умолчанию.")
            config = dict()
        else:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                print(f"Ошибка чтения JSON-файла '{config_path}'. Будут загружены значения по умолчанию.")
                config = dict()

        # инициализация параметров из JSON
        self.total_memory = config.get("total_memory", 1024) # общая память модели
        self.proc_table_size = config.get("proc_table_size", 10) # максимальное число процессов (объем таблицы слов состояний процессов)
        self.speed = config.get("speed", 1.0) # скорость моделирования
        self.speed_multiplier = config.get("speed_multiplier", 0.05) # множитель для уменьшения/увеличения скорости
        self.min_speed = config.get("min_speed", 0.1) # минимальная скорость
        self.max_speed = config.get("max_speed", 1000) # максимальная скорость

        # инициализация основных структур модели
        self.proc_table = dict()  # таблица процессов: dict [int, Process] (Доступ по PID)
        self.process_queue = deque()  # очередь на исполнение процессов: deque [int] (Доступ по PID)
        self.free_pid = 0 # свободное значение PID Для новых процессов

        self.running = True

    def get_current_process_pid(self) -> int:
        """
        Возвращает PID активного процесса с проверкой на корректность (ненулевая очередь, наличие PID процесса из очереди в таблице процессов)
        :return: PID активного процесса, гарантированно присутствующий в таблице процессов
        """
        if len(self.process_queue) == 0:
            raise RuntimeError("Отсутствуют процессы в очереди.")
        if len(self.proc_table) == 0 or self.process_queue[0] not in self.proc_table.keys():
            raise RuntimeError("Таблица процессов/очередь процессов повреждены.")
        return self.process_queue[0]

    def generate_new_task(self, memory: int = 10):
        """
        Генерация нового задания
        :param memory: минимальная память, необходимая для процесса
        :return: созданный объект Process
        """
        new_process = Process(self.free_pid, memory)
        self.free_pid += 1

        return new_process

    def calculate_memory_usage(self):
        """
        Вычисление текущей используемой памяти (сумма используемой памяти по всем процессам в таблице процессов)
        :return: размер текущей используемой памяти, целое число
        """
        return sum([process.memory for process in self.proc_table.values()])

    def calculate_available_memory(self):
        """
        Вычисление текущей свободной памяти (общая память минус используемая)
        :return: размер текущей свободной памяти, целое число
        """
        memory_usage = self.calculate_memory_usage()
        return self.total_memory - memory_usage

    def load_new_task(self, process: Process):
        """
        Загрузка новой задачи, если есть место в таблице процессов и достаточно памяти
        :param process: задача (процесс) на загрузку
        :return: PID загруженного процесса
        """
        if len(self.proc_table.items()) >= self.proc_table_size:
            raise RuntimeError("Достигнуто максимальное количество загруженных задач.")

        if self.calculate_available_memory() < process.memory:
            raise RuntimeError("Недостаточно памяти для загрузки нового процесса.")

        self.proc_table[process.pid] = process
        self.process_queue.append(process.pid)
        return process.pid

    def execute_current_process(self):
        """
        Выполнение очередного такта активного процесса (активным считается процесс в начале очереди)
        :return: void
        """
        active_pid = self.get_current_process_pid()
        proc = self.proc_table[active_pid]
        proc.execute_tick()

    def perform_program_delay(self):
        """
        Выполнение программной задержки
        :return: void
        """
        if self.speed > 0:
            delay = 1.0 / self.speed
            time.sleep(delay)

    def terminate(self):
        """
        Завершение моделирования (очистка структур и установление флага)
        :return: void
        """
        self.proc_table.clear()
        self.process_queue.clear()
        self.running = False

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

        return new_speed


