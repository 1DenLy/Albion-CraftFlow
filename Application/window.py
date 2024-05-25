import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

from PYQT.Api.start_window import Ui_start_window


class Window(object):
    def __init__(self):

        self.Ui = None

        self.start_window_ui = Ui_start_window()
        self.main_window = QMainWindow()



    def set_screen(self, ui):
        ui.setupUi(self.main_window)
        self.main_window.show()



