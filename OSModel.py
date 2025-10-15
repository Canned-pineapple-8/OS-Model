from collections import deque

from Process import Process
from Speed import Speed
from Scheduler import Scheduler
from CPU import CPU
from RandomFactory import ProcessFactory
import json
import os
import time
import random
from EventBus import *
import threading


def generate_new_task(memory: int = -1, regular_commands_size: int = -1,
                      io_commands_percentage: float = -1.0, priority: int = -1) -> Process:
    """
    Генерация нового процесса с возможностью случайной инициализации параметров.

    :param memory: объём памяти процесса (если -1 — сгенерируется случайно)
    :param regular_commands_size: количество команд CPU (если -1 — случайно)
    :param io_commands_percentage: доля I/O команд (если -1.0 — случайно)
    :param priority: приоритет (если -1 — случайно)
    :return: экземпляр Process
    """

    if memory == -1:
        memory = random.randint(10, 500)

    if regular_commands_size == -1:
        regular_commands_size = random.randint(1, 3)

    if io_commands_percentage == -1.0:
        io_commands_percentage = round(random.uniform(0.0, 0.5), 2)

    if priority == -1:
        priority = random.randint(0, 10)

    new_process = Process(
        memory=memory,
        regular_commands_size=regular_commands_size,
        io_commands_percentage=io_commands_percentage,
        priority=priority
    )

    return new_process


class OSModel:
    def __init__(self, config_path: str, event_bus: EventBus) -> None:
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

        self.event_bus = event_bus
        self.event_bus.subscribe(EventType.PROCESS_TERMINATED, self.remove_process_from_process_table)

        self._lock = threading.Lock()

        # инициализация параметров из JSON
        self.total_memory = config.get("total_memory", 1024)  # общая память модели
        self.proc_table_size = config.get("proc_table_size",
                                          10)  # максимальное число процессов (объем таблицы слов состояний процессов)
        cpus_num = config.get("cpus_num", 3)  # количество процессоров

        # инициализация основных структур модели
        self.proc_table = dict()  # таблица процессов: dict [int, Process] (Доступ по PID)
        self.cpus = [CPU(self.event_bus) for _ in range(cpus_num)]
        self.speed_manager = Speed(config)  # инициализация параметров, связанных со скоростью (делегируется классу Speed)
        self.scheduler = Scheduler(self.cpus, self.event_bus)  # инициализация планировщика и его структур
        self.running = True
        return

    @property
    def speed(self) -> float:
        """Геттер для скорости"""
        return self.speed_manager.speed

    def change_speed(self, increase:bool = True):
        """
        Увеличение/уменьшение скорости моделирования (геттер метода speed_manager)
        :param increase: для увеличения - True, Для уменьшения - False
        :return: новое значение скорости (float)
        """
        new_speed = self.speed_manager.change_speed(increase)
        return new_speed

    @property
    def process_queue(self) -> deque:
        """Геттер для очереди"""
        return self.scheduler.process_queue

    def calculate_memory_usage(self) -> int:
        """
        Вычисление текущей используемой памяти (сумма используемой памяти по всем процессам в таблице процессов)
        :return: размер текущей используемой памяти, целое число
        """
        return sum([process.memory for process in self.proc_table.values()])

    def calculate_available_memory(self) -> int:
        """
        Вычисление текущей свободной памяти (общая память минус используемая)
        :return: размер текущей свободной памяти, целое число
        """
        memory_usage = self.calculate_memory_usage()
        return self.total_memory - memory_usage

    def load_new_task(self, process: Process) -> int:
        """
        Загрузка новой задачи, если есть место в таблице процессов и достаточно памяти
        :param process: задача (процесс) на загрузку
        :return: PID загруженного процесса
        """
        if len(self.proc_table.items()) >= self.proc_table_size:
            raise RuntimeError("Достигнуто максимальное количество загруженных задач.")

        if self.calculate_available_memory() < process.memory:
            raise RuntimeError("Недостаточно памяти для загрузки нового процесса.")

        with self._lock:
            self.proc_table[process.pid] = process
        self.event_bus.emit(EventType.PROCESS_CREATED, process=process)
        return process.pid

    def perform_program_delay(self) -> None:
        """
        Выполнение программной задержки
        """
        if self.speed > 0:
            delay = 1.0 / self.speed
            time.sleep(delay)
        else:
            time.sleep(0.01)
        return

    def terminate(self) -> None:
        """
        Завершение моделирования (очистка структур и установление флага)
        :return: void
        """
        with self._lock:
            self.proc_table.clear()
        self.process_queue.clear()
        self.running = False
        return

    def remove_process_from_process_table(self, process_pid: int) -> None:
        """
        Удаляет процесс из таблицы процессов
        :param process_pid: PID процесса для удаления
        """
        with self._lock:
            self.proc_table.pop(process_pid, None)
        return

    def fill_processes_if_possible(self) -> None:
        """
        Заполняет память новыми процессами до достижения лимита.
        """
        new_process_memory = 10
        while self.calculate_available_memory() > new_process_memory:
            new_process = ProcessFactory.create(memory=new_process_memory)
            self.load_new_task(new_process)
        return

    def perform_tick(self) -> None:
        """
        Выполняет один такт моделирования. В его ходе:
        - планировщик распределяет задачи между ЦП (если есть освободившиеся)
        - каждый ЦП выполняет один такт назначенного ему процесса
        :return:
        """
        self.scheduler.dispatch()
        for cpu in self.cpus:
            cpu.execute_tick()
        return
