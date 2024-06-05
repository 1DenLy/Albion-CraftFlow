import sys
from PyQt5.QtWidgets import QMainWindow

from PYQT.Api.start_window import Ui_start_window
#from PYQT.Api.profit_tree_window import Ui_craft_tree_window 


class Window(object):
    def __init__(self):

        self.main_window = QMainWindow()

        self.start_window_ui = Ui_start_window()
        #self.craft_tree_window_ui = Ui_craft_tree_window()
        #self.prices_window_ui = Ui_prices_window()
        #self.statistics_window_ui = Ui_statistics_window()



    def set_Ui(self, ui):
        ui.setupUi(self.main_window)
        self.main_window.show()



