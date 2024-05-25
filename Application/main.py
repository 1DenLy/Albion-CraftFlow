import sys

from PyQt5.QtWidgets import QApplication

from window import Window



app = QApplication(sys.argv)

window = Window()
window.set_screen(window.start_window_ui)

if __name__ == "__main__":
    sys.exit(app.exec_())
