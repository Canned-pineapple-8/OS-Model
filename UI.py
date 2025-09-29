import tkinter as tk
from OSModel import OSModel

class OSUI:
    def __init__(self, os_model: OSModel):
        self.os_model = os_model

        # инициализация окна
        self.root = tk.Tk()
        self.root.title("Модель ОС")
        self.root.geometry("400x300")

        # метки состояния
        self.current_pid_label = tk.Label(self.root, text="PID активного процесса: -")
        self.current_pid_label.pack(pady=5)

        self.command_counter_label = tk.Label(self.root, text="Счетчик команд активного процесса: 0")
        self.command_counter_label.pack(pady=5)

        self.speed_label = tk.Label(self.root, text=f"Скорость: {self.os_model.speed:.2f} тактов/сек")
        self.speed_label.pack(pady=5)

        # область для истории команд
        self.text_area = tk.Text(self.root, height=10, state=tk.DISABLED)
        self.text_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # поле для ввода команды
        self.command_entry = tk.Entry(self.root)
        self.command_entry.pack(padx=5, pady=5, fill=tk.X)
        self.command_entry.bind("<Return>", self.process_command)

        # запускаем автообновление интерфейса
        self.start_auto_update(interval=100)

        # флаг для остановки интерфейса
        self.running = True

        # запуск главного цикла Tkinter
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def update_ui(self):
        """Обновление состояния интерфейса"""
        try:
            current_pid = self.os_model.get_current_process_pid()
            current_proc = self.os_model.proc_table[current_pid]
            self.current_pid_label.config(text=f"PID активного процесса: {current_pid}")
            self.command_counter_label.config(text=f"Счетчик команд активного процесса: {current_proc.command_counter}")
        except RuntimeError as e:
            self.current_pid_label.config(text="PID активного процесса: -")
            self.command_counter_label.config(text="Счетчик команд активного процесса: 0")
            self.append_text(f"Ошибка времени выполнения: {e}")

        self.speed_label.config(text=f"Скорость: {self.os_model.speed:.2f} тактов/сек")

    def start_auto_update(self, interval=100):
        """Запуск периодического обновления интерфейса"""
        self.update_ui()
        self.root.after(interval, self.start_auto_update, interval)

    def process_command(self, event):
        """Обработка команд из поля ввода и вывод в историю"""
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
