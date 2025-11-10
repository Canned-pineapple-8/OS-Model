from typing import *
from Memory import Memory


class MemoryManager:
    def __init__(self, memory_ptr: Memory):
        """
        Инициализация менеджера памяти
        :param memory_ptr: указатель на структуру физической памяти
        """
        # таблица сегментов - структура типа Dict[адрес_начала_блока, Tuple[Optional[PID_процесса], размер_блока]
        self.memory_map: Dict[int, Tuple[Optional[int], int]] = dict()
        self.memory_ptr = memory_ptr
        self.available_memory = self.memory_ptr.physical_memory_size

    def find_free_block(self, req_size: int) -> Tuple[Optional[int], Optional[int]]:
        """
        Находит первый свободный блок размером >= req_size в таблице сегментов
        :param req_size: требуемый размер
        :return: если сегментов подходящего размера нет - (None, None)
        иначе - (адрес_начала_блока, размер_блока)
        """
        if req_size < 0:
            raise RuntimeError(f"Неверный требуемый размер блока ({req_size})")
        index = 0
        while index < self.memory_ptr.physical_memory_size:
            if index not in self.memory_map:
                raise RuntimeError("Таблица сегментов повреждена")
            if self.memory_map[index][0] is None:
                if self.memory_map[index][1] >= req_size:
                    return self.memory_map[index]
            index += self.memory_map[index][1]
        return None, None

    def allocate_memory_for_process(self, process_pid: int, req_size: int) -> None:
        """
        Выделение памяти под новый процесс
        :param process_pid: PID процесса, который должен быть размещен
        :param req_size: требуемый размер памяти под процесс
        """
        free_block = self.find_free_block(req_size=req_size)
        if free_block == (None, None):
            raise RuntimeError(f"Недостаточно памяти для процесса {process_pid} (требуемое количество: {req_size})")
        address, free_block_size = free_block
        self.memory_map[address] = (process_pid, req_size)
        if free_block_size > req_size:
            self.memory_map[address + req_size] = (None, free_block_size - req_size)

        self.update_available_memory(0 - req_size)

    def free_memory_from_process(self, process_pid: int) -> None:
        """
        Освобождает память от процесса и обновляет свободную память
        :param process_pid: который нужно удалить из памяти
        """
        if process_pid not in self.memory_map:
            raise RuntimeError(f"Процесса {process_pid} не существует")
        process_address, process_size = self.memory_map.pop(process_pid)

        start_address = process_address
        new_size = process_size

        # проверяем левый соседний блок
        left = start_address - 1
        while left >= 0 and left not in self.memory_map:
            left -= 1
        if left >= 0 and self.memory_map[left][0] is None:
            left_address, left_size = self.memory_map.pop(left)
            start_address = left_address
            new_size += left_size

        # проверяем правый соседний блок
        right = process_address + process_size
        while right < self.memory_ptr.physical_memory_size and right not in self.memory_map:
            right += 1
        if right < self.memory_ptr.physical_memory_size and self.memory_map[right][0] is None:
            _, right_size = self.memory_map.pop(right)
            new_size += right_size

        # создаём новый объединённый свободный блок
        self.memory_map[start_address] = (None, new_size)
        self.update_available_memory(new_size)

    def update_available_memory(self, value: int) -> None:
        """
        Обновление размера свободной памяти (увеличение/уменьшение)
        :param value: значение увеличения/уменьшения
        """
        if self.available_memory + value < 0:
            self.available_memory = 0
        elif self.available_memory + value > self.memory_ptr.physical_memory_size:
            self.available_memory = self.memory_ptr.physical_memory_size
        else:
            self.available_memory += value


