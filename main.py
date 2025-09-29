from OSModel import OSModel
from UI import OSUI
import threading


def main():
    # инициализация модели, параметры - в config.json
    path_to_config = "config.json"
    os_model = OSModel(path_to_config)

    if not os_model.running:
        print(f"Ошибка при запуске моделирования. Проверьте наличие конфигурационного файла {path_to_config}.")
        return

    # генерация и загрузка одного процесса
    process = os_model.generate_new_task(memory=50)
    try:
        os_model.load_new_task(process)
        pass
    except RuntimeError as e:
        print(f"Ошибка при загрузке процесса: {e}")
        return

    # инициализация интерфейса (в отдельном потоке)
    ui_thread = threading.Thread(target=OSUI, args=(os_model,))
    ui_thread.start()

    # соновной цикл моделирования ОС
    try:
        while os_model.running:
            try:
                # выполнение такта активного процесса (первый в очереди)
                os_model.execute_current_process()
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
