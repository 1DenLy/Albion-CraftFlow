
import sys, os

from PyQt5 import QtCore, QtGui, QtWidgets

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))


from Api.windows.parsed_items_price.main import Ui_Parcer
from Url_manager.main import URL_parser


from Api.windows.start_window.settingsDialogWindow import SettingsDialog
from utils.file_manager.file_manager import Files





class Ui_start_window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Ui_start_window, self).__init__(parent)
        self.file_manager = Files()


        self.language = self.file_manager.settings.get("language", "English")
        self.font_size = self.file_manager.settings.get("font_size", "12")

        self.setupUi()

        # Window Settings
        self.window_settings = QtCore.QSettings("main_window", "window")
        self._load_window_settings()

        # Windows To
        self.parcer_window = Ui_Parcer(file_manager= self.file_manager)


        self.OT_parcer_task = URL_parser(file_manager= self.file_manager )

#----------------------------------------------------------------
# Create the window
    def setupUi(self):
        self.setObjectName("main_Wind")
        self.resize(250, 500)
        self.setStyleSheet("")

        self.central_widg = QtWidgets.QWidget(self)
        self.central_widg.setStyleSheet("#central_widg{background-image:url(:/image/image.png);background-position: center;}")
        self.setCentralWidget(self.central_widg)

        self.frame = QtWidgets.QFrame(self.central_widg)
        self.frame.setGeometry(QtCore.QRect(40, 0, 170, 500))
        self.frame.setStyleSheet("border-radius: 10px;")
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(10, 20, 10, 20)
        self.verticalLayout.setSpacing(26)
        self.verticalLayout.setObjectName("verticalLayout")

        self.craft_pushButton = self.create_button("craft_pushButton", self.font_size)
        self.parcer_pushButton = self.create_button("parcer_pushButton", self.font_size)
        self.price_analysis_puchButton = self.create_button("price_analysis_puchButton", self.font_size)
        self.statistics_pushButton = self.create_button("statistics_pushButton", self.font_size)
        self.autoClouse_checkBox = self.create_checkbox(self.font_size)
        self.settings_pushButton = self.create_button("settings_pushButton", self.font_size)
        self.exit_pushButton = self.create_button("exit_pushButton", self.font_size)

        self.verticalLayout.addWidget(self.craft_pushButton)
        self.verticalLayout.addWidget(self.parcer_pushButton)
        self.verticalLayout.addWidget(self.price_analysis_puchButton)
        self.verticalLayout.addWidget(self.statistics_pushButton)
        self.verticalLayout.addWidget(self.autoClouse_checkBox, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.verticalLayout.addWidget(self.settings_pushButton)
        self.verticalLayout.addWidget(self.exit_pushButton)

        self.exit_pushButton.clicked.connect(self.exit_pushButton_clicked)
        #self.settings_pushButton.clicked.connect(self.show_settings_dialog)
        self.parcer_pushButton.clicked.connect(self.parcer_pushButton_clicked)

        self.update_font_size()
        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        translations = {
            "English": {
                "title": "Main Window",
                "craft": "Craft",
                "parser": "Parser",
                "price_analysis": "Price Analysis",
                "statistics": "Statistics",
                "auto_close": "Auto Close",
                "settings": "Settings",
                "exit": "Exit"
            },
            "Russian": {
                "title": "Главное окно",
                "craft": "Крафт",
                "parser": "Парсер",
                "price_analysis": "Анализ цен",
                "statistics": "Статистика",
                "auto_close": "Автозакрытие",
                "settings": "Настройки",
                "exit": "Выход"
            }
        }

        trans = translations.get(self.language, translations["English"])

        self.setWindowTitle(_translate("main_Wind", trans["title"]))
        self.craft_pushButton.setText(_translate("main_Wind", trans["craft"]))
        self.parcer_pushButton.setText(_translate("main_Wind", trans["parser"]))
        self.price_analysis_puchButton.setText(_translate("main_Wind", trans["price_analysis"]))
        self.statistics_pushButton.setText(_translate("main_Wind", trans["statistics"]))
        self.autoClouse_checkBox.setText(_translate("main_Wind", trans["auto_close"]))
        self.settings_pushButton.setText(_translate("main_Wind", trans["settings"]))
        self.exit_pushButton.setText(_translate("main_Wind", trans["exit"]))

    def create_button(self, name, font_size):
        button = QtWidgets.QPushButton(self.frame)
        button.setEnabled(True)
        button.setMaximumSize(QtCore.QSize(160, 45))
        font = QtGui.QFont()
        font.setFamily("High Tower Text")
        font.setPointSize(font_size)
        font.setBold(True)
        font.setItalic(True)
        button.setFont(font)
        button.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(191, 0, 153, 255), stop:1 rgba(0, 140, 178, 255))")
        button.setObjectName(name)
        return button

    def create_checkbox(self, font_size):
        checkbox = QtWidgets.QCheckBox(self.frame)
        font = QtGui.QFont()
        font.setPointSize(font_size)
        font.setBold(True)
        checkbox.setFont(font)
        checkbox.setStyleSheet("color: white;")
        checkbox.setChecked(True)
        return checkbox


# ----------------------------------------------------------------
# Menu buttons logic

    def parcer_pushButton_clicked(self):
        self.parcer_window.show()

        if self.autoClouse_checkBox.isChecked():
            self.hide()
        
    def exit_pushButton_clicked(self):
        self.close()






# ----------------------------------------------------------------
# Resize window logic
    def resizeEvent(self, event):
        super(Ui_start_window, self).resizeEvent(event)
        self._center_frame()

    def _center_frame(self):
        frame_width = self.frame.width()
        frame_height = self.frame.height()
        central_widg_width = self.central_widg.width()
        central_widg_height = self.central_widg.height()

        x = (central_widg_width - frame_width) // 2
        y = (central_widg_height - frame_height) // 2

        self.frame.move(x, y)

    def _load_window_settings(self):

        width = self.window_settings.value("Width", 500, type=int)
        height = self.window_settings.value("Height", 250, type=int)
        self.resize(width, height)

        position = self.window_settings.value("Position", QtCore.QPoint(100, 100), type=QtCore.QPoint)
        self.move(position)


# ----------------------------------------------------------------
# Close event - Save all settings
    def closeEvent(self, event):
        self.window_settings.setValue("Width", self.width())
        self.window_settings.setValue("Height", self.height())
        self.window_settings.setValue("Position", self.pos())  
        super(Ui_start_window, self).closeEvent(event)




# ----------------------------------------------------------------
# Settings dialog window
    def show_settings_dialog(self):
        dialog = SettingsDialog(self)

        dialog.set_font_size(self.font_size)
        dialog.set_language(self.language)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:

            new_font_size = dialog.get_font_size()
            new_language = dialog.get_language()

            self.font_size = new_font_size
            self.language = new_language

            #save settings

            self.update_font_size(new_font_size)
            self.retranslateUi()


# ----------------------------------------------------------------
    def update_font_size(self):
        for widget in [self.craft_pushButton, self.parcer_pushButton, self.price_analysis_puchButton, self.statistics_pushButton, self.autoClouse_checkBox, self.settings_pushButton, self.exit_pushButton]:
            widget_font = widget.font()
            widget_font.setPointSize(self.font_size)
            widget.setFont(widget_font)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_win = Ui_start_window()
    main_win.show()
    sys.exit(app.exec_())
