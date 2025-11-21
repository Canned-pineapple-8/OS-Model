# ui_pyqt_modern_layout.py

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QTextEdit,
    QLineEdit, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QGridLayout, QSplitter, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
import sys
import os

MONO_FONT = "Cascadia Mono"  # можно заменить на другой моноширинный

# -------------------- CPU / IO CARD --------------------
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

        self.info_keys = ["PID", "Память", "Длительность IO команды", "Счетчик IO команд", "Состояние"]
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


class CPUColumn(QWidget):
    def __init__(self, cpu_name, accent_color="#FF6F61", parent=None):
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

        title = QLabel(cpu_name)
        title.setFont(QFont(MONO_FONT, 12, weight=QFont.Weight.Bold))
        layout.addWidget(title)

        self.info_keys = ["PID", "Память", "Всего команд", "Счетчик команд", "Состояние"]
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
                if "wait" in state_str:
                    color = "#ffb300"
                elif "stop" in state_str or "term" in state_str:
                    color = "#f44336"
                self.labels[key].setStyleSheet(f"color:{color}; font-weight:bold; padding-left:2px;")
            self.labels[key].setText(text)


# -------------------- Process List (widget + dialog) --------------------
class ProcessListWidget(QWidget):
    """Встраиваемая панель с таблицей процессов"""
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

        # style file optional
        qss_path = os.path.join("ui", "process-table-style.qss")
        if os.path.exists(qss_path):
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


class ProcessListDialog(QDialog):
    """Всплывающее окно со списком процессов (использует ProcessListWidget)"""
    def __init__(self, os_model, parent=None):
        super().__init__(parent)
        self.os_model = os_model
        self.setWindowTitle("Список процессов")
        self.resize(700, 420)
        layout = QVBoxLayout(self)
        self.inner = ProcessListWidget(os_model, self)
        layout.addWidget(self.inner)
        # close button
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

    def update_list(self):
        self.inner.update_list()


