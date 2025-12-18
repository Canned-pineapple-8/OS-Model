from dataclasses import dataclass, field
from typing import Dict
from enum import Enum
from model.Config import TimeCosts

# сбор статистики для отображения и вычислений
@dataclass
class OSStats:
    tasks_loaded: int = 0  # число загруженных заданий
    d_system: float = 0  # системные затраты ОС (в процентах)
    t_multi: float = 0  # время работы системы (в тактах) (мультипрограммная система)
    t_sys_multi: float = 0  # время работы системы (в тактах) (мультипрограммная система)
    m_multi: float = 0  # число выполненных заданий с момента начала моделирования
    t_proc_avg_multi: float = 0  # оборотное время в мультипрограммной
    t_proc_avg_mono: float = 0  # оборотное время в мультипрограммной
    t_mono: float = 0  # время выполнения m_multi Заданий в однопрограммной системе
    m_mono: float = 0  # число заданий, которые могли бы выполниться за время running_time
    # в однопрограммной ОС
    d_multi: float = 0  # производительность модели по сравнению с однопрограммной (в процентах)


# контейнер для средних статистик процессов
@dataclass
class AvgProcessTimeStats:
    t_mono_avg: float = 0  # среднее t_mono по процессам
    t_multi_avg: float = 0  # среднее t_multi по процессам
    d_exe_avg: float = 0  # среднее d_exe по процессам
    d_ready_avg: float = 0  # среднее d_ready по процессам


# контейнер для хранения статистик процесса
@dataclass
class ProcessTimeStats:
    t_active: float = 0  # время активного выполнения процесса
    # = выполнение команд
    t_passive: float = 0  # время пассивного выполнения процесса
    # = нахождение в очередях
    t_sys_multi: float = 0  # системные издержки специфичные для
    # мультипрограммной системы
    t_sys_mono: float = 0  # системные издержки специфичные для
    # однопрограммной системы
    t_start: float = 0  # время загрузки задания в систему
    t_end: float = 0  # время выгрузки задания из системы
    t_mono: float = 0  # время выполнения в однопроцессорной системе
    t_multi: float = 0  # время выполнения в мультипрограммной системе
    d_exe: float = 0  # процент увеличения времени выполнения по сравнению с однопрограммной системой
    d_ready: float = 0  # процент простоя (нахождения в очереди) по сравнению с общим временем выполнения


class ProcessTimeRecordType(Enum):
    T_ACTIVE = 0
    T_PASSIVE = 1
    T_SYS_MULTI = 2
    T_SYS_MONO = 3


