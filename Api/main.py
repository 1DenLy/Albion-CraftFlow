from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi


from button_logic import ButtonLogic

# Tabs
from Tabs.Settings.settings_main import Settings_window




class MyWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        # Загружаем компоненты
        loadUi("Api\main.ui", self)

        self.tab_load()
        # --------------------------------


        try:
            self.button_logic = ButtonLogic(self, tab_element = self.tab_zone)
        except Exception as e:
            print(f"Button logic not working because V \n {e}")


        self.setup_clicked_connect()

        self.tab_zone.tabCloseRequested.connect(self.close_tab)
        


    def setup_clicked_connect(self):
        self.pushButton_settings.clicked.connect(lambda: self.button_logic.open_tab(tab= self.tab_settings, tab_name= "Settings"))

    def close_tab(self, index):
        """Закрытие вкладки по индексу"""
        self.tab_zone.removeTab(index)

    def tab_load(self):
        self.tab_settings = Settings_window()




    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # Получаем новые размеры окна
        new_width = self.width()
        new_height = self.height()

        # Масштабируем центральный виджет пропорционально размеру окна
        self.window.setFixedSize(new_width, new_height)


if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()