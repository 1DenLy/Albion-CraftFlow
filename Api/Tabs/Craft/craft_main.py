from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QButtonGroup
from PyQt5.uic import loadUi

import json
import os

class Craft_window(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        # Загружаем компоненты
        loadUi("Api\Tabs\Craft\craft.ui", self)

        self.main_window = main_window
        self.button_func()

        self.items = {}
        self.folder_path = "item_info"
        self.load_items()
        print(self.items)

        self.combobox_func()

    def load_items(self):
        if not os.path.isdir(self.folder_path):
            print(f"Папка '{self.folder_path}' не найдена.")
            return

        for filename in os.listdir(self.folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(self.folder_path, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                        key = os.path.splitext(filename)[0]  # Имя файла без .json
                        self.items[key] = data
                except Exception as e:
                    print(f"Ошибка при загрузке '{filename}': {e}")



    def button_func(self):
        group1 = QButtonGroup(self)

        group1.addButton(self.Prise_materials_radioButton_1, 1)
        group1.addButton(self.Prise_materials_radioButton_2, 2)
        group1.addButton(self.Prise_materials_radioButton_3, 3)
        group1.addButton(self.Prise_materials_radioButton_4, 4)
        group1.addButton(self.Prise_materials_radioButton_5, 5)
        group1.addButton(self.Prise_materials_radioButton_6, 6)
        group1.addButton(self.Prise_materials_radioButton_7, 7)
        group1.addButton(self.Personal_Prise_materials_radioButton, 8) 

        group1.setExclusive(True)
        self.selected_radio = None
        self.group1 = group1

        group1.buttonClicked[int].connect(self.on_radio_selected)


        group2 = QButtonGroup(self)
        group2.addButton(self.radioButton_char_0, 1)
        group2.addButton(self.radioButton_char_1, 2)
        group2.addButton(self.radioButton_char_2, 3)
        group2.addButton(self.radioButton_char_3, 4)
        group2.addButton(self.radioButton_char_4, 5)
        group1.setExclusive(True)



    def combobox_func(self):
        self.pushButton_1.clicked.connect(lambda: self.updete_warrior_combobox())
        self.pushButton_2.clicked.connect(lambda: self.update_combobox())
        self.pushButton_3.clicked.connect(lambda: self.update_combobox())
        self.pushButton_4.clicked.connect(lambda: self.update_combobox())


    def on_radio_selected(self, id):
        self.selected_radio = id
        # Если выбрана персональная кнопка, сбрасываем остальные
        if id == 8:
            for i in range(1, 8):
                btn = self.group1.button(i)
                if btn:
                    btn.setChecked(False)
            self.Personal_Prise_materials_radioButton.setChecked(True)
        else:
            self.Personal_Prise_materials_radioButton.setChecked(False)
        # Можно добавить print или обновление UI
        # print(f"Selected radio: {self.selected_radio}")

    def updete_warrior_combobox(self):
        items = self.items["Plate_Equipment"]["Plate"]
        self.comboBox_class.clear()
        self.comboBox_2.clear()
        self.comboBox_class.addItems(items)

        for category_dict in items.values():  # перебираем "Helmets", "Armors", "Boots"
            for item_name in category_dict.keys():  # перебираем "Soldier Helmet", "Knight Helmet" и т.п.
                self.comboBox_2.addItem(item_name)



    def resizeEvent(self, event):
        super().resizeEvent(event)

        new_width = self.width()
        new_height = self.height()

        self.window.setFixedSize(new_width, new_height)



if __name__ == "__main__":
    app = QApplication([])
    window = Craft_window()
    window.show()
    app.exec_()