from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QButtonGroup
from PyQt5.uic import loadUi

import json
import os

class Craft_window(QWidget):
    def __init__(self, main_window=None, db= None, url_generator=None):
        super().__init__()
        loadUi("Api\Tabs\Craft\craft.ui", self)
        self.main_window = main_window

        self.button_func()
        self.combobox_func()


        # Поля для хранения данных

        self.sett_T4 = False
        self.sett_T5 = False
        self.sett_T6 = False
        self.sett_T7 = False
        self.sett_T8 = False

        self.sett_Charr = 0

        self.sett_quantity = 2


        self.city_to_sell = None

        self.expected_profit_text = 0
        self.prise_materials_text = 0
        self.count_journals = 0
        self.tax_text = 0

        self.use_focus = False
        self.use_journals = False

        self.count_resources_1 = 0
        self.count_resources_2 = 0

        self.return_resources_percent = 15
        self.fee_for_100_nutrition = 500
        self.count_items_craft = 1



        self.items = {}
        self.folder_path = "item_info"
        self.load_items()

        


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

        group1.buttonClicked[int].connect(self._on_radio_selected)


        group2 = QButtonGroup(self)
        group2.addButton(self.radioButton_char_0, 1)
        group2.addButton(self.radioButton_char_1, 2)
        group2.addButton(self.radioButton_char_2, 3)
        group2.addButton(self.radioButton_char_3, 4)
        group2.addButton(self.radioButton_char_4, 5)
        group1.setExclusive(True)
        self.group2 = group2
        group2.buttonClicked[int].connect(self._on_char_radio_selected)  

        group3 = QButtonGroup(self)
        group3.addButton(self.radioButton_quantity_1, 1)
        group3.addButton(self.radioButton_quantity_2, 2)
        group3.addButton(self.radioButton_quantity_3, 3)
        group3.addButton(self.radioButton_quantity_4, 4)
        group3.addButton(self.radioButton_quantity_5, 5)
        self.group3 = group3
        group3.buttonClicked[int].connect(self._on_quantity_radio_selected)


    def combobox_func(self):
        self.pushButton_1.clicked.connect(lambda: self._updete_warrior_combobox())
        self.pushButton_2.clicked.connect(lambda: self._update_combobox())
        self.pushButton_3.clicked.connect(lambda: self._update_combobox())
        self.pushButton_4.clicked.connect(lambda: self._update_combobox())

        self.comboBox_3.currentIndexChanged.connect(lambda: self._update_combobox_city('city_to_sell', self.comboBox_3.currentText()))
        self.checkBox.stateChanged.connect(lambda state: self._update_combobox('use_focus', state))
        self.checkBox_2.stateChanged.connect(lambda state: self._update_combobox('use_journals', state))

        self.return_percent_doubleSpinBox.valueChanged.connect(self._make_setter('return_resources_percent'))

        self.T4_checkBox.stateChanged.connect(lambda state: self._update_combobox('sett_T4', state))
        self.T5_checkBox.stateChanged.connect(lambda state: self._update_combobox('sett_T5', state))
        self.T6_checkBox.stateChanged.connect(lambda state: self._update_combobox('sett_T6', state))
        self.T7_checkBox.stateChanged.connect(lambda state: self._update_combobox('sett_T7', state))
        self.T8_checkBox.stateChanged.connect(lambda state: self._update_combobox('sett_T8', state))

        self.charr_setter()

        self.pushButton_calculate.clicked.connect(self.get_recult)




    def charr_setter(self):
        for butt in self.group2.buttons():  # Исправлено на group2
            if butt.isChecked():
                self.sett_Charr = int(butt.text())
                print(f"Selected char: {self.sett_Charr}")
                break
        else:
            self.sett_Charr = 0

    def _on_char_radio_selected(self, id):
        self.sett_Charr = id - 1
        print(f"Selected char: {self.sett_Charr}")

    def _on_quantity_radio_selected(self, id):
        self.sett_quantity = id
        print(f"Selected quantity: {self.sett_quantity}")







    def get_recult(self):
        print({"Tier":{
            "T4": self.sett_T4,
            "T5": self.sett_T5,
            "T6": self.sett_T6,
            "T7": self.sett_T7,
            "T8": self.sett_T8
        },
        "Char": self.sett_Charr,
        "Quantity": self.sett_quantity
        })




# Buttons methods -------------------------------------------------

    def _on_radio_selected(self, id):
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

    def _updete_warrior_combobox(self):
        items = self.items["Plate_Equipment"]["Plate"]
        self.comboBox_class.clear()
        self.comboBox_2.clear()
        self.comboBox_class.addItems(items)

        for category_dict in items.values():  
            for item_name in category_dict.keys():  
                self.comboBox_2.addItem(item_name)

    def _update_combobox(self, field_name, state):
        setattr(self, field_name, state == 2)
       
    def _update_combobox_city(self, box, value):
        setattr(self, box, value)

    def _make_setter(self, attr_name, obj=None):
        if obj is None:
            obj = self
        return lambda value: setattr(obj, attr_name, value)

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