from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import QFont, QColor

MONO_FONT = "Cascadia Mono"


# виджет со списком процессов
class ProcessListWidget(QWidget):
    def __init__(self, os_model, parent=None):
        super().__init__(parent)
        self.os_model = os_model

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("Список процессов")
        title.setFont(QFont(MONO_FONT, 12, weight=QFont.Weight.Bold))
        layout.addWidget(title)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["PID", "Состояние"])
        self.table.horizontalHeader().setFont(QFont(MONO_FONT, 10))
        self.table.verticalHeader().setFont(QFont(MONO_FONT, 10))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setFont(QFont(MONO_FONT, 10))
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)
        self.setLayout(layout)

        qss_path = "UI/stylesheets/process-table-style.qss"
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass

    def update_list(self):
        procs = getattr(self.os_model, "proc_table", {})
        self.table.setRowCount(0)
        for pid, process in procs.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(pid)))

            state = getattr(process, "current_state", None)
            try:
                state_text = state.name
            except Exception:
                state_text = str(state)
            item_state = QTableWidgetItem(state_text)

            s = state_text.lower()
            color = QColor("#4caf50")
            if "wait" in s:
                color = QColor("#ffb300")
            elif "stop" in s or "term" in s or "end" in s:
                color = QColor("#f44336")

            item_state.setForeground(color)
            self.table.setItem(row, 1, item_state)