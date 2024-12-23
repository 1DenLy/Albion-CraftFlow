from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
from PyQt5.uic import loadUi


class Settings_window(QWidget):
    def __init__(self):
        super().__init__()
        # Загружаем компоненты
        loadUi("Api\Tabs\Settings\settings.ui", self)









if __name__ == "__main__":
    app = QApplication([])
    window = Settings_window()
    window.show()
    app.exec_()