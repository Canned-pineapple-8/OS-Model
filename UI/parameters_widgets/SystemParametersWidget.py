from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QWidget
)
from PyQt6.QtGui import QFont
from UI.parameters_widgets.KeyValuePanel import KeyValuePanel, MONO_FONT


class SystemParamsWidget(QWidget):
    def __init__(self, os_model, memory_btn_callback, parent=None):
        super().__init__(parent)
        self.os_model = os_model

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6, 6, 6, 6)

        header = QHBoxLayout()
        title = QLabel("Параметры системы")
        title.setFont(QFont(MONO_FONT, 16, weight=QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        self.mem_btn = QPushButton("Память")
        self.mem_btn.setFont(QFont(MONO_FONT, 16))
        self.mem_btn.clicked.connect(memory_btn_callback)
        header.addWidget(self.mem_btn)

        self.layout.addLayout(header)

        try:
            with open("UI/stylesheets/system-params.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.input_panel = KeyValuePanel()
        self.tabs.addTab(self._wrap_scroll(self.input_panel), "Входные параметры системы")

        self.output_panel = KeyValuePanel()
        self.tabs.addTab(self._wrap_scroll(self.output_panel), "Выходные параметры системы")

        self.mean_panel = KeyValuePanel()
        self.tabs.addTab(self._wrap_scroll(self.mean_panel), "Средние параметры процессов")

        self._input_getters = {}
        self._out_getters = {}
        self._mean_getters = {}

        self._init_input_panel()
        self._init_output_panel()
        self._init_mean_panel()

        self.setObjectName("SystemParamsWidget")
        self.tabs.setObjectName("SystemParamsTabs")
        self.mem_btn.setObjectName("MemoryButton")
        title.setObjectName("SystemParamsTitle")

    def _wrap_scroll(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        cont = QWidget()
        la = QVBoxLayout(cont)
        la.setContentsMargins(6, 6, 6, 6)
        la.addWidget(widget)

        scroll.setWidget(cont)
        return scroll

    def _fmt(self, v):
        if isinstance(v, float):
            return f"{v:.3f}".rstrip("0").rstrip(".")
        return str(v)

    def _init_input_panel(self):
        cfg = self.os_model.config

        sections = {
            "Параметры памяти": cfg.memory,
            "Параметры CPU": cfg.cpu,
            "Параметры IO": cfg.io,
            "Параметры скорости": cfg.speed,
            "Параметры генерации процессов": cfg.process_generation,
            "Параметры генерации команд": cfg.command_generation,
            "Сид для случайных операций": cfg.random,
            "Параметры временных затрат на системные процессы ОС": cfg.time_costs
        }

        placeholders = {}

        for section_name, section in sections.items():
            placeholders[f"    {section_name}"] = ""
            for field in vars(section).keys():
                key = f"{field}"
                placeholders[key] = "-"
                self._input_getters[key] = (
                    lambda s=section, f=field: self._fmt(getattr(s, f))
                )

        self.input_panel.bulk_set(placeholders)

    def _init_output_panel(self):
        self._out_getters = {
            "Число загруженных заданий (N_Proc)": lambda: len(self.os_model.proc_table),
            "Системные затраты ОС (%) (D_sys)": lambda: f"{self.os_model.stats.os_stats.d_system:.3f}".rstrip("0").rstrip("."),
            "Время работы модели (такты, T_multi)": lambda: f"{self.os_model.stats.os_stats.t_multi:.3f}".rstrip("0").rstrip("."),
            "Число выполненных заданий (M_multi)": lambda: f"{self.os_model.stats.os_stats.m_multi:.3f}".rstrip("0").rstrip("."),
            "Оборотное время (такты, T_обор)": lambda: f"{self.os_model.stats.os_stats.t_proc_avg_multi:.3f}".rstrip("0").rstrip("."),
            "Время выполнения заданий в однопрограммной ОС (T_mono)": lambda: f"{self.os_model.stats.os_stats.t_mono:.3f}".rstrip("0").rstrip("."),
            "Число заданий за T_multi в однопрограммной ОС (M_mono)": lambda: f"{self.os_model.stats.os_stats.m_mono:.3f}".rstrip("0").rstrip("."),
            "Производительность системы (%) (D_multi)": lambda: f"{self.os_model.stats.os_stats.d_multi:.3f}".rstrip("0").rstrip("."),
        }

        self.output_panel.bulk_set({k: "-" for k in self._out_getters})

    def _init_mean_panel(self):
        self._mean_getters = {
            "T_mono (такты, среднее)": lambda: f"{self.os_model.stats.avg_process_stats.t_mono_avg:.3f}".rstrip("0").rstrip("."),
            "T_multi (такты, среднее)": lambda: f"{self.os_model.stats.avg_process_stats.t_multi_avg:.3f}".rstrip("0").rstrip("."),
            "D_exe (%, среднее)": lambda: f"{self.os_model.stats.avg_process_stats.d_exe_avg:.3f}".rstrip("0").rstrip("."),
            "D_ready (%, среднее)": lambda: f"{self.os_model.stats.avg_process_stats.d_ready_avg:.3f}".rstrip("0").rstrip(".")
        }

        self.mean_panel.bulk_set({k: "-" for k in self._mean_getters})

    def refresh(self):
        for key, getter in self._input_getters.items():
            try:
                self.input_panel.set(key, getter())
            except Exception:
                self.input_panel.set(key, "-")

        for key, getter in self._out_getters.items():
            try:
                self.output_panel.set(key, getter())
            except Exception:
                self.output_panel.set(key, "-")

        for key, getter in self._mean_getters.items():
            try:
                self.mean_panel.set(key, getter())
            except Exception:
                self.mean_panel.set(key, "-")
