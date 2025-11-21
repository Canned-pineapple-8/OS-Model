from OSModel import OSModel
from UI import OSUI
import threading

# main.py
import threading
import time
from OSModel import OSModel
from UI_QT import run_ui


def model_thread_fn(os_model):
    try:
        while os_model.running:
            try:
                os_model.fill_processes_if_possible()
                os_model.perform_tick()
            except RuntimeError as e:
                print(f"Ошибка при выполнении активного процесса: {e}")
                return
            os_model.perform_program_delay()
    except KeyboardInterrupt:
        os_model.terminate()


def main():
    path_to_config = "config.json"
    os_model = OSModel(config_path=path_to_config)

    if not os_model.running:
        print(f"Ошибка при запуске моделирования. Проверьте наличие конфигурационного файла {path_to_config}.")
        return

    # Запускаем модель в отдельном потоке (daemon=False, чтобы корректно завершиться)
    model_thread = threading.Thread(target=model_thread_fn, args=(os_model,), daemon=True)
    model_thread.start()

    # Запускаем UI в главном потоке (blocking)
    # update_interval_ms можно настроить (например 1000)
    run_ui(os_model, interval_ms=100)

    # После закрытия UI подождём завершения модели
    os_model.terminate()
    model_thread.join(timeout=2)

if __name__ == "__main__":
    main()
