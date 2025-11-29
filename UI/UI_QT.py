from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QTextEdit,
    QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import sys

from UI.IOColumn import IOColumn
from UI.CPUColumn import CPUColumn
from UI.ProcessList import ProcessListWidget
from UI.MemoryViewer import MemoryViewer
MONO_FONT = "Cascadia Mono"


class OSUI(QMainWindow):
    def __init__(self, os_model, update_interval_ms=100):
        super().__init__()
        self.os_model = os_model
        self.setWindowTitle("Модель ОС")
        self.resize(1200, 700)

        # центральный виджет + основной layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # панель скорости
        top_panel = QHBoxLayout()
        self.speed_label = QLabel(f"Скорость: {os_model.speed:.2f} тактов/сек")
        self.speed_label.setFont(QFont(MONO_FONT, 12))
        top_panel.addWidget(self.speed_label)

        # кнопка просмотра памяти
        mem_btn = QPushButton("Память")
        mem_btn.setFont(QFont(MONO_FONT, 12))
        mem_btn.clicked.connect(self.show_memory_viewer)
        top_panel.addWidget(mem_btn)

        top_panel.addStretch()
        main_layout.addLayout(top_panel)

        # слева (CPUs+IO) | справа (список процессов)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)

        # левая панель
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(6, 6, 6, 6)
        left_layout.setSpacing(12)

        # заголовок
        title_cpu = QLabel("Центральные процессоры")
        title_cpu.setFont(QFont(MONO_FONT, 12, weight=QFont.Weight.Bold))
        left_layout.addWidget(title_cpu)

        # сетка для процессоров
        cpu_grid = QGridLayout()
        cpu_grid.setSpacing(12)
        self.cpu_columns = []
        for i in range(3):
            c = CPUColumn(f"ЦП {i + 1}", accent_color="#FF6F61")
            self.cpu_columns.append(c)
            cpu_grid.addWidget(c, 0, i)
        left_layout.addLayout(cpu_grid)

        # заголовок для IO
        title_io = QLabel("Процессоры ввода-вывода")
        title_io.setFont(QFont(MONO_FONT, 12, weight=QFont.Weight.Bold))
        left_layout.addWidget(title_io)

        # сетка для IO
        io_grid = QGridLayout()
        io_grid.setSpacing(12)
        self.io_columns = []
        for i in range(3):
            io_c = IOColumn(f"IO {i + 1}", accent_color="#8BC34A")
            self.io_columns.append(io_c)
            io_grid.addWidget(io_c, 0, i)
        left_layout.addLayout(io_grid)

        left_panel.setMinimumWidth(680)
        left_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        # правая панель
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(6, 6, 6, 6)
        right_layout.setSpacing(8)

        self.process_widget = ProcessListWidget(self.os_model, self)
        self.process_widget.setMinimumWidth(380)
        right_layout.addWidget(self.process_widget)

        right_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([760, 420])

        main_layout.addWidget(splitter)

        # терминал
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont(MONO_FONT, 11))
        self.text_area.setMinimumHeight(180)
        main_layout.addWidget(self.text_area)

        # область ввода
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

        # загрузка стиля
        qss_path = "UI/stylesheets/main-style.qss"
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            # минимальный стиль (если нет .qss)
            self.setStyleSheet("""
                QMainWindow { background-color: #121217; color: #f0f0f0; }
                QPushButton { background-color: #ff6f61; color: white; padding:6px 10px; border-radius:6px; }
                QPushButton:hover { background-color: #ff8a75; }
                QLineEdit, QTextEdit { background-color: #1c1c22; color: #f0f0f0; border: 1px solid #2a2a30; border-radius:6px; padding:6px; }
                QTableWidget { background-color: #1c1c22; color: #f0f0f0; }
                QHeaderView::section { background-color: #262630; color: #f0f0f0; padding:6px; }
            """)

        # таймер
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(update_interval_ms)

        # dialog for processes
        self.process_dialog = None
        self.closed = False

    def show_memory_viewer(self):
        try:
            viewer = MemoryViewer(self.os_model.memory_manager)
            viewer.exec()
        except Exception as e:
            self.append_text(f"[Ошибка MemoryViewer]: {e}")

    def append_text(self, txt: str):
        self.text_area.append(txt)

    # обновление UI
    def update_ui(self):
        # обновление скорости
        try:
            self.speed_label.setText(f"Скорость: {self.os_model.speed:.2f} тактов/сек")
        except Exception:
            pass

        # инфо о ЦП
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
                    if process.current_command is not None:
                        try:
                            command_type = process.current_command.type.name
                        except Exception:
                            command_type = str(process.current_command.type)
                    else:
                        command_type = "-"

                    info = {
                        "PID": process.pid,
                        "Всего команд": getattr(getattr(process, "process_commands_config", None), "total_commands_cnt",
                                                "-"),
                        "Счетчик команд": getattr(getattr(process, "process_statistics", None),
                                                  "total_commands_counter", "-"),
                        "Тип текущей команды": command_type,
                        "Состояние": state,
                        "Такты": cpu.ticks_executed
                    }
            except Exception as e:
                info = {k: "-" for k in col.info_keys}
                self.append_text(f"Ошибка CPU {i + 1}: {e}")
            col.update_info(info)

        # инфо о IO
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
                    if process.current_command is not None:
                        try:
                            command_type = process.current_command.type.name
                        except Exception:
                            command_type = str(process.current_command.type)
                    else:
                        command_type = "-"
                    duration = getattr(getattr(process, "current_command", None), "duration", "-")
                    info = {
                        "PID": process.pid,
                        "Длительность IO команды": duration,
                        "Счетчик IO команд": getattr(io, "current_ticks_executed", "-"),
                        "Тип текущей команды": command_type,
                        "Состояние": state
                    }
            except Exception as e:
                info = {k: "-" for k in col.info_keys}
                self.append_text(f"Ошибка IO {i + 1}: {e}")
            col.update_info(info)

        # таблица процессов
        try:
            self.process_widget.update_list()
        except Exception:
            pass

    # команды
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
                self.append_text("Доступные команды:\n"
                                 "speed+      — увеличить скорость моделирования\n"
                                 "speed-      — уменьшить скорость\n"
                                 "terminate   — завершить моделирование\n"
                                 "/?          — показать справку")
            else:
                self.append_text("Неизвестная команда!")
        except Exception as e:
            self.append_text(f"Ошибка: {e}")

    # закрытие окна
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
    ui.showMaximized()
    sys.exit(app.exec())
