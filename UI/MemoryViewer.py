from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QScrollArea, QWidget, QLabel, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QSize, QTimer


MONO_FONT = "Cascadia Mono"


class MemoryViewer(QDialog):
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.memory = memory_manager.memory_ptr

        self.setWindowTitle("Использование памяти")
        self.resize(900, 600)

        self.labels = []
        self.columns = 25

        self.process_colors = {}
        self.color_palette = [
            "#8BC34A",  # зеленый
            "#42A5F5",  # голубой
            "#26A69A",  # бирюзовый

            "#4CAF50",  # насыщенный зеленый
            "#AB47BC",  # фиолетовый
            "#FFA726",  # оранжево-янтарный
        ]

        self.setStyleSheet("""
            QDialog {
                background-color: #121217;
            }
            QWidget {
                background-color: #121217;
                color: #f0f0f0;
            }
        """)

        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(2)

        layout.addWidget(scroll)
        scroll.setWidget(container)

        self.create_cells()
        self.update_view()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_view)
        self.timer.start(300)

    def get_color_for_pid(self, pid):
        if pid not in self.process_colors:
            color = self.color_palette[
                len(self.process_colors) % len(self.color_palette)
            ]
            self.process_colors[pid] = color
        return self.process_colors[pid]

    def create_cells(self):
        total = self.memory.physical_memory_size
        cell_size = 32

        for index in range(total):
            label = QLabel()
            label.setFixedSize(QSize(cell_size, cell_size))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont(MONO_FONT, 9))
            label.setAutoFillBackground(True)

            row = index // self.columns
            col = index % self.columns

            self.grid.addWidget(label, row, col)
            self.labels.append(label)

    def update_view(self):
        total = self.memory.physical_memory_size

        mem_map = self.memory_manager.memory_map
        address_to_pid = [None] * total

        for start, (pid, block_size) in mem_map.items():
            for i in range(block_size):
                if 0 <= start + i < total:
                    address_to_pid[start + i] = pid

        for index in range(total):
            label = self.labels[index]
            pid = address_to_pid[index]
            value = self.memory.physical_memory[index]

            label.setText("" if value is None else str(value))

            if pid is None:
                bg = "#1c1c22"
            else:
                bg = self.get_color_for_pid(pid)

            label.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg};
                    color: #f0f0f0;
                    border: 1px solid #2a2a30;
                    border-radius: 4px;
                }}
            """)

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)
