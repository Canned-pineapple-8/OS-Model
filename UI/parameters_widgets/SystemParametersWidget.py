from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QScrollArea, QWidget
from PyQt6.QtGui import QFont
from UI.parameters_widgets.KeyValuePanel import KeyValuePanel, MONO_FONT


class SystemParamsWidget(QWidget):
    """
    Область параметров системы с вкладками Входные/Выходные/Средние.
    В правом верхнем углу находится кнопка отображения памяти.
    """
    def __init__(self, os_model, memory_btn_callback, parent=None):
        super().__init__(parent)
        self.os_model = os_model

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6,6,6,6)

        header = QHBoxLayout()
        title = QLabel("Параметры системы")
        title.setFont(QFont(MONO_FONT, 12, weight=QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        self.mem_btn = QPushButton("Память")
        self.mem_btn.setFont(QFont(MONO_FONT, 11))
        self.mem_btn.clicked.connect(memory_btn_callback)
        header.addWidget(self.mem_btn)
        self.layout.addLayout(header)

        try:
            with open("UI/stylesheets/system-params.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass

        # вкладки
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.layout.addWidget(self.tabs)

        # входные параметры системы
        self.input_panel = KeyValuePanel()
        inp = self._wrap_scroll(self.input_panel)
        self.tabs.addTab(inp, "Входные параметры системы")

        # выходные параметры системы
        self.output_panel = KeyValuePanel()
        outp = self._wrap_scroll(self.output_panel)
        self.tabs.addTab(outp, "Выходные параметры системы")

        # средние параметры процессов
        self.mean_panel = KeyValuePanel()
        meanw = self._wrap_scroll(self.mean_panel)
        self.tabs.addTab(meanw, "Средние параметры процессов")

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
        la.setContentsMargins(6,6,6,6)
        la.addWidget(widget)
        scroll.setWidget(cont)
        return scroll

    def _fill_placeholders(self):
        inp = {
            "Скорость (тактов/сек)": getattr(self.os_model, "speed", "-"),
            "Общая память (int)": getattr(self.os_model.config.memory, "total_memory", "-"),
            "Размер таблицы процессов": getattr(self.os_model.config.memory, "proc_table_size", "-"),
            "Количество ЦП": getattr(self.os_model.config.cpu, "cpus_num", "-"),
            "Квант (такты)": getattr(self.os_model.config.cpu, "quantum_size", "-"),
            "Мин память процесса": getattr(self.os_model.config.process_generation, "min_memory", "-"),
            "Макс память процесса": "-",
            "Время выбора процесса (такты)": "-",
            "Затраты при IO (такты)": "-",
            "Затраты на обработку IO_END (такты)": "-",
            "Затраты на загрузку задания (такты)": "-",
            "Затраты на общие данные (такты)": "-"
        }
        self.input_panel.bulk_set(inp)

        out = {
            "Число загруженных заданий": lambda: len(getattr(self.os_model, "proc_table", {})),
            "Системные затраты ОС (%)": "-",
            "Время работы модели (сек)": "-",
            "Число выполненных заданий": "-",
            "Оборотное время (avg)": "-",
            "T_multi (mono) (заглушка)": "-",
            "Число заданий за T_multi (заглушка)": "-",
            "Производительность vs mono (%)": "-"
        }
        resolved = {k: (v() if callable(v) else v) for k, v in out.items()}
        self.output_panel.bulk_set(resolved)

        mean = {
            "T_mono_i (среднее)": "-",
            "T_multi_i (среднее)": "-",
            "D_exe (%)": "-",
            "D_ready (%)": "-"
        }
        self.mean_panel.bulk_set(mean)

    def refresh(self):
        self.input_panel.set("Скорость (тактов/сек)", getattr(self.os_model, "speed", "-"))
        self.output_panel.set("Число загруженных заданий", str(len(getattr(self.os_model, "proc_table", {}))))
