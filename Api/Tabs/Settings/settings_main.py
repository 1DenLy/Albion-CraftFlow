from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
from PyQt5.uic import loadUi


class Settings_window(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        # Загружаем компоненты
        loadUi("Api\Tabs\Settings\settings.ui", self)

        self.main_window = main_window
        self.button_func()
    
    def button_func(self):

        self.pushButton_point_size_bigg.clicked.connect(lambda: self.adjust_font_size(1))
        self.pushButton_piont_size_smal.clicked.connect(lambda: self.adjust_font_size(-1))







    def adjust_font_size(self, delta):
        print('работа')
        """Изменение размера шрифта для всех кнопок и надписей"""
        # Получаем все дочерние элементы, включая кнопки и надписи
        widgets = self.findChildren(QWidget) + self.main_window.findChildren(QWidget)

        for widget in widgets:
            # Проверяем, поддерживает ли виджет изменение шрифта
            if hasattr(widget, "font"):
                font = widget.font()
                font.setPointSize(max(1, font.pointSize() + delta))  # Изменяем размер шрифта
                widget.setFont(font)




if __name__ == "__main__":
    app = QApplication([])
    window = Settings_window()
    window.show()
    app.exec_()