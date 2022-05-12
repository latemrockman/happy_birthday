import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
    QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp
from main_form import *
from add_form import *
import json
import datetime
import os.path

def loading_dict():
    with open(data_path, "r") as file:
        dict_config = json.load(file)
        dict_birthday = dict_config["base"]

        return dict_birthday

def loading_dict_settings():
    with open(data_path, "r") as file:
        dict_config = json.load(file)
        dict_settings = dict_config["settings"]

        return dict_settings

def save_dict(dict):
    with open(data_path, "w") as file:
       json.dump(dict, file, indent=2)

def update_dict(dict):
    save_dict(dict)
    loading_dict()

def print_dict(dict):
    for name, data in dict.items():
        print(data, name)
    print('')

update = False

data_path = "user.json"

dict_birthday = {}
dict_settings = {
    "check_tray": False,
    "remind": 0,
    "position_w": 10,
    "position_h": 10,
    "height": 500
}
dict_config = {"base": dict_birthday, "settings": dict_settings}

if os.path.exists(data_path):
    dict_birthday = loading_dict()
    dict_settings = loading_dict_settings()
    print_dict(dict_birthday)
    print_dict(dict_settings)
else:
    update_dict(dict_config)

tray = dict_settings["check_tray"]

class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

class GUI(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)
        #QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #self.ui.comboRemind.hide()
        #self.ui.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.ui.tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.setCurrentData()
        self.setSettings()

        #self.ui.tableWidget.cellClicked.connect(self.clickTable)
        self.ui.tableWidget.cellChanged.connect(self.changeTable)
        self.ui.tableWidget.cellClicked.connect(self.selectRow)
        self.ui.tableWidget.cellDoubleClicked.connect(self.clickTable)

        self.changeCell = ""
        self.changedCell = ""

        self.ui.btn_addPerson.clicked.connect(self.open_add_window)
        self.ui.btn_delPerson.clicked.connect(self.del_person)
        #self.ui.pushButton.clicked.connect(self.table_to_dict)
        #self.ui.btn_remind.clicked.connect(self.print_remind_list)
        #self.ui.btnColor.clicked.connect(self.setColors)

        self.ui.checkTray.stateChanged.connect(self.change_checkTray)
        self.ui.comboRemind.currentIndexChanged.connect(self.change_comboRemind)

        # Инициализируем QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        show_action = QAction("Открыть программу", self)
        quit_action = QAction("Выход", self)
        #hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        #hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        #tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.monitoring_data)
        self.monitoring_interval = 1
        self.timer.start(self.monitoring_interval * 1000)

        self.start_programm()
        self.time_check = []

    def start_programm(self):
        if tray:
            self.print_remind_list()

    def closeEvent(self, event):
        self.fillTable()
        if self.ui.checkTray.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage("Дни Рождения", "Программа работает в фоновом режиме",
                QSystemTrayIcon.Information, 2000)

    def scroll_to_today(self):
        def today_row():
            all_rows = []
            for row in range(0, max_row):
                day_to = self.ui.tableWidget.item(row, 3).text()
                if day_to.isdigit():
                    day_to = int(day_to)
                else:
                    day_to = 0
                all_rows.append(day_to)

            result = all_rows.index(min(all_rows))
            return result

        max_row = self.ui.tableWidget.rowCount()
        if max_row <= 1:
            return

        today_row = today_row()

        self.ui.tableWidget.scrollToBottom()
        self.ui.tableWidget.selectRow(today_row)
        self.ui.tableWidget.clearSelection()

    def check_time_remind(self):
        self.time_check.append(datetime.datetime.today())

        if len(self.time_check) < 2:
            return

        last = self.time_check[-1]
        pre_last = self.time_check[-2]

        delta = last.minute - pre_last.minute

        if delta > 5:
            self.print_remind_list()

        print(self.time_check)
        print(delta)

        del self.time_check[0]

    def monitoring_data(self):
        if self.ui.checkTray.isChecked() == False:
            print('не напоминать')
            return


        if self.ui.comboRemind.currentIndex() == 1:
            print("1й режим напоминания")
            self.check_time_remind()


        today = datetime.date.today().strftime("%d.%m.%Y")
        today_actual = self.ui.label.text()[8:]

        if today != today_actual:
            self.setCurrentData()
            self.fillTable()
            self.print_remind_list()

        global update
        if update:
            self.fillTable()
            update = False

    def scroll_to_row(self):
        self.ui.tableWidget.selectRow(6)

    def selectRow(self, row, column):
        self.ui.tableWidget.selectRow(row)

    def setSettings(self):
        check_tray = dict_settings["check_tray"]
        remind = dict_settings["remind"]
        position_w = dict_settings["position_w"]
        position_h = dict_settings["position_h"]
        height = dict_settings["height"]

        self.ui.checkTray.setChecked(check_tray)
        self.ui.comboRemind.setCurrentIndex(remind)
        self.move(position_w, position_h)
        self.resize(self.width(),height)

    def change_checkTray(self):
        self.fillTable()

    def change_comboRemind(self):
        self.fillTable()

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        self.fillTable()
        self.scroll_to_today()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.packingDict()

    def moveEvent(self, a0: QtGui.QMoveEvent) -> None:
        self.packingDict()

    def packingDict(self):
        dict_settings["check_tray"] = self.ui.checkTray.isChecked()
        dict_settings["remind"] = self.ui.comboRemind.currentIndex()
        dict_settings["position_w"] = self.x()
        dict_settings["position_h"] = self.y()
        dict_settings["height"] = self.height()

        dict_config["base"] = dict_birthday
        dict_config["settings"] = dict_settings

    def fillTable(self):
        self.packingDict()

        update_dict(dict_config)
        self.clearTableWidget()

        # определение переменных
        for name in self.sort_dict():
            data = dict_birthday[name]

            countRow = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(countRow)
            #self.item = QTableWidgetItem(scraped_age).setTextAlignment(Qt.AlignHCenter)


            hb_data = data[0]
            hb_data = hb_data.split("-")
            hb_data.reverse()
            hb_data[0] = f"{hb_data[0]:0>2}"
            hb_data[1] = f"{hb_data[1]:0>2}"
            hb_data = ".".join(hb_data)

            delictDay = self.declinationDay(data[1])

            #заполнение таблицы

            self.ui.tableWidget.setItem(countRow, 0, QtWidgets.QTableWidgetItem(hb_data))
            self.ui.tableWidget.setItem(countRow, 1, QtWidgets.QTableWidgetItem(name))
            self.ui.tableWidget.setItem(countRow, 4, QtWidgets.QTableWidgetItem(f"За {str(data[1])} {delictDay}"))

            toAge = self.countAge(data[0])
            self.ui.tableWidget.setItem(countRow, 2, QtWidgets.QTableWidgetItem(toAge))

            toDay = self.countIntervalDay(data[0])
            if toDay == 0:
                toDay = "Сегодня Д.Р.!!!"
            else:
                toDay = str(toDay)

            self.ui.tableWidget.setItem(countRow, 3, QtWidgets.QTableWidgetItem(toDay))

            delegate = AlignDelegate(self.ui.tableWidget)
            self.ui.tableWidget.setItemDelegateForColumn(0,delegate)
            self.ui.tableWidget.setItemDelegateForColumn(1, delegate)
            self.ui.tableWidget.setItemDelegateForColumn(2, delegate)
            self.ui.tableWidget.setItemDelegateForColumn(3, delegate)
            self.ui.tableWidget.setItemDelegateForColumn(4, delegate)

            self.setupSize()
            self.setColors()

    def setColors(self):
        def setColorRow(row, color):
            columnCount = int(self.ui.tableWidget.columnCount())

            for column in range(0,columnCount):
                self.ui.tableWidget.item(row, column).setBackground(color)

        color_hb = QtGui.QColor(255, 205, 210)
        color_soon = QtGui.QColor(197, 202, 233)
        color_white = QtGui.QColor(255, 255, 255)

        countRow = int(self.ui.tableWidget.rowCount())


        for row in range(0, countRow):
            hb_day = self.ui.tableWidget.item(row, 3).text()                        # содержание  ячейки ЧЕРЕЗ СКОЛЬКО ДНЕЙ ДР str
            remind = int(self.ui.tableWidget.item(row, 4).text().split()[1])        # за сколько дней напоминать int

            if hb_day.isdigit():
                hb_day = int(hb_day)
                if hb_day <= remind:
                    setColorRow(row, color_soon)
                else:
                    setColorRow(row, color_white)
            else:
                setColorRow(row, color_hb)

    def checkCorrectCell(self, value, correct_value, row, column):
        def checkData(data):
            try:
                data_obj = datetime.datetime.strptime(data, "%d.%m.%Y")

                list_value = value.split(".")
                value_day = list_value[0]
                value_month = list_value[1]

                if len(value_day) == 1 or len(value_month) == 1:
                    format_data = f"{data_obj.day:0>2}.{data_obj.month:0>2}.{data_obj.year}"
                    self.ui.tableWidget.setItem(row, column, QtWidgets.QTableWidgetItem(format_data))

                list_value.reverse()
                age = self.countAge("-".join(list_value))
                count_day = self.countIntervalDay("-".join(list_value))

                if count_day == 0:
                    count_day = "Сегодня Д.Р.!!!"

                self.ui.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(age))
                self.ui.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(count_day))

            except:
                self.ui.tableWidget.setItem(row, column, QtWidgets.QTableWidgetItem(correct_value))
                QtWidgets.QMessageBox.information(self, "Изменение даты", 'Неправильный формат даты или некорректная дата. \nФормат даты "01.01.2000"')

        def checkName(name):
            if name == correct_value:
                return True

            if name:
                all_names = []
                for n in dict_birthday.keys():
                    all_names.append(n)

                if value in all_names:
                    self.ui.tableWidget.setItem(row, column, QtWidgets.QTableWidgetItem(correct_value))
                    QtWidgets.QMessageBox.information(self, "Изменение имени", 'Такое имя уже есть')
                    return False
                else:
                    return True
            else:
                self.ui.tableWidget.setItem(row, column, QtWidgets.QTableWidgetItem(correct_value))
                QtWidgets.QMessageBox.information(self, "Изменение имени", 'Имя не может быть пустым')
                return False

        def checkRemind(remind):
            countDay = ""

            for i in remind:
                if i.isdigit():
                    countDay += i
            if countDay and int(countDay) >= 1 and int(countDay) <= 30:
                day = self.declinationDay(countDay)
                correct_remind = f"За {countDay} {day}"
                if value == correct_remind:
                    return True
                else:
                    self.ui.tableWidget.setItem(row, column, QtWidgets.QTableWidgetItem(correct_remind))
            else:
                self.ui.tableWidget.setItem(row, column, QtWidgets.QTableWidgetItem(correct_value))
                QtWidgets.QMessageBox.information(self, "Изменение напоминания", "Напоминание может быть от 1 до 30 дней")

        if not self.changeCell:
            return

        if column == 0:
            checkData(value)
        if column == 1:
            checkName(value)
        if column == 4:
            checkRemind(value)

    def clickTable(self, row, column):
        self.changeCell = self.ui.tableWidget.item(row, column).text()

        if column == 2:
            QtWidgets.QMessageBox.information(self, "Изменение возраста", "Для того чтобы изменить возраст изменить дату рождения")
            self.fillTable()

        if column == 3:
            QtWidgets.QMessageBox.information(self, "Изменение даты", 'Для того чтобы изменить кол-во дней до наступления события изменить дату рождения')
            #self.ui.tableWidget.setItem(row, column, QtWidgets.QTableWidgetItem(self.changeCell))
            self.fillTable()

    def changeTable(self, row, column):
        self.changedCell = self.ui.tableWidget.item(row, column).text()
        self.checkCorrectCell(self.changedCell, self.changeCell, row, column)

        self.table_to_dict()
        self.changeCell = ""

    def create_list_remind(self):
        self.remind_list = []

        for name, data in dict_birthday.items():
            born = data[0]
            remind = data[1]
            interval_day = int(self.countIntervalDay(born))

            if interval_day == 0:
                age = int(self.countAge(born))
            else:
                age = int(self.countAge(born)) + 1

            if interval_day <= remind:
                self.remind_list.append([interval_day, name, age])

        return self.remind_list

    def print_remind_list(self):
        list_remind = self.create_list_remind()
        list_remind.sort()

        list_remind_final = ""
        hb = True
        soon = True
        for i in list_remind:
            interval = i[0]
            name = i[1]
            age = i[2]
            decDay = self.declinationDay(interval)
            decYear = self.declinationYear(age)
            decTurned = self.declinationTurned(age)

            if interval == 0 and hb:
                hb = False
                prefix = "Сегодня День Рождения:\n"
            elif interval != 0 and soon and list_remind_final:
                soon = False
                prefix = "\n"
            else:
                soon = False
                prefix = ""


            if interval == 0:
                list_remind_final += f'{prefix}{name} - {decTurned} {age} {decYear}\n'
            elif interval == 1:
                list_remind_final += f'{prefix}{name} - завтра исполнится {age} {decYear}\n'
            elif interval == 2:
                list_remind_final += f'{prefix}{name} - послезавтра исполнится {age} {decYear}\n'
            else:
                list_remind_final += f'{prefix}{name} - через {interval} {decDay} исполнится {age} {decYear}\n'

        if list_remind_final:
            self.tray_icon.showMessage(
            "Дни Рождения", list_remind_final, QSystemTrayIcon.Information, 5000)
        else:
            self.tray_icon.showMessage("Дни Рождения", "В ближайшее время ни у кого нет Дня Рождения", QSystemTrayIcon.Information, 5000)

    def setupSize(self):
        self.ui.tableWidget.setColumnWidth(0, 110)
        self.ui.tableWidget.setColumnWidth(2, 60)
        self.ui.tableWidget.setColumnWidth(3, 100)
        self.ui.tableWidget.setColumnWidth(4, 100)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

    def sort_dict(self):
        data_list = []
        for name, data in dict_birthday.items():

            data_num = data[0].split("-")[1] + data[0].split("-")[2]
            data_list.append((data_num, name))

        sorted_data_list = [name[1] for name in sorted(data_list)]
        return sorted_data_list

    def setCurrentData(self):
        datetime.date.today()
        data = str(datetime.date.today()).split("-")

        year = data[0]
        month = data[1]
        day = data[2]

        self.ui.label.setText(f"Сегодня {day:0>2}.{month:0>2}.{year}")

    def open_add_window(self):
        window = modal_window(self)
        window.show()

        #self.fillTable()

    def countAge(self, born):
        born_obj = datetime.datetime.strptime(born, "%Y-%m-%d")
        today = datetime.date.today()

        age = today.year - born_obj.year - ((today.month, today.day) < (born_obj.month, born_obj.day))

        return str(age)

    def countIntervalDay(self, data):
        today = [int(i) for i in str(datetime.date.today()).split("-")]
        hbDay = [int(i) for i in data.split("-")]
        hbDay[0] = today[0]

        interval = -1
        while int(interval) < 0:
            today1 = datetime.date.today()
            hb1 = datetime.date(hbDay[0], hbDay[1], hbDay[2])

            interval = hb1 - today1
            interval = str(interval).split()[0]

            if interval == "0:00:00":
                interval = 0
            elif int(interval) < 0:
                hbDay[0] += 1

        return interval

    def declinationDay(self, num):
        num = int(num)
        if num >= 11 and num <= 20:
            result = "дней"
        elif int(str(num)[-1]) == 1:
            result = "день"
        elif int(str(num)[-1]) >= 2 and int(str(num)[-1]) <= 4:
            result = "дня"
        elif int(str(num)[-1]) >= 5 and int(str(num)[-1]) <= 9 or int(str(num)[-1]) == 0:
            result = "дней"

        return result

    def declinationYear(self, num):
        num = int(num)
        if num >= 11 and num <= 20:
            result = "лет"
        elif int(str(num)[-1]) == 1:
            result = "год"
        elif int(str(num)[-1]) >= 2 and int(str(num)[-1]) <= 4:
            result = "года"
        elif int(str(num)[-1]) >= 5 and int(str(num)[-1]) <= 9 or int(str(num)[-1]) == 0:
            result = "лет"

        return result

    def declinationTurned(self, num):
        num = int(num)

        if int(str(num)[-1]) == 1:
            result = "исполнился"
        else:
            result = "исполнилось"

        return result

    def clearTableWidget(self):
        count = self.ui.tableWidget.rowCount()

        if count == 0:
            pass

        for i in range(0, count):
            self.ui.tableWidget.removeRow(0)

    def table_to_dict(self):
        def extract_remind(text):
            result = ""
            for i in text:
                if i.isdigit():
                    result += i
            result = int(result)

            return result

        def convert_data_format(data):
            data = data.replace(".", "-")
            data = data.split("-")
            data.reverse()
            data = "-".join(data)

            return data

        if not self.changeCell:
            return

        dict_birthday.clear()
        countRow = self.ui.tableWidget.rowCount()

        for i in range(0, countRow):
            data = convert_data_format(self.ui.tableWidget.item(i, 0).text())
            name = self.ui.tableWidget.item(i, 1).text()
            remind = extract_remind(self.ui.tableWidget.item(i, 4).text())

            dict_birthday[name] = [data, remind]

        #self.fillTable()
        #self.packingDict()

        save_dict(dict_config)
        print_dict(dict_birthday)
        print_dict(dict_settings)

    def del_person(self):
        try:
            currentRow = self.ui.tableWidget.currentRow()
            person = self.ui.tableWidget.item(currentRow, 1).text()
            if self.ui.tableWidget.currentRow() == -1:
                return

            result = QtWidgets.QMessageBox.question(self, "Удаление", f"Вы действительно хотите удалить {person}?",
                                                    QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if result == QtWidgets.QMessageBox.Yes:
                del dict_birthday[person]
            else:
                pass

            #update_dict(dict_birthday)
            self.fillTable()

            self.selectRow(currentRow, 1)
        except:
            return

class modal_window(QtWidgets.QWidget):
    def __init__(self,parent=GUI):
        super().__init__(parent,QtCore.Qt.Window)           # (parent) для того чтобы окно открывалось внутри существующего
        self.modal = Ui_Form()
        self.modal.setupUi(self)
        self.setWindowModality(2)
        # setWindowModality(2)принимает значения:
        # 0 - не использовать модульные окна (по умолчанию),
        # 1 использовать модульное окно только для предыдущих окон,
        # 2 - использовать модульное окно для всех окон программы

        self.modal.btn_add.clicked.connect(self.add_person)




    def add_person(self):
        dataBirthday = self.modal.dateEdit.text().split(".")
        dataBirthday.reverse()
        dataBirthday = "-".join(dataBirthday)

        personName = self.modal.lineEdit.text()
        dayReminder = int(self.modal.comboreminder.currentText())

        if personName in dict_birthday:
            if self.message_already_have():
                dict_birthday[personName] = [dataBirthday, dayReminder]
                self.clear()
        elif not personName:
            QtWidgets.QMessageBox.warning(self, "Сообщение", "Введите имя человека")
        else:
            dict_birthday[personName] = [dataBirthday, dayReminder]
            self.clear()

        global update
        update = True


        save_dict(dict_birthday)
        self.modal.lineEdit.setFocus()

        #save_dict(dict_birthday)

    def clear(self):
        self.modal.lineEdit.setText("")
        self.modal.comboreminder.setCurrentIndex(2)

    def message_already_have(self):
        result = QtWidgets.QMessageBox.question(self, "Сообщение", "Такое имя уже есть, заменить?",
                                                QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if result == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mywin = GUI()
    if not tray:
        mywin.show()
    sys.exit(app.exec_())