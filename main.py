from OSModel import OSModel
from UI import OSUI
import threading


def main():
    # инициализация модели, параметры - в config.json
    path_to_config = "config.json"
    os_model = OSModel(config_path=path_to_config)

    if not os_model.running:
        print(f"Ошибка при запуске моделирования. Проверьте наличие конфигурационного файла {path_to_config}.")
        return

    # инициализация интерфейса (в отдельном потоке)
    ui_thread = threading.Thread(target=OSUI, args=(os_model,))
    ui_thread.start()

    # os_model.fill_processes_if_possible()

    # оcновной цикл моделирования ОС
    try:
        while os_model.running:
            try:
                os_model.fill_processes_if_possible()
                os_model.perform_tick()
            except RuntimeError as e:
                print(f"Ошибка при выполнении активного процесса: {e}")
                return
            # выполнение программной задержки
            os_model.perform_program_delay()
    except KeyboardInterrupt:
        os_model.terminate()

    ui_thread.join()


if __name__ == "__main__":
    main()
