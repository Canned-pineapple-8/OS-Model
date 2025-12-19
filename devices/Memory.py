from typing import *


class Memory:
    def __init__(self, memory_size: int, stats) -> None:
        """
        Инициализация физической памяти
        Память моделируется как список элементов
        типа int (машинное слово/операнд в вычислениях) / None, если память не инициализирована (мусор)
        :param memory_size: размер памяти (в машинных словах)
        """
        self.physical_memory_size: int = memory_size
        self.physical_memory: List[Optional[int]] = [None] * memory_size
        self.stats = stats

    def read(self, address:int) -> Optional[int]:
        """
        Прочитать слово по адресу address
        :param address: адрес машинного слова
        :return: прочитанное машинное слово (или None) / RuntimeException при попытке обратиться за границы
        """
        if address < 0 or address >= self.physical_memory_size:
            raise RuntimeError("Попытка чтения памяти за допустимыми пределами.")
        return self.physical_memory[address]

    def write(self, value:Optional[int], address:int) -> None:
        """
        Записать машинное слово value по адресу address
        :param value: слово для записи
        :param address: адрес
        """
        if address < 0 or address >= self.physical_memory_size:
            raise RuntimeError("Попытка записи в память за допустимыми пределами.")
        self.physical_memory[address] = value


