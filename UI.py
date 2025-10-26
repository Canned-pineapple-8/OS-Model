import tkinter as tk
from tkinter import ttk
from OSModel import OSModel


class CPUColumn:
    """
    Колонка информации для одного ЦП
    """
    def __init__(self, parent, cpu_name):
        self.frame = tk.Frame(parent, bd=1, relief=tk.SOLID, padx=5, pady=5)
        self.frame.config(width=250, height=200)
        # Заголовок ЦП
        self.title_label = tk.Label(self.frame, text=cpu_name, font=("Arial", 12, "bold"))
        self.title_label.grid(row=0, column=0, pady=(0, 5))

        # Словарь меток для полей
        self.info_labels = {}
        self.info_keys = ["PID", "Память", "Всего команд", "Счетчик команд", "Состояние"]

        for i, key in enumerate(self.info_keys, start=1):
            lbl = tk.Label(self.frame, text=f"{key}: -", anchor="w")
            lbl.grid(row=i, column=0, sticky="w")
            self.info_labels[key] = lbl

    def update_info(self, process_info: dict):
        for key in self.info_keys:
            value = process_info.get(key, "-")
            self.info_labels[key].config(text=f"{key}: {value}")


class OSUI:
    def __init__(self, os_model: OSModel):
        self.os_model = os_model

        # Главное окно
        self.root = tk.Tk()
        self.root.title("Модель ОС")
        self.root.geometry("950x500")

        # Frame для всех колонок ЦП
        self.cpu_frame = tk.Frame(self.root)
        self.cpu_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаем колонки для ЦП
        self.cpu_columns = []
        for i in range(3):
            col = CPUColumn(self.cpu_frame, f"ЦП {i + 1}")
            col.frame.grid(row=0, column=i, sticky="n", padx=5)
            col.frame.config(width=300, height=200)
            col.frame.grid_propagate(False)
            self.cpu_columns.append(col)

        # Метка скорости
        self.speed_label = tk.Label(self.root, text=f"Скорость: {self.os_model.speed:.2f} тактов/сек")
        self.speed_label.pack(pady=5)

        # Кнопка — открыть окно со списком процессов
        self.show_processes_button = tk.Button(
            self.root,
            text="Показать список процессов",
            command=self.show_process_list_window
        )
        self.show_processes_button.pack(pady=5)

        # Текстовое поле для истории команд (внизу)
        self.text_area = tk.Text(self.root, height=10, state=tk.DISABLED)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Поле для ввода команд
        self.command_entry = tk.Entry(self.root)
        self.command_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.command_entry.bind("<Return>", self.process_command)

        # Запуск автообновления
        self.running = True
        self.start_auto_update(interval=1000)  # обновление каждые 1000 мс
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def update_ui(self):
        """Обновляет все визуальные элементы интерфейса"""
        self.speed_label.config(text=f"Скорость: {self.os_model.speed:.2f} тактов/сек")

        for i, col in enumerate(self.cpu_columns):
            try:
                process = self.os_model.cpus[i].current_process
                if process is None:
                    process_info = {
                        "PID": "-",
                        "Память": "-",
                        "Всего команд": "-",
                        "Счетчик команд": "-",
                        "Состояние": "-"
                    }
                else:
                    process_info = {
                        "PID": process.pid,
                        "Память": process.memory,
                        "Всего команд": process.commands_size,
                        "Счетчик команд": process.commands_counter,
                        "Состояние": process.current_state
                    }
            except Exception as e:
                process_info = {key: "-" for key in col.info_keys}
                self.append_text(f"Ошибка CPU {i + 1}: {e}")
            col.update_info(process_info)

        # Обновляем окно со списком процессов (если оно открыто)
        self.update_process_list()

    def start_auto_update(self, interval=1000):
        """Запускает периодическое обновление интерфейса"""
        self.update_ui()
        if self.running:
            self.root.after(interval, self.start_auto_update, interval)

    def show_process_list_window(self):
        """Открывает новое окно со списком текущих процессов"""
        if hasattr(self, "process_window") and self.process_window.winfo_exists():
            self.process_window.lift()
            return

        self.process_window = tk.Toplevel(self.root)
        self.process_window.title("Список процессов")
        self.process_window.geometry("400x300")

        self.tree = ttk.Treeview(self.process_window, columns=("PID", "State"), show="headings")
        self.tree.heading("PID", text="PID")
        self.tree.heading("State", text="Состояние")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        close_btn = tk.Button(self.process_window, text="Закрыть", command=self.process_window.destroy)
        close_btn.pack(pady=5)

        # Первичная загрузка
        self.update_process_list()

    def update_process_list(self):
        """Обновляет содержимое окна со списком процессов"""
        if not hasattr(self, "process_window") or not self.process_window.winfo_exists():
            return  # окно закрыто или не создано

        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Заполнение актуальными данными
        for pid, process in self.os_model.proc_table.items():
            self.tree.insert("", tk.END, values=(pid, process.current_state.name))

    def process_command(self, event):
        cmd = self.command_entry.get().strip().lower()
        self.command_entry.delete(0, tk.END)
        self.append_text(f"> {cmd}")

        if cmd == "speed+":
            new_speed = self.os_model.change_speed(increase=True)
            self.append_text(f"Скорость увеличена до {new_speed:.2f} тактов/сек")
        elif cmd == "speed-":
            new_speed = self.os_model.change_speed(increase=False)
            self.append_text(f"Скорость уменьшена до {new_speed:.2f} тактов/сек")
        elif cmd == "terminate":
            self.append_text("Завершение моделирования...")
            self.os_model.terminate()
            self.running = False
            self.root.destroy()
        elif cmd == "/?":
            self.show_help()
        else:
            self.append_text("Неизвестная команда. Введите '/?' для справки.")

    def append_text(self, message):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def show_help(self):
        help_text = (
            "Доступные команды:\n"
            "speed+      — увеличить скорость моделирования\n"
            "speed-      — уменьшить скорость\n"
            "terminate   — завершить моделирование\n"
            "/?          — показать справку"
        )
        self.append_text(help_text)

    def on_close(self):
        self.running = False
        self.os_model.terminate()
        self.root.destroy()
