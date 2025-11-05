import sys, time, threading

from datetime import datetime, timedelta


from PIL import Image
import pystray

from pystray import MenuItem, Icon

from PyQt5.QtWidgets import QApplication


class SystemTrayIcon:
    def __init__(self, icon_path, end_date):
        self.icon_path = icon_path

        self.icon = Icon("urlM_icon", Image.open(self.icon_path), "Miner", menu=self._create_menu())

        # Flags for system tray icon
        self.thread = None
        self.running = True  

        # End date for system tray icon
        self.end_date = end_date

        # Intervals per second for working system tray
        self.interval_list = []


    # ----------------------------------------------------------------
    # Create menu for icon
    def _create_menu(self):
        """Create menu for system tray icon"""

        return pystray.Menu(
            MenuItem("Exit", self.on_quit)
        )


    # ----------------------------------------------------------------
    # Quit function
    def on_quit(self, icon, item):
        """Обработка выхода из приложения."""

        self.running = False  
        icon.stop()  

        print("Завершение фонового потока...")

        if self.thread is not None:
            self.thread.join()  # Ожидание завершения фонового потока
        print("Приложение завершено.")



    def periodic_task(self):
        """Задача, которая будет выполняться периодически."""


        print("Выполнение периодической задачи...")
        

    # Function with intervals between tasks
    def run_app(self):
        """Запускает фоновый процесс, который выполняет периодическую задачу до заданной даты."""
        
        while self.running:
            
            if datetime.now() < self.end_date:
                
                self.periodic_task()  # TASK
                time.sleep(15)  # Wait # interval between

            else:
                print("Конечная дата достигнута. Остановка фоновой задачи.")
                self.running = False  



    # ----------------------------------------------------------------
    # Start function for periodic tasks
    def start(self):
        """Запускает иконку и фоновый процесс."""

        # Запускаем иконку в отдельном потоке
        icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        icon_thread.start()

        self.thread = threading.Thread(target=self.run_app, daemon=True)
        self.thread.start()

        




if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Установка конечной даты (например, через 10 часов от текущего момента)
    end_date = datetime.now() + timedelta(hours=10)

    # Запуск класса системного трея
    tray_icon = SystemTrayIcon("Url_manager/icon_file.jpg", end_date)
    tray_icon.start()

    app.exec_()
    print("Цикл обработки событий завершён.")
