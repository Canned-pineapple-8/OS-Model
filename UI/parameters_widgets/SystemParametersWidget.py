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
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.layout.addWidget(self.tabs)

        self.input_panel = KeyValuePanel()
        self.tabs.addTab(self._wrap_scroll(self.input_panel), "Входные параметры системы")

        self.output_panel = KeyValuePanel()
        self.tabs.addTab(self._wrap_scroll(self.output_panel), "Выходные параметры системы")

        self.mean_panel = KeyValuePanel()
        self.tabs.addTab(self._wrap_scroll(self.mean_panel), "Средние параметры процессов")

        self._out_getters = {}
        self._fill_placeholders()

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

    def _fill_placeholders(self):
        self.input_panel.bulk_set({
            "Скорость (тактов/сек)": "-",
            "Общая память (int)": "-",
            "Размер таблицы процессов": "-",
            "Количество ЦП": "-",
            "Квант (такты)": "-",
            "Мин память процесса": "-",
            "Макс память процесса": "-",
            "Время выбора процесса (такты)": "-",
            "Затраты при IO (такты)": "-",
            "Затраты на обработку IO_END (такты)": "-",
            "Затраты на загрузку задания (такты)": "-",
            "Затраты на общие данные (такты)": "-"
        })

        self._out_getters = {
            "Число загруженных заданий (N_Proc)": lambda: len(self.os_model.proc_table),
            "Системные затраты ОС (%) (D_sys)": lambda: f"{self.os_model.stats.os_stats.d_system:.3f}",
            "Время работы модели (такты, T_multi)": lambda: f"{self.os_model.stats.os_stats.t_multi:.3f}",
            "Число выполненных заданий (M_multi)": lambda: f"{self.os_model.stats.os_stats.m_multi:.3f}",
            "Оборотное время (такты, T_обор)": lambda: f"{self.os_model.stats.os_stats.t_proc_avg_multi:.3f}",
            "Время выполнения заданий в однопрограммной ОС (T_mono)": lambda: f"{self.os_model.stats.os_stats.t_mono:.3f}",
            "Число заданий за T_multi в однопрограммной ОС (M_mono)": lambda: f"{self.os_model.stats.os_stats.m_mono:.3f}",
            "Производительность системы (%) (D_multi)": lambda: f"{self.os_model.stats.os_stats.d_multi:.3f}",
        }

        self.output_panel.bulk_set({k: "-" for k in self._out_getters})

        self.mean_panel.bulk_set({
            "T_mono_i (среднее)": "-",
            "T_multi_i (среднее)": "-",
            "D_exe (%)": "-",
            "D_ready (%)": "-"
        })

    def refresh(self):
        for key, getter in self._out_getters.items():
            try:
                self.output_panel.set(key, getter())
            except Exception:
                self.output_panel.set(key, "-")
