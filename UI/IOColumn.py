from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QSizePolicy
)
from PyQt6.QtGui import QFont

MONO_FONT = "Cascadia Mono"


# виджет колонки с IO
class IOColumn(QWidget):
    def __init__(self, io_name, accent_color="#FF6F61", parent=None):
        super().__init__(parent)
        self.setMinimumWidth(220)
        self.setMinimumHeight(180)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.top_bar = QLabel()
        self.top_bar.setFixedHeight(6)
        self.top_bar.setStyleSheet(f"background-color: {accent_color}; border-radius: 3px;")
        layout.addWidget(self.top_bar)

        title = QLabel(io_name)
        title.setFont(QFont(MONO_FONT, 12, weight=QFont.Weight.Bold))
        layout.addWidget(title)

        self.info_keys = ["PID", "Длительность IO команды", "Счетчик IO команд", "Тип текущей команды", "Состояние"]
        self.labels = {}
        for key in self.info_keys:
            lbl = QLabel(f"{key}: -")
            lbl.setFont(QFont(MONO_FONT, 10))
            lbl.setContentsMargins(4, 2, 4, 2)
            layout.addWidget(lbl)
            self.labels[key] = lbl

        layout.addStretch()
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f25;
                border-radius: 10px;
                color: #f0f0f0;
            }
        """)

    def update_info(self, info: dict):
        for key, val in info.items():
            text = f"{key}: {val}"
            if key == "Состояние":
                state_str = str(val).lower()
                color = "#4caf50"
                if "end" in state_str or "stop" in state_str or "term" in state_str:
                    color = "#f44336"
                elif "wait" in state_str:
                    color = "#ffb300"
                self.labels[key].setStyleSheet(f"color:{color}; font-weight:bold; padding-left:2px;")
            self.labels[key].setText(text)
