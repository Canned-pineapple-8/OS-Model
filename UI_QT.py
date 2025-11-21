# ui_pyqt_modern.py

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QTextEdit,
    QLineEdit, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
import sys

MONO_FONT = "Cascadia Mono"

class IOColumn(QWidget):
    """Стильная карточка CPU с цветовым акцентом и просторной компоновкой"""
    def __init__(self, io_name, accent_color="#FF6F61", parent=None):
        super().__init__(parent)
        self.setMinimumWidth(280)
        self.setMinimumHeight(280)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Цветная верхняя полоса
        self.top_bar = QLabel()
        self.top_bar.setFixedHeight(8)
        self.top_bar.setStyleSheet(f"background-color: {accent_color}; border-radius: 4px;")
        layout.addWidget(self.top_bar)

        # Заголовок
        title = QLabel(io_name)
        title.setFont(QFont(MONO_FONT, 13, weight=QFont.Weight.Bold))
        layout.addWidget(title)

        # Поля
        self.info_keys = ["PID", "Память", "Длительность IO команды", "Счетчик IO команд", "Состояние"]
        self.labels = {}

        for key in self.info_keys:
            lbl = QLabel(f"{key}: -")
            lbl.setFont(QFont(MONO_FONT, 11))
            lbl.setContentsMargins(6, 4, 6, 4)
            layout.addWidget(lbl)
            self.labels[key] = lbl

        layout.addStretch()
        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f25;
                border-radius: 14px;
                color: #f0f0f0;
            }
        """)

    def update_info(self, info):
        for key, val in info.items():
            text = f"{key}: {val}"

            if key == "Состояние":
                state_str = str(val).lower()
                color = "#4caf50"  # running

                if "end" in state_str:
                    color = "#f44336"

                self.labels[key].setStyleSheet(
                    f"color:{color}; font-weight:bold; padding-left:2px;"
                )

            self.labels[key].setText(text)

class CPUColumn(QWidget):
    """Стильная карточка CPU с цветовым акцентом и просторной компоновкой"""
    def __init__(self, cpu_name, accent_color="#FF6F61", parent=None):
        super().__init__(parent)
        self.setMinimumWidth(280)
        self.setMinimumHeight(280)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Цветная верхняя полоса
        self.top_bar = QLabel()
        self.top_bar.setFixedHeight(8)
        self.top_bar.setStyleSheet(f"background-color: {accent_color}; border-radius: 4px;")
        layout.addWidget(self.top_bar)

        # Заголовок
        title = QLabel(cpu_name)
        title.setFont(QFont(MONO_FONT, 13, weight=QFont.Weight.Bold))
        layout.addWidget(title)

        # Поля
        self.info_keys = ["PID", "Память", "Всего команд", "Счетчик команд", "Состояние"]
        self.labels = {}

        for key in self.info_keys:
            lbl = QLabel(f"{key}: -")
            lbl.setFont(QFont(MONO_FONT, 11))
            lbl.setContentsMargins(6, 4, 6, 4)
            layout.addWidget(lbl)
            self.labels[key] = lbl

        layout.addStretch()
        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f25;
                border-radius: 14px;
                color: #f0f0f0;
            }
        """)

    def update_info(self, info):
        for key, val in info.items():
            text = f"{key}: {val}"

            if key == "Состояние":
                state_str = str(val).lower()

                color = "#4caf50"  # running

                if "wait" in state_str:
                    color = "#ffb300"
                elif "stop" in state_str or "term" in state_str:
                    color = "#f44336"

                self.labels[key].setStyleSheet(
                    f"color:{color}; font-weight:bold; padding-left:2px;"
                )

            self.labels[key].setText(text)


