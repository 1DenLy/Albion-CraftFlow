from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi


from button_logic import ButtonLogic
from AppManager import AppManager

# Tabs
from Tabs.Settings.settings_main import Settings_window
from Tabs.Craft.craft_main import Craft_window



class MyWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        # Загружаем компоненты
        loadUi("Api\main.ui", self)

        self.tab_load()
        # --------------------------------


        # Инициализация зависимостей

        self.manager = AppManager(app_name="Albion_Data_Manager")



        # --------------------------------




        try:
            self.button_logic = ButtonLogic(self, tab_element = self.tab_zone)
        except Exception as e:
            print(f"Button logic not working because V \n {e}")


        self.setup_clicked_connect()

        self.tab_zone.tabCloseRequested.connect(self.close_tab)
        
        


    def setup_clicked_connect(self):
        self.pushButton_settings.clicked.connect(lambda: self.button_logic.open_tab(tab= self.tab_settings, tab_name= "Settings"))
        self.pushButton_file_5.clicked.connect(lambda: self.button_logic.open_tab(tab= self.tab_craft, tab_name= "Craft"))


# База окна ----------------------------------------------------

    def close_tab(self, index):
        """Закрытие вкладки по индексу"""
        self.tab_zone.removeTab(index)

    def tab_load(self):
        """Загрузка вкладок"""
        self.tab_craft = Craft_window(self)

        # Добавьте другие вкладки по аналогии
        # self.tab_zone.addTab(OtherTab(), "Other Tab")


    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        new_width = self.width()
        new_height = self.height()

        self.window.setFixedSize(new_width, new_height)


if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()