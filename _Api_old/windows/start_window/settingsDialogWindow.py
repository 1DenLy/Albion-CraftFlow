
from PyQt5 import QtWidgets


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Настройки")
        self.setGeometry(100, 100, 300, 150)

        self.layout = QtWidgets.QVBoxLayout()

        self.label_font = QtWidgets.QLabel("Выберите размер шрифта:")
        self.layout.addWidget(self.label_font)
        self.spinBox = QtWidgets.QSpinBox()
        self.spinBox.setRange(8, 48)
        self.layout.addWidget(self.spinBox)

        self.label_language = QtWidgets.QLabel("Выберите язык:")
        self.layout.addWidget(self.label_language)
        self.languageComboBox = QtWidgets.QComboBox()
        self.languageComboBox.addItems(["English", "Russian"])
        self.layout.addWidget(self.languageComboBox)

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def get_font_size(self):
        return self.spinBox.value()

    def set_font_size(self, size):
        self.spinBox.setValue(size)

    def get_language(self):
        return self.languageComboBox.currentText()

    def set_language(self, language):
        index = self.languageComboBox.findText(language)
        if index != -1:
            self.languageComboBox.setCurrentIndex(index)