# --------------------------- MAIN WINDOW -------------------------
class OSUI(QMainWindow):
    def __init__(self, os_model, update_interval_ms=100):
        super().__init__()
        self.os_model = os_model
        self.setWindowTitle("Модель ОС")
        self.resize(1200, 700)

        # central + main vertical layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Top controls (speed label + processes button)
        top_panel = QHBoxLayout()
        self.speed_label = QLabel(f"Скорость: {os_model.speed:.2f} тактов/сек")
        self.speed_label.setFont(QFont(MONO_FONT, 12))
        top_panel.addWidget(self.speed_label)
        top_panel.addStretch()
        main_layout.addLayout(top_panel)

        # Splitter: left (CPUs+IO) | right (process list)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)

        # ---------------- left panel ----------------
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(6, 6, 6, 6)
        left_layout.setSpacing(12)

        # Titles
        title_cpu = QLabel("Центральные процессоры")
        title_cpu.setFont(QFont(MONO_FONT, 12, weight=QFont.Weight.Bold))
        left_layout.addWidget(title_cpu)

        # Grid for CPU (3 in row)
        cpu_grid = QGridLayout()
        cpu_grid.setSpacing(12)
        self.cpu_columns = []
        cpu_colors = ["#FF6F61", "#FFB300", "#00BCD4"]
        for i in range(3):
            c = CPUColumn(f"ЦП {i+1}", accent_color=cpu_colors[i])
            self.cpu_columns.append(c)
            cpu_grid.addWidget(c, 0, i)  # row 0, columns 0..2
        left_layout.addLayout(cpu_grid)

        # IO title and grid
        title_io = QLabel("Процессоры ввода-вывода")
        title_io.setFont(QFont(MONO_FONT, 12, weight=QFont.Weight.Bold))
        left_layout.addWidget(title_io)

        io_grid = QGridLayout()
        io_grid.setSpacing(12)
        self.io_columns = []
        io_colors = ["#8BC34A", "#FFB300", "#9C27B0"]
        for i in range(3):
            io_c = IOColumn(f"IO {i+1}", accent_color=io_colors[i])
            self.io_columns.append(io_c)
            io_grid.addWidget(io_c, 0, i)
        left_layout.addLayout(io_grid)

        # allow left panel to grow vertically but keep reasonable width
        left_panel.setMinimumWidth(680)
        left_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        # ---------------- right panel ----------------
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(6, 6, 6, 6)
        right_layout.setSpacing(8)

        # embedded process list widget (visible)
        self.process_widget = ProcessListWidget(self.os_model, self)
        self.process_widget.setMinimumWidth(380)
        right_layout.addWidget(self.process_widget)

        # optional controls under table (e.g., filters) — left empty for now
        # right_layout.addStretch()

        right_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        # initial splitter sizes (left bigger)
        splitter.setSizes([760, 420])

        main_layout.addWidget(splitter)

        # ------ Log View ------
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont(MONO_FONT, 11))
        self.text_area.setMinimumHeight(180)
        main_layout.addWidget(self.text_area)

        # ---- Command Input ----
        cmd_layout = QHBoxLayout()
        self.cmd_entry = QLineEdit()
        self.cmd_entry.setFont(QFont(MONO_FONT, 11))
        self.cmd_entry.setPlaceholderText("speed+, speed-, terminate, /?")
        self.cmd_entry.returnPressed.connect(self.process_command)
        cmd_layout.addWidget(self.cmd_entry)

        send_btn = QPushButton("Отправить")
        send_btn.setFont(QFont(MONO_FONT, 11))
        send_btn.clicked.connect(self.process_command)
        cmd_layout.addWidget(send_btn)
        main_layout.addLayout(cmd_layout)

        # Load global QSS if exists
        qss_path = os.path.join("ui", "main-style.qss")
        if os.path.exists(qss_path):
            try:
                with open(qss_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            except Exception:
                pass
        else:
            # Minimal built-in styling to make UI cohesive without external file
            self.setStyleSheet("""
                QMainWindow { background-color: #121217; color: #f0f0f0; }
                QPushButton { background-color: #ff6f61; color: white; padding:6px 10px; border-radius:6px; }
                QPushButton:hover { background-color: #ff8a75; }
                QLineEdit, QTextEdit { background-color: #1c1c22; color: #f0f0f0; border: 1px solid #2a2a30; border-radius:6px; padding:6px; }
                QTableWidget { background-color: #1c1c22; color: #f0f0f0; }
                QHeaderView::section { background-color: #262630; color: #f0f0f0; padding:6px; }
            """)

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(update_interval_ms)

        # dialog for processes
        self.process_dialog = None
        self.closed = False

    # ---------------- update / helpers ----------------
    def append_text(self, txt: str):
        self.text_area.append(txt)

    def update_ui(self):
        # update speed
        try:
            self.speed_label.setText(f"Скорость: {self.os_model.speed:.2f} тактов/сек")
        except Exception:
            pass

        # CPUs
        for i, col in enumerate(self.cpu_columns):
            try:
                cpu = self.os_model.cpus[i]
                process = getattr(cpu, "current_process", None)
                if not process:
                    info = {k: "-" for k in col.info_keys}
                else:
                    try:
                        state = process.current_state.name
                    except Exception:
                        state = str(process.current_state)
                    info = {
                        "PID": process.pid,
                        "Память": getattr(process, "process_memory_config", {}).block_size
                                if getattr(process, "process_memory_config", None) else "-",
                        "Всего команд": getattr(getattr(process, "process_commands_config", None), "total_commands_cnt", "-"),
                        "Счетчик команд": getattr(getattr(process, "process_statistics", None), "total_commands_counter", "-"),
                        "Состояние": state
                    }
            except Exception as e:
                info = {k: "-" for k in col.info_keys}
                self.append_text(f"Ошибка CPU {i+1}: {e}")
            col.update_info(info)

        # IOs
        for i, col in enumerate(self.io_columns):
            try:
                io = self.os_model.io_controllers[i]
                process = getattr(io, "current_process", None)
                if not process:
                    info = {k: "-" for k in col.info_keys}
                else:
                    try:
                        state = process.current_state.name
                    except Exception:
                        state = str(process.current_state)
                    duration = getattr(getattr(process, "current_command", None), "duration", "-")
                    info = {
                        "PID": process.pid,
                        "Память": getattr(process, "process_memory_config", {}).block_size
                                  if getattr(process, "process_memory_config", None) else "-",
                        "Длительность IO команды": duration,
                        "Счетчик IO команд": getattr(io, "current_ticks_executed", "-"),
                        "Состояние": state
                    }
            except Exception as e:
                info = {k: "-" for k in col.info_keys}
                self.append_text(f"Ошибка IO {i+1}: {e}")
            col.update_info(info)

        # processes table (right embedded)
        try:
            self.process_widget.update_list()
        except Exception:
            pass


    # ---------- commands ----------
    def process_command(self):
        cmd = self.cmd_entry.text().strip().lower()
        if not cmd:
            return
        self.cmd_entry.clear()
        self.append_text(f"> {cmd}")

        try:
            if cmd == "speed+":
                s = self.os_model.change_speed(True)
                self.append_text(f"Скорость увеличена до {s:.2f}")
            elif cmd == "speed-":
                s = self.os_model.change_speed(False)
                self.append_text(f"Скорость уменьшена до {s:.2f}")
            elif cmd == "terminate":
                self.append_text("Завершение...")
                try:
                    self.os_model.terminate()
                except Exception:
                    pass
                self.close()
            elif cmd == "/?":
                self.append_text("Команды:\nspeed+\nspeed-\nterminate\n/?")
            else:
                self.append_text("Неизвестная команда!")
        except Exception as e:
            self.append_text(f"Ошибка: {e}")

    # ---------- close ----------
    def closeEvent(self, event):
        if not self.closed:
            self.closed = True
            try:
                self.os_model.terminate()
            except Exception:
                pass
        event.accept()


def run_ui(os_model, interval_ms=100):
    app = QApplication(sys.argv)
    ui = OSUI(os_model, interval_ms)
    ui.show()
    sys.exit(app.exec())
