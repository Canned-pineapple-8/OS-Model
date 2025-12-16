from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtGui import QFont
from UI.parameters_widgets.KeyValuePanel import KeyValuePanel
from dataclasses import asdict

MONO_FONT = "Cascadia Mono"


class ProcessParamsWidget(QWidget):
    def __init__(self, os_model, parent=None):
        super().__init__(parent)
        self.os_model = os_model

        self._initialized = False
        self._last_values = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        title = QLabel("Параметры процессов")
        title.setFont(QFont(MONO_FONT, 12, weight=QFont.Weight.Bold))
        title.setObjectName("title")
        layout.addWidget(title)

        self.params_panel = KeyValuePanel()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("params_scroll")

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(6, 6, 6, 6)
        vbox.addWidget(self.params_panel)
        scroll.setWidget(container)

        layout.addWidget(scroll)

        self.setObjectName("ProcessParamsWidget")

        try:
            with open("UI/stylesheets/process-params.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass

    def refresh(self):
        procs = getattr(self.os_model, "proc_table", {})

        current = {}

        if not procs:
            current["Процессы"] = "Нет активных процессов"
        else:
            for pid, proc in procs.items():
                p = f"PID {pid}"

                current[f"{p} | Состояние"] = proc.current_state.name

                for k, v in asdict(proc.process_memory_config).items():
                    current[f"{p} | Память | {k}"] = v

                for k, v in asdict(proc.process_statistics).items():
                    current[f"{p} | Статистика | {k}"] = v

                for k, v in asdict(proc.process_commands_config).items():
                    current[f"{p} | Команды | {k}"] = v

                current[f"{p} | Текущая команда"] = (
                    proc.current_command.__class__.__name__
                    if proc.current_command else "-"
                )

        if not self._initialized:
            self.params_panel.bulk_set(current)
            self._last_values = current
            self._initialized = True
            return

        for key, value in current.items():
            old = self._last_values.get(key)
            if old != value:
                self.params_panel.set(key, value)

        self._last_values = current
