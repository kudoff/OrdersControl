import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QInputDialog
from UI import Ui_Form


class OrderControl(QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Устанавливаем фиксированный размер окна
        self.setFixedSize(1280, 720)

        # Подключаем базу данных
        self.con = sqlite3.connect('clients_db.db')

        # Активируем все кнопки
        self.searchBtn.clicked.connect(self.update_result)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.saveBtn.clicked.connect(self.save_results)
        self.addBtn.clicked.connect(self.add_info)
        self.showBtn.clicked.connect(self.show_data)
        self.cuponsBtn.clicked.connect(self.show_cupons)
        self.ordersBtn.clicked.connect(self.show_orders)

        # Добавляем вспомогательные переменные
        self.modified = {}
        self.titles = None
        self.show_data()

    # Функция, отображающая таблицу с данными всех клиентов
    def show_data(self):
        self.cur_window = 'clients'
        self.addBtn.setText('Добавить клиента')
        self.flag = False

        res = self.con.cursor().execute("SELECT * FROM clients_info").fetchall()

        # Заполним размеры таблицы
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)

        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

        self.flag = True

    # Функция, отображающая таблицу с данными об акциях
    def show_cupons(self):
        self.cur_window = 'cupons'
        self.addBtn.setText('Добавить акцию')
        self.flag = False

        res = self.con.cursor().execute("SELECT * FROM cupons").fetchall()

        # Заполним размеры таблицы
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)

        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

        self.flag = True

    # Функция, отображающая таблицу с данными о текущих заказах
    def show_orders(self):
        self.cur_window = 'orders'
        self.addBtn.setText('Добавить заказ')
        self.flag = False

        res = self.con.cursor().execute("SELECT * FROM CurrentOrders").fetchall()

        # Заполним размеры таблицы
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)

        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

        self.flag = True

    # Функция, с помощью которой происходит выбор определенного клиента
    def update_result(self):
        cur = self.con.cursor()
        item_id = self.fio.text()

        # Получили результат запроса, который ввели в текстовое поле
        result = cur.execute("SELECT * FROM clients_info WHERE ФИО=?",
                             (item_id,)).fetchall()

        # Заполнили размеры таблицы
        self.tableWidget.setRowCount(len(result))

        # Если запись не нашлась, то не будем ничего делать
        if not result:
            self.statusBar().showMessage('Ничего не нашлось')
            self.show_data()
            return
        else:
            self.statusBar().showMessage(f"Нашлась запись с id = {item_id}")
            self.cur_window = 'client'

        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]

        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

        self.modified = {}

    # Функция, запоминающая изменения таблицы
    # Если значение в ячейке было изменено,
    # то в словарь записывается пара: название поля, новое значение
    def item_changed(self, item):
        if not self.flag:
            return

        if self.cur_window == 'client':
            self.modified[self.titles[item.column()]] = item.text()
        else:
            self.modified = {}

            if self.cur_window == 'clients':
                QMessageBox.critical(self, "Ошибка", "Выберите по поиску определённого человека", QMessageBox.Ok)
                self.show_data()
            elif self.cur_window == 'cupons':
                QMessageBox.critical(self, "Ошибка", "Нельзя изменить акции!", QMessageBox.Ok)
                self.show_cupons()
            elif self.cur_window == 'orders':
                QMessageBox.critical(self, "Ошибка", "Нельзя изменить заказы!", QMessageBox.Ok)
                self.show_orders()

    # Функция, сохраняющая изменения таблицы
    def save_results(self):
        if self.modified:
            cur = self.con.cursor()

            que = "UPDATE clients_info SET\n"
            for key in self.modified.keys():
                que += "{}='{}'\n".format(key, self.modified.get(key))
            que += "WHERE ФИО = ?"

            cur.execute(que, (self.fio.text(),))

            self.con.commit()
            self.modified.clear()

    # Функция, добавления информации о клиенте, акции или заказе в зависимости
    # от значения флага cur_window, которому присваиваются разные значения в
    # зависимости от выбранного окна
    def add_info(self):
        if self.addBtn.text() == 'Добавить клиента':
            cur = self.con.cursor()

            fio, ok = QInputDialog.getText(self, 'Основная информация', 'ФИО:')
            if not ok:
                return
            if not fio:
                fio = 'Не добавлено'

            address, ok = QInputDialog.getText(self, 'Основная информация', 'Адрес заказа:')
            if not ok or not address:
                address = 'Не добавлен'

            phone, ok = QInputDialog.getText(self, 'Основная информация', 'Номер телефона:')
            if not ok or not phone:
                phone = 'Не добавлен'

            n_order, ok = QInputDialog.getText(self, 'Дополнительная информация', 'Номер заказа:')
            if not ok or not n_order:
                n_order = 'Нет заказов'

            past_orders = 'Не было заказов'

            pref, ok = QInputDialog.getText(self, 'Дополнительная информация', 'Предпочтения:')
            if not ok or not pref:
                pref = 'Нет предпочтений'

            cur.execute("INSERT INTO clients_info(ФИО,Адрес,НомерТелефона,ТекущиеЗаказы,ПрошлыеЗаказы,Предпочтения)"
                        f"VALUES(?,?,?,?,?,?)", (fio, address, phone, n_order, past_orders, pref)).fetchall()

            self.con.commit()
            self.show_data()
        elif self.addBtn.text() == 'Добавить акцию':
            cur = self.con.cursor()

            name, ok = QInputDialog.getText(self, 'Основная информация', 'Название:')
            if not ok:
                return
            if not name:
                name = 'Не добавлено'

            rules, ok = QInputDialog.getText(self, 'Основная информация', 'Правила:')
            if not ok or not rules:
                rules = 'Не добавлены'

            cur.execute("INSERT INTO cupons(Имя,Описание) VALUES(?,?)", (name, rules)).fetchall()

            self.con.commit()
            self.show_cupons()
        elif self.addBtn.text() == 'Добавить заказ':
            cur = self.con.cursor()

            name, ok = QInputDialog.getText(self, 'Основная информация', 'ФИО клиента:')
            if not ok:
                return
            if not name:
                name = 'Не добавлено'

            number, ok = QInputDialog.getText(self, 'Основная информация', 'Номер заказа:')
            if not ok or not number:
                number = 'Не добавлен'

            structure, ok = QInputDialog.getText(self, 'Основная информация', 'Состав заказа:')
            if not ok or not structure:
                structure = 'Не добавлен'

            cur.execute("INSERT INTO CurrentOrders(Заказчик,НомерЗаказа,СоставЗаказа)"
                        f"VALUES(?,?,?)", (name, number, structure)).fetchall()

            self.con.commit()
            self.show_orders()

    def closeEvent(self, event):
        # При закрытии формы закроем и наше соединение
        # с базой данных
        self.con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OrderControl()
    ex.show()
    sys.exit(app.exec_())
