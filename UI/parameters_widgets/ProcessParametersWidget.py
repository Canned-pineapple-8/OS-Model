# UI/parameters_widgets/process_params_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from UI.parameters_widgets.KeyValuePanel import KeyValuePanel


class ProcessParamsWidget(QWidget):
    """
    Виджет параметров процессов с KeyValuePanel внутри ScrollArea.
    """
    def __init__(self, os_model, parent=None):
        super().__init__(parent)
        self.os_model = os_model

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6,6,6,6)
        self.layout.setSpacing(6)

        self.params_panel = KeyValuePanel()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(6,6,6,6)
        vbox.addWidget(self.params_panel)
        scroll.setWidget(container)

        self.layout.addWidget(scroll)

        self.params_panel.bulk_set({
            "Заглушка": "Параметры процессов будут здесь"
        })

        self.setObjectName("ProcessParamsWidget")

        try:
            with open("UI/stylesheets/process-params.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass

    def refresh(self):
        procs = getattr(self.os_model, "proc_table", {})
        self.params_panel.set("Заглушка", f"Количество процессов: {len(procs)}")