# класс для подсчёта времени исполнения процессов в одно- и мультипрограммной системе и формирования статистик
class Statistics:
    def __init__(self, config_ptr: TimeCosts, proc_table_ptr):
        self.time_costs = config_ptr
        self.proc_table = proc_table_ptr

        self.process_stats: Dict[int, ProcessTimeStats] = {}  # контейнер для хранения времени исполнения
        # процессов (доступ по PID)
        self.os_stats = OSStats()  # контейнер для выходной статистики системы
        self.avg_process_stats = AvgProcessTimeStats()  # класс для хранения средних параметров процессов

    def add_time_process(self, pid: int, add_to: ProcessTimeRecordType, value: float) -> None:
        """
        Увеличить время выполнения процесса
        :param pid: PID процесса
        :param add_to: категория временной затраты
        :param value: значение (в тактах)
        """
        if pid not in self.process_stats:
            self.process_stats[pid] = ProcessTimeStats()
            self.proc_table[pid].stats = self.process_stats[pid]
        else:
            match add_to:
                case ProcessTimeRecordType.T_ACTIVE:
                    self.process_stats[pid].t_active += value
                case ProcessTimeRecordType.T_PASSIVE:
                    self.process_stats[pid].t_passive += value
                case ProcessTimeRecordType.T_SYS_MONO:
                    self.process_stats[pid].t_sys_mono += value
                case ProcessTimeRecordType.T_SYS_MULTI:
                    self.process_stats[pid].t_sys_multi += value

    def add_time_os_multi(self, value: float) -> None:
        """
        Увеличить время выполнения системы в мультпрограммном режиме на value
        :param value: значение времени в тактах моделирования
        """
        self.os_stats.t_multi += value

    def add_sys_time_os_multi(self, value: float) -> None:
        """
        Увеличить системные затраты в мультпрограммном режиме на value
        :param value: значение времени в тактах моделирования
        """
        self.os_stats.t_sys_multi += value

    def add_time_os_mono(self, value: float) -> None:
        """
        Увеличить время выполнения системы в однопрограммном режиме на value
        :param value: значение времени в тактах моделирования
        """
        self.os_stats.t_mono += value

    def add_runtime_to_processes(self, proc_table_ptr) -> None:
        """
        Добавить активное/пассивное время выполнения ко всем процессам системы на каждом такте
        :param proc_table_ptr: указатель на таблицу процессов
        """
        from abstractions.Process import ProcessState

        for pid, process in proc_table_ptr.items():
            if process.current_state == ProcessState.RUNNING or process.current_state == ProcessState.IO_RUNNING:
                self.add_time_process(pid, ProcessTimeRecordType.T_ACTIVE, 1)
            elif process.current_state in [ProcessState.READY, ProcessState.IO_BLOCKED]:
                self.add_time_process(pid, ProcessTimeRecordType.T_PASSIVE, 1)

    def add_process_start_time(self, pid: int):
        """
        Зафиксировать начальное время нахождения процесса в системе
        :param pid: PID процесса
        """
        if pid not in self.process_stats:
            self.process_stats[pid] = self.proc_table[pid].stats
        self.process_stats[pid].t_start = self.os_stats.t_multi

    def add_process_end_time(self, pid: int):
        """
        Зафиксировать время время окончания жизни процесса и рассчитать его параметры
        :param pid: PID процесса
        """
        if pid not in self.process_stats:
            self.process_stats[pid] = ProcessTimeStats()
        process = self.process_stats[pid]
        process.t_end = self.os_stats.t_multi
        process.t_multi = process.t_end - process.t_start
        process.t_sys_multi = process.t_multi - process.t_active - process.t_passive
        process.t_mono = process.t_active + process.t_sys_mono
        process.d_exe = process.t_multi / process.t_mono * 100
        process.d_ready = process.t_passive / process.t_multi * 100

    def recalc_system_params(self):
        """
        Пересчитать параметры системы на основе времени процессов
        """
        summa, cnt = 0, 0
        for pid, stats in self.process_stats.items():
            if stats.t_end != 0:
                summa += stats.t_multi
                cnt += 1
        if cnt:
            self.os_stats.t_proc_avg_multi = summa / cnt  # среднее время выполнения задания в мультипрограммной системе

        self.os_stats.t_mono = 0
        summa, cnt = 0, 0
        for pid, stats in self.process_stats.items():
            if stats.t_end != 0:
                summa += stats.t_mono
                self.os_stats.t_mono += stats.t_mono  # время выполнения m_multi заданий в однопрограммной системе
                cnt += 1
        if cnt:
            self.os_stats.t_proc_avg_mono = summa / cnt  # среднее время выполнения задания в однопрограммной системе

        # число заданий, которые могли бы выполниться в однопрограммной системе за t_multi
        if self.os_stats.t_proc_avg_mono:
            self.os_stats.m_mono = self.os_stats.t_multi / self.os_stats.t_proc_avg_mono

        # производительность
        if self.os_stats.m_mono:
            self.os_stats.d_multi = self.os_stats.m_multi / self.os_stats.m_mono * 100

        # системные затраты ОС в мультипрограммной системе
        if self.os_stats.t_multi:
            self.os_stats.d_system = self.os_stats.t_sys_multi / self.os_stats.t_multi * 100

    def recalc_avg_process_params(self):
        """
        Пересчитать средние параметры процессов
        """
        t_mono = [s.t_mono for s in self.process_stats.values() if s.t_end != 0]
        if t_mono:
            self.avg_process_stats.t_mono_avg = sum(t_mono) / len(t_mono)

        t_multi = [s.t_multi for s in self.process_stats.values() if s.t_end != 0]
        if t_multi:
            self.avg_process_stats.t_multi_avg = sum(t_multi) / len(t_multi)

        d_exe = [s.d_exe for s in self.process_stats.values() if s.t_end != 0]
        if d_exe:
            self.avg_process_stats.d_exe_avg = sum(d_exe) / len(d_exe)

        d_ready = [s.d_ready for s in self.process_stats.values() if s.t_end != 0]
        if d_ready:
            self.avg_process_stats.d_ready_avg = sum(d_ready) / len(d_ready)







