from PyQt5.QtWidgets import QTabWidget, QWidget


class ButtonLogic:
    def __init__(self, main_window, tab_element: QTabWidget = None):
        """
        Конструктор принимает объект главного окна для доступа к его элементам.
        """
        self.main_window = main_window
        self.tab = tab_element


    def open_tab(self, tab, tab_name: str = "Tab"):

        new = self.tab.addTab(tab, tab_name)

        self.tab.setCurrentIndex(new)

        print(f"open tab {tab}")