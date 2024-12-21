import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import QStringListModel

from Api.windows.parsed_items_price.dialogwind import InfoDialogWindow as info_dialog



class Ui_Parcer(QtWidgets.QMainWindow):

    def __init__(self, parent=None, file_manager=None):
        super(Ui_Parcer, self).__init__(parent)
        self.setupUi()

        self.file_manager = file_manager


        self.language = self.file_manager.settings.get("language", "English")


        self.selected_item = None
        self.files = None


        # Load settings
        self.items_data = self.file_manager.items_info
        self.settings = QtCore.QSettings("Parser", "info_dialog")
        self._load_window_settings()


        # ComboBox logic
        self.populate_classItem_comboBox()
        self.classItem_comboBox.currentIndexChanged.connect(self.update_item_combobox)


        # Sliders logic
        self.verticalSlider_day.valueChanged.connect(lambda: self.update_slider_value(self.verticalSlider_day, self.sl1_value_label))
        self.verticalSlider_hour.valueChanged.connect(lambda: self.update_slider_value(self.verticalSlider_hour, self.sl2_value_label))


        # Buttons logic 
        self.append_pushButton.clicked.connect(self.append_item_configuration_to_list)
        self.infoItem_pushButton.clicked.connect(self.open_dialog)
        self.deleteItem_pushButton.clicked.connect(self.delete_item_from_list)


        # ListView logic
        self.list_widget_items.clicked.connect(self.handle_list_item_clicked)
        self.update_list_view()

        # Value_limitation
        self.tier_start_comboBox.currentIndexChanged.connect(self.value_limitation_combobox_tier)
        self.tier_end_comboBox.currentIndexChanged.connect(self.value_limitation_combobox_tier)
        self.enchant_start_comboBox.currentIndexChanged.connect(self.value_limitation_combobox_enchant)
        self.enchant_end_comboBox.currentIndexChanged.connect(self.value_limitation_combobox_enchant)



    # Statics logic
    def setupUi(self):
        self.setObjectName("Parcer")
        self.resize(500, 250)
        self.setStyleSheet("background-color: rgb(195, 195, 195);")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.main_horizontalFrame = QtWidgets.QFrame(self.centralwidget)
        self.main_horizontalFrame.setGeometry(QtCore.QRect(10, 10, 480, 230))
        self.main_horizontalFrame.setObjectName("main_horizontalFrame")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.main_horizontalFrame)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.all_settings_horizontalFrame = QtWidgets.QFrame(self.main_horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.all_settings_horizontalFrame.sizePolicy().hasHeightForWidth())
        self.all_settings_horizontalFrame.setSizePolicy(sizePolicy)
        self.all_settings_horizontalFrame.setObjectName("all_settings_horizontalFrame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.all_settings_horizontalFrame)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalFrame_4 = QtWidgets.QFrame(self.all_settings_horizontalFrame)
        self.verticalFrame_4.setMaximumSize(QtCore.QSize(16777215, 16777208))
        self.verticalFrame_4.setObjectName("verticalFrame_4")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.verticalFrame_4)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.items_changer_verticalFrame = QtWidgets.QFrame(self.verticalFrame_4)
        self.items_changer_verticalFrame.setObjectName("items_changer_verticalFrame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.items_changer_verticalFrame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.classItem_comboBox = QtWidgets.QComboBox(self.items_changer_verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.classItem_comboBox.sizePolicy().hasHeightForWidth())
        self.classItem_comboBox.setSizePolicy(sizePolicy)
        self.classItem_comboBox.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.classItem_comboBox.setFont(font)
        self.classItem_comboBox.setObjectName("classItem_comboBox")
        self.classItem_comboBox.addItem("--------")
        self.verticalLayout.addWidget(self.classItem_comboBox)
        self.itemName_comboBox = QtWidgets.QComboBox(self.items_changer_verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.itemName_comboBox.sizePolicy().hasHeightForWidth())
        self.itemName_comboBox.setSizePolicy(sizePolicy)
        self.itemName_comboBox.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.itemName_comboBox.setFont(font)
        self.itemName_comboBox.setObjectName("itemName_comboBox")
        self.itemName_comboBox.addItem("--------")
        self.verticalLayout.addWidget(self.itemName_comboBox)
        self.verticalLayout_6.addWidget(self.items_changer_verticalFrame)
        self.settings_horizontalFrame = QtWidgets.QFrame(self.verticalFrame_4)
        self.settings_horizontalFrame.setObjectName("settings_horizontalFrame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.settings_horizontalFrame)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tier_verticalFrame = QtWidgets.QFrame(self.settings_horizontalFrame)
        self.tier_verticalFrame.setObjectName("tier_verticalFrame")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tier_verticalFrame)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tier_label = QtWidgets.QLabel(self.tier_verticalFrame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.tier_label.setFont(font)
        self.tier_label.setAlignment(QtCore.Qt.AlignCenter)
        self.tier_label.setObjectName("tier_label")
        self.verticalLayout_4.addWidget(self.tier_label)
        self.tier_start_comboBox = QtWidgets.QComboBox(self.tier_verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tier_start_comboBox.sizePolicy().hasHeightForWidth())
        self.tier_start_comboBox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.tier_start_comboBox.setFont(font)
        self.tier_start_comboBox.setObjectName("tier_start_comboBox")
        self.tier_start_comboBox.addItem("")
        self.tier_start_comboBox.addItem("")
        self.tier_start_comboBox.addItem("")
        self.tier_start_comboBox.addItem("")
        self.tier_start_comboBox.addItem("")
        self.verticalLayout_4.addWidget(self.tier_start_comboBox, 0, QtCore.Qt.AlignHCenter)
        self.tier_end_comboBox = QtWidgets.QComboBox(self.tier_verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tier_end_comboBox.sizePolicy().hasHeightForWidth())
        self.tier_end_comboBox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.tier_end_comboBox.setFont(font)
        self.tier_end_comboBox.setObjectName("tier_end_comboBox")
        self.tier_end_comboBox.addItem("")
        self.tier_end_comboBox.addItem("")
        self.tier_end_comboBox.addItem("")
        self.tier_end_comboBox.addItem("")
        self.tier_end_comboBox.addItem("")
        self.verticalLayout_4.addWidget(self.tier_end_comboBox, 0, QtCore.Qt.AlignHCenter)
        self.horizontalLayout_3.addWidget(self.tier_verticalFrame)
        self.Enchant_verticalFrame = QtWidgets.QFrame(self.settings_horizontalFrame)
        self.Enchant_verticalFrame.setObjectName("Enchant_verticalFrame")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.Enchant_verticalFrame)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.Enchant_label = QtWidgets.QLabel(self.Enchant_verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Enchant_label.sizePolicy().hasHeightForWidth())
        self.Enchant_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Enchant_label.setFont(font)
        self.Enchant_label.setAlignment(QtCore.Qt.AlignCenter)
        self.Enchant_label.setObjectName("Enchant_label")
        self.verticalLayout_5.addWidget(self.Enchant_label)
        self.enchant_start_comboBox = QtWidgets.QComboBox(self.Enchant_verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.enchant_start_comboBox.sizePolicy().hasHeightForWidth())
        self.enchant_start_comboBox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.enchant_start_comboBox.setFont(font)
        self.enchant_start_comboBox.setObjectName("Enchant_start_comboBox")
        self.enchant_start_comboBox.addItem("")
        self.enchant_start_comboBox.addItem("")
        self.enchant_start_comboBox.addItem("")
        self.enchant_start_comboBox.addItem("")
        self.enchant_start_comboBox.addItem("")
        self.verticalLayout_5.addWidget(self.enchant_start_comboBox, 0, QtCore.Qt.AlignHCenter)
        self.enchant_end_comboBox = QtWidgets.QComboBox(self.Enchant_verticalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.enchant_end_comboBox.sizePolicy().hasHeightForWidth())
        self.enchant_end_comboBox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.enchant_end_comboBox.setFont(font)
        self.enchant_end_comboBox.setObjectName("Enchant_end_comboBox")
        self.enchant_end_comboBox.addItem("")
        self.enchant_end_comboBox.addItem("")
        self.enchant_end_comboBox.addItem("")
        self.enchant_end_comboBox.addItem("")
        self.enchant_end_comboBox.addItem("")
        self.verticalLayout_5.addWidget(self.enchant_end_comboBox, 0, QtCore.Qt.AlignHCenter)
        self.horizontalLayout_3.addWidget(self.Enchant_verticalFrame)
        self.slider_horizontalFrame = QtWidgets.QFrame(self.settings_horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slider_horizontalFrame.sizePolicy().hasHeightForWidth())
        self.slider_horizontalFrame.setSizePolicy(sizePolicy)
        self.slider_horizontalFrame.setObjectName("slider_horizontalFrame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.slider_horizontalFrame)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.slider1_horizontalFrame = QtWidgets.QFrame(self.slider_horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slider1_horizontalFrame.sizePolicy().hasHeightForWidth())
        self.slider1_horizontalFrame.setSizePolicy(sizePolicy)
        self.slider1_horizontalFrame.setMinimumSize(QtCore.QSize(0, 0))
        self.slider1_horizontalFrame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.slider1_horizontalFrame.setObjectName("slider1_horizontalFrame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.slider1_horizontalFrame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.sl1_mane_label = QtWidgets.QLabel(self.slider1_horizontalFrame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.sl1_mane_label.setFont(font)
        self.sl1_mane_label.setObjectName("sl1_mane_label")
        self.verticalLayout_2.addWidget(self.sl1_mane_label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.verticalSlider_day = QtWidgets.QSlider(self.slider1_horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalSlider_day.sizePolicy().hasHeightForWidth())
        self.verticalSlider_day.setSizePolicy(sizePolicy)
        self.verticalSlider_day.setMinimumSize(QtCore.QSize(10, 30))
        self.verticalSlider_day.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalSlider_day.setMinimum(3)
        self.verticalSlider_day.setMaximum(15)
        self.verticalSlider_day.setProperty("value", 7)
        self.verticalSlider_day.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_day.setObjectName("verticalSlider_day")
        self.verticalLayout_2.addWidget(self.verticalSlider_day, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.sl1_value_label = QtWidgets.QLabel(self.slider1_horizontalFrame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.sl1_value_label.setFont(font)
        self.sl1_value_label.setObjectName("sl1_value_label")
        self.verticalLayout_2.addWidget(self.sl1_value_label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.horizontalLayout_2.addWidget(self.slider1_horizontalFrame)
        self.slider2_horizontalFrame = QtWidgets.QFrame(self.slider_horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slider2_horizontalFrame.sizePolicy().hasHeightForWidth())
        self.slider2_horizontalFrame.setSizePolicy(sizePolicy)
        self.slider2_horizontalFrame.setMinimumSize(QtCore.QSize(0, 0))
        self.slider2_horizontalFrame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.slider2_horizontalFrame.setObjectName("slider2_horizontalFrame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.slider2_horizontalFrame)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(5)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.sl2_name_label = QtWidgets.QLabel(self.slider2_horizontalFrame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.sl2_name_label.setFont(font)
        self.sl2_name_label.setObjectName("sl2_name_label")
        self.verticalLayout_3.addWidget(self.sl2_name_label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.verticalSlider_hour = QtWidgets.QSlider(self.slider2_horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalSlider_hour.sizePolicy().hasHeightForWidth())
        self.verticalSlider_hour.setSizePolicy(sizePolicy)
        self.verticalSlider_hour.setMinimumSize(QtCore.QSize(10, 30))
        self.verticalSlider_hour.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalSlider_hour.setMinimum(1)
        self.verticalSlider_hour.setMaximum(6)
        self.verticalSlider_hour.setProperty("value", 1)
        self.verticalSlider_hour.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_hour.setObjectName("verticalSlider_hour")
        self.verticalLayout_3.addWidget(self.verticalSlider_hour, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.sl2_value_label = QtWidgets.QLabel(self.slider2_horizontalFrame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.sl2_value_label.setFont(font)
        self.sl2_value_label.setObjectName("sl2_value_label")
        self.verticalLayout_3.addWidget(self.sl2_value_label, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.horizontalLayout_2.addWidget(self.slider2_horizontalFrame)
        self.horizontalLayout_3.addWidget(self.slider_horizontalFrame)
        self.verticalLayout_6.addWidget(self.settings_horizontalFrame)
        self.horizontalLayout_4.addWidget(self.verticalFrame_4)
        self.horizontalLayout_5.addWidget(self.all_settings_horizontalFrame)
        self.list_widget_verticalFrame = QtWidgets.QFrame(self.main_horizontalFrame)
        self.list_widget_verticalFrame.setObjectName("list_widget_verticalFrame")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.list_widget_verticalFrame)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setSpacing(2)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.list_widget_items = QtWidgets.QListView(self.list_widget_verticalFrame)
        self.list_widget_items.setObjectName("list_widget_items")
        self.verticalLayout_8.addWidget(self.list_widget_items)
        self.model = QStringListModel()
        self.list_widget_items.setEditTriggers(QtWidgets.QListView.NoEditTriggers)
        self.list_widget_items.setModel(self.model)
        self.horizontalFrame = QtWidgets.QFrame(self.list_widget_verticalFrame)
        self.horizontalFrame.setObjectName("horizontalFrame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalFrame)
        self.horizontalLayout.setContentsMargins(5, 2, 5, 2)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.append_pushButton = QtWidgets.QPushButton(self.horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.append_pushButton.sizePolicy().hasHeightForWidth())
        self.append_pushButton.setSizePolicy(sizePolicy)
        self.append_pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.append_pushButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.append_pushButton.setFont(font)
        self.append_pushButton.setObjectName("infoItem_pushButton_2")
        self.horizontalLayout.addWidget(self.append_pushButton)
        self.infoItem_pushButton = QtWidgets.QPushButton(self.horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.infoItem_pushButton.sizePolicy().hasHeightForWidth())
        self.infoItem_pushButton.setSizePolicy(sizePolicy)
        self.infoItem_pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.infoItem_pushButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.infoItem_pushButton.setFont(font)
        self.infoItem_pushButton.setObjectName("infoItem_pushButton")
        self.horizontalLayout.addWidget(self.infoItem_pushButton)
        self.deleteItem_pushButton = QtWidgets.QPushButton(self.horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deleteItem_pushButton.sizePolicy().hasHeightForWidth())
        self.deleteItem_pushButton.setSizePolicy(sizePolicy)
        self.deleteItem_pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.deleteItem_pushButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.deleteItem_pushButton.setFont(font)
        self.deleteItem_pushButton.setObjectName("deleteItem_pushButton")
        self.horizontalLayout.addWidget(self.deleteItem_pushButton)
        self.verticalLayout_8.addWidget(self.horizontalFrame)
        self.horizontalLayout_5.addWidget(self.list_widget_verticalFrame)
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, Parcer):
        _translate = QtCore.QCoreApplication.translate
        Parcer.setWindowTitle(_translate("Parcer", "MainWindow"))
        self.tier_label.setText(_translate("Parcer", "Tier"))
        self.tier_start_comboBox.setItemText(0, _translate("Parcer", "4"))
        self.tier_start_comboBox.setItemText(1, _translate("Parcer", "5"))
        self.tier_start_comboBox.setItemText(2, _translate("Parcer", "6"))
        self.tier_start_comboBox.setItemText(3, _translate("Parcer", "7"))
        self.tier_start_comboBox.setItemText(4, _translate("Parcer", "8"))
        self.tier_end_comboBox.setItemText(0, _translate("Parcer", "4"))
        self.tier_end_comboBox.setItemText(1, _translate("Parcer", "5"))
        self.tier_end_comboBox.setItemText(2, _translate("Parcer", "6"))
        self.tier_end_comboBox.setItemText(3, _translate("Parcer", "7"))
        self.tier_end_comboBox.setItemText(4, _translate("Parcer", "8"))
        self.Enchant_label.setText(_translate("Parcer", "Enchant"))
        self.enchant_start_comboBox.setItemText(0, _translate("Parcer", "0"))
        self.enchant_start_comboBox.setItemText(1, _translate("Parcer", "1"))
        self.enchant_start_comboBox.setItemText(2, _translate("Parcer", "2"))
        self.enchant_start_comboBox.setItemText(3, _translate("Parcer", "3"))
        self.enchant_start_comboBox.setItemText(4, _translate("Parcer", "4"))
        self.enchant_end_comboBox.setItemText(0, _translate("Parcer", "0"))
        self.enchant_end_comboBox.setItemText(1, _translate("Parcer", "1"))
        self.enchant_end_comboBox.setItemText(2, _translate("Parcer", "2"))
        self.enchant_end_comboBox.setItemText(3, _translate("Parcer", "3"))
        self.enchant_end_comboBox.setItemText(4, _translate("Parcer", "4"))
        self.sl1_mane_label.setText(_translate("Parcer", "Days"))
        self.sl1_value_label.setText(_translate("Parcer", "7"))
        self.sl2_name_label.setText(_translate("Parcer", "Step-H"))
        self.sl2_value_label.setText(_translate("Parcer", "0.5"))
        self.append_pushButton.setText(_translate("Parcer", "Append"))
        self.infoItem_pushButton.setText(_translate("Parcer", "Info"))
        self.deleteItem_pushButton.setText(_translate("Parcer", "Delete"))

# ----------------------------------------------------------------
# Window methods for controlling the state of the application window

    def resizeEvent(self, event):
        super(Ui_Parcer, self).resizeEvent(event)
        self._center_frame()
        self._scaling_frame()

    def _center_frame(self):
        frame_width = self.main_horizontalFrame.width()
        frame_height = self.main_horizontalFrame.height()
        central_widg_width = self.centralwidget.width()
        central_widg_height = self.centralwidget.height()

        x = (central_widg_width - frame_width) // 2
        y = (central_widg_height - frame_height) // 2

        self.main_horizontalFrame.move(x, y)

    def _scaling_frame(self):
        
        self.main_horizontalFrame.setGeometry(0,0, self.centralwidget.width() + 0, self.centralwidget.height() + 0)

    def _load_window_settings(self):
        width = self.settings.value("mainWidth", 500, type=int)
        height = self.settings.value("mainHeight", 250, type=int)
        self.resize(width, height)

        position = self.settings.value("mainPosition", QtCore.QPoint(600, 300), type=QtCore.QPoint)
        self.move(position)

    def closeEvent(self, event):
        self.settings.setValue("mainWidth", self.width())
        self.settings.setValue("mainHeight", self.height())
        self.settings.setValue("mainPosition", self.pos())  
        super(Ui_Parcer, self).closeEvent(event)


# ----------------------------------------------------------------
# ComboBox logic

    def populate_classItem_comboBox(self):

        if self.items_data:
            categories = self.items_data.keys() 
            self.classItem_comboBox.addItems(categories)
        else:
            print("Не удалось загрузить данные для интерфейса")

    def update_item_combobox(self):
        """Обновляет содержимое item_comboBox в зависимости от выбранной категории в classItem_comboBox и текущего языка."""
        
        selected_category = self.classItem_comboBox.currentText()

        if self.items_data:
            # Очищаем item_comboBox перед добавлением новых элементов
            self.itemName_comboBox.clear()

            # Получаем данные для выбранной категории
            items_for_category = self.items_data.get(selected_category, {})

            if items_for_category:
                # Выбираем язык для отображения
                item_names = [item_data.get(self.language, "") for item_data in items_for_category.values()]

                # Добавляем элементы в item_comboBox
                self.itemName_comboBox.addItems(item_names)
            else:
                print(f"Категория {selected_category} не содержит предметов.")
        else:
            print("Не удалось загрузить данные для интерфейса.")

    def value_limitation_combobox_tier(self):
        if self.tier_start_comboBox.currentText() > self.tier_end_comboBox.currentText():
            self.tier_start_comboBox.setCurrentIndex(self.tier_end_comboBox.currentIndex())

        elif self.tier_end_comboBox.currentText() < self.tier_start_comboBox.currentText():
            self.tier_start_comboBox.setCurrentIndex(self.tier_end_comboBox.currentIndex())

    def value_limitation_combobox_enchant(self):
        if self.enchant_start_comboBox.currentText() > self.enchant_end_comboBox.currentText():
            self.enchant_start_comboBox.setCurrentIndex(self.enchant_end_comboBox.currentIndex())

        elif self.enchant_end_comboBox.currentText() < self.enchant_start_comboBox.currentText():
            self.enchant_start_comboBox.setCurrentIndex(self.enchant_end_comboBox.currentIndex())

 
# ----------------------------------------------------------------
# Slider logic

    def update_slider_value(self, slider, label):
        """
        Universal method to update slider value and label
        :param slider: the slider to retrieve the value from
        :param label: the label to display the slider's value
        """
        slider_value = slider.value()  # Get the current value of the slider

        if slider == self.verticalSlider_hour: slider_value /= 2 # corrected value for second hour slider

        label.setText(str(slider_value))  # Update the label with the slider value


# ----------------------------------------------------------------
# Getting items configuration and return list of parameters for function -self.save_items_to_json-

    def append_item_configuration_to_list(self):

        def _get_data():
            """
            Method to append item configuration to the list
            :return: item configuration dictionary
            """
            return {
                "class": self.classItem_comboBox.currentText(),
                "item": self.itemName_comboBox.currentText(),

                "tier_min": self.tier_start_comboBox.currentText(),
                "tier_max": self.tier_end_comboBox.currentText(),
                "enchant_min": self.enchant_start_comboBox.currentText(),
                "enchant_max": self.enchant_end_comboBox.currentText(),

                "days": self.sl1_value_label.text(),
                "step_h": self.sl2_value_label.text()
            }
        # Добавляем данные в файл
        
        self.save_items_to_json(new_item=_get_data())


# ----------------------------------------------------------------
# Appdating data in listView

    def save_items_to_json(self, new_item):
        """
        Saving data in actual json list 
        
        """

        item_found = False

        for item in self.file_manager.parsing_list_dict:
            # Проверка на совпадение по имени предмета
            if item["item"] == new_item["item"]:
                # Обновляем данные, если они отличаются
                if (item["tier_min"] != new_item["tier_min"] or
                    item["tier_max"] != new_item["tier_max"] or
                    item["enchant_min"] != new_item["enchant_min"] or
                    item["enchant_max"] != new_item["enchant_max"] or
                    item["days"] != new_item["days"] or
                    item["step_h"] != new_item["step_h"]):
                    
                    item["tier_min"] = new_item["tier_min"]
                    item["tier_max"] = new_item["tier_max"]
                    item["enchant_min"] = new_item["enchant_min"]
                    item["enchant_max"] = new_item["enchant_max"]
                    item["days"] = new_item["days"]
                    item["step_h"] = new_item["step_h"]
                    print("Данные обновлены.")
                else:
                    print("Предмет с такими же данными уже существует. Обновление не требуется.")
                
                item_found = True
                break

        # Append the item to the list for saving
        if not item_found:
            self.file_manager.parsing_list_dict.append(new_item)
            print("Новый предмет добавлен.")

        # Save the new item
        self.file_manager.save_json(data=self.file_manager.parsing_list_dict, path=self.file_manager.file_path_file["actual_parsing_file_path"])


        # Обновляем QListView после добавления/обновления предмета
        self.update_list_view()

    def update_list_view(self):
        
        all_data = self.file_manager.parsing_list_dict

        # Преобразуем данные в список строк, содержащих только значение "item"
        item_strings = [item['item'] for item in all_data if 'item' in item]

        # Обновляем модель данных QListView
        self.model.setStringList(item_strings)
            
    def handle_list_item_clicked(self, index: QtCore.QModelIndex):
        # Обрабатываем выбор элемента
        self.selected_item = self.model.data(index, 0)  # Получаем текст элемента


# ----------------------------------------------------------------
# Info for qdialog window

    def get_info_item(self, name):

        for item in self.file_manager.parsing_list_dict:
            if item["item"] == name:
                return item

    def open_dialog(self):

        qDialog_window = info_dialog(self.get_info_item(self.selected_item))
        qDialog_window.exec_()

    
# ----------------------------------------------------------------
# Delete item from parsed list

    def delete_item_from_list(self):

        for item in self.file_manager.parsing_list_dict:
            if item["item"] == self.selected_item:
                
                self.file_manager.parsing_list_dict.remove(item)
                break  

        self.file_manager.save_json(
            data=self.file_manager.parsing_list_dict, 
            path=self.file_manager.file_path_file["actual_parsing_file_path"]
        )

        # Обновляем QListView после добавления/обновления предмета
        self.update_list_view()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = Ui_Parcer()
    main_window.show()
    sys.exit(app.exec_())