# ------------------------ PROCESS LIST ---------------------------
class ProcessListDialog(QDialog):
    """Аккуратный список процессов"""
    def __init__(self, os_model, parent=None):
        super().__init__(parent)
        self.os_model = os_model

        self.setWindowTitle("Список процессов")
        self.resize(700, 400)

        layout = QVBoxLayout()

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["PID", "Состояние"])
        self.table.horizontalHeader().setFont(QFont(MONO_FONT, 10))
        self.table.verticalHeader().setFont(QFont(MONO_FONT,10))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setFont(QFont(MONO_FONT, 11))

        layout.addWidget(self.table)

        self.setLayout(layout)

        # Стиль окна
        with open("ui/process-table-style.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def update_list(self):
        procs = getattr(self.os_model, "proc_table", {})

        self.table.setRowCount(0)
        for pid, process in procs.items():
            row = self.table.rowCount()
            self.table.insertRow(row)

            # PID
            self.table.setItem(row, 0, QTableWidgetItem(str(pid)))

            # State
            state = getattr(process, "current_state", None)
            try:
                state_text = state.name
            except:
                state_text = str(state)

            item_state = QTableWidgetItem(state_text)

            # Цвет состояния
            s = state_text.lower()
            color = QColor("#4caf50")
            if "wait" in s:
                color = QColor("#ffb300")
            elif "stop" in s or "term" in s:
                color = QColor("#f44336")

            item_state.setForeground(color)
            self.table.setItem(row, 1, item_state)


# --------------------------- MAIN WINDOW -------------------------
class OSUI(QMainWindow):

    def __init__(self, os_model, update_interval_ms=100):
        super().__init__()
        self.os_model = os_model

        self.setWindowTitle("Модель ОС")
        self.resize(1100, 650)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        boxes = QWidget()
        boxes_layout = QHBoxLayout(boxes)

        vertical_boxes = QWidget()
        vertical_boxes.setMinimumWidth(800)

        v_boxes_layout = QVBoxLayout(vertical_boxes)

        cpu_title = QLabel("Центральные процессоры")
        cpu_title.setFont(QFont(MONO_FONT, 13, weight=QFont.Weight.Bold))
        v_boxes_layout.addWidget(cpu_title)

        # -------- CPU block --------
        cpu_layout = QHBoxLayout()
        cpu_layout.setSpacing(20)

        cpu_colors = ["#FF6F61", "#FFB300", "#00BCD4"]
        self.cpu_columns = []

        for i in range(3):
            col = CPUColumn(f"ЦП {i+1}", accent_color=cpu_colors[i])
            self.cpu_columns.append(col)
            cpu_layout.addWidget(col)

        v_boxes_layout.addLayout(cpu_layout)

        io_title = QLabel("Процессоры ввода-вывода")
        io_title.setFont(QFont(MONO_FONT, 13, weight=QFont.Weight.Bold))
        v_boxes_layout.addWidget(io_title)

        # -------- IO block --------
        io_layout = QHBoxLayout()
        io_layout.setSpacing(20)

        io_colors = ["#FF6F61", "#FFB300", "#00BCD4"]
        self.io_columns = []

        for i in range(3):
            col = IOColumn(f"IO {i+1}", accent_color=io_colors[i])
            self.io_columns.append(col)
            io_layout.addWidget(col)

        v_boxes_layout.addLayout(io_layout)

        boxes_layout.addWidget(vertical_boxes)

        self.processes = ProcessListDialog(self.os_model, self)
        self.processes.setMinimumWidth(400)

        boxes_layout.addWidget(self.processes)

        main_layout.addWidget(boxes)

        # ----- speed + button ------
        top_panel = QHBoxLayout()

        self.speed_label = QLabel(f"Скорость: {os_model.speed:.2f} тактов/сек")
        self.speed_label.setFont(QFont(MONO_FONT, 12))
        top_panel.addWidget(self.speed_label)

        top_panel.addStretch()

        main_layout.addLayout(top_panel)

        # ------ Log View -------
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont(MONO_FONT, 11))
        self.text_area.setMinimumHeight(150)
        main_layout.addWidget(self.text_area)

        # ---- Command Input ----
        cmd = QHBoxLayout()

        self.cmd_entry = QLineEdit()
        self.cmd_entry.setFont(QFont(MONO_FONT, 11))
        self.cmd_entry.setPlaceholderText("speed+, speed-, terminate, /?")
        self.cmd_entry.returnPressed.connect(self.process_command)
        cmd.addWidget(self.cmd_entry)

        send_btn = QPushButton("Отправить")
        send_btn.setFont(QFont(MONO_FONT, 11))
        send_btn.clicked.connect(self.process_command)
        cmd.addWidget(send_btn)

        main_layout.addLayout(cmd)

        # ----- Global Style ----
        with open("ui/main-style.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(update_interval_ms)

        self.process_window = None
        self.closed = False

    # --------------- Internal Methods -------------------
    def append_text(self, text):
        self.text_area.append(text)

    def update_ui(self):
        # Speed update
        try:
            self.speed_label.setText(f"Скорость: {self.os_model.speed:.2f} тактов/сек")
        except:
            pass

        # CPU cards
        for i, col in enumerate(self.cpu_columns):
            try:
                cpu = self.os_model.cpus[i]
                process = cpu.current_process

                if not process:
                    info = {k: "-" for k in col.info_keys}
                else:
                    try:
                        state = process.current_state.name
                    except:
                        state = str(process.current_state)

                    info = {
                        "PID": process.pid,
                        "Память": process.process_memory_config.block_size,
                        "Всего команд": process.process_commands_config.total_commands_cnt,
                        "Счетчик команд": process.process_statistics.total_commands_counter,
                        "Состояние": state
                    }

            except Exception as e:
                info = {k: "-" for k in col.info_keys}
                self.append_text(f"Ошибка CPU {i+1}: {e}")

            col.update_info(info)

        for i, col in enumerate(self.io_columns):
            try:
                io = self.os_model.io_controllers[i]
                process = io.current_process

                if not process:
                    info = {k: "-" for k in col.info_keys}
                else:
                    try:
                        state = process.current_state.name
                    except:
                        state = str(process.current_state)

                    info = {
                        "PID": process.pid,
                        "Память": process.process_memory_config.block_size,
                        "Длительность IO команды": process.current_command.duration,
                        "Счетчик IO команд": io.current_ticks_executed,
                        "Состояние": state
                    }

            except Exception as e:
                info = {k: "-" for k in col.info_keys}
                self.append_text(f"Ошибка IO {i+1}: {e}")

            col.update_info(info)

        # Process window update
        self.processes.update_list()

    # -------- Command Handling ----------
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
                self.os_model.terminate()
                self.close()

            elif cmd == "/?":
                self.append_text("Команды:\nspeed+\nspeed-\nterminate\n/?")

            else:
                self.append_text("Неизвестная команда!")

        except Exception as e:
            self.append_text(f"Ошибка: {e}")

    def closeEvent(self, event):
        if not self.closed:
            self.closed = True
            try:
                self.os_model.terminate()
            except:
                pass
        event.accept()


# -------------- EXTERNAL START FUNCTION ---------------------
def run_ui(os_model, interval_ms=100):
    app = QApplication(sys.argv)
    ui = OSUI(os_model, interval_ms)
    ui.show()
    sys.exit(app.exec())
