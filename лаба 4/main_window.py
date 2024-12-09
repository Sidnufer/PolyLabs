from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QDialog, QFileDialog
)
from PyQt5.QtCore import Qt
from FileManager import FileManager
from add_edit_client_dialog import AddEditClientDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Internet Operator with JSON Support")
        self.file_manager = FileManager()

        self.layout = QVBoxLayout()

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Имя клиента", "Тип", "Базовая стоимость", "Скидка"])
        self.layout.addWidget(self.table)

        # Кнопка "Добавить клиента"
        self.add_button = QPushButton("Добавить клиента")
        self.add_button.clicked.connect(self.add_client)
        self.layout.addWidget(self.add_button)

        # Кнопка "Редактировать клиента"
        self.edit_button = QPushButton("Редактировать клиента")
        self.edit_button.clicked.connect(self.edit_client)
        self.layout.addWidget(self.edit_button)

        # Кнопка "Удалить клиента"
        self.delete_button = QPushButton("Удалить клиента")
        self.delete_button.clicked.connect(self.delete_client)
        self.layout.addWidget(self.delete_button)

        # Кнопка "Подсчитать общую стоимость"
        self.calculate_button = QPushButton("Подсчитать общую стоимость")
        self.calculate_button.clicked.connect(self.calculate_total_cost)
        self.layout.addWidget(self.calculate_button)

        # Кнопка "Выбрать файл для сохранения"
        self.change_file_button = QPushButton("Выбрать файл для сохранения")
        self.change_file_button.clicked.connect(self.change_file)
        self.layout.addWidget(self.change_file_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.load_clients()

    def load_clients(self):
        self.table.setRowCount(0)
        for client in self.file_manager.get_clients():
            self.add_table_row(client)

    def add_table_row(self, client):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(client["name"]))
        self.table.setItem(row, 1, QTableWidgetItem(client["type"]))
        self.table.setItem(row, 2, QTableWidgetItem(f"{client['base_cost']:.2f}"))
        self.table.setItem(row, 3, QTableWidgetItem(f"{client['discount']:.2f}"))

    def add_client(self):
        dialog = AddEditClientDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, client_type, base_cost, discount = dialog.get_client_data()
            self.file_manager.add_client(name, client_type, base_cost, discount)
            self.add_table_row({
                "name": name,
                "type": client_type,
                "base_cost": base_cost,
                "discount": discount
            })

    def edit_client(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента для редактирования.")
            return

        client = self.file_manager.get_clients()[selected_row]
        dialog = AddEditClientDialog(self, client=client)
        if dialog.exec_() == QDialog.Accepted:
            name, client_type, base_cost, discount = dialog.get_client_data()
            self.file_manager.update_client(selected_row, name, client_type, base_cost, discount)
            self.load_clients()

    def delete_client(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента для удаления.")
            return

        reply = QMessageBox.question(self, "Подтверждение", "Удалить клиента?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.file_manager.delete_client(selected_row)
            self.table.removeRow(selected_row)

    def calculate_total_cost(self):
        total_cost = 0.0
        for client in self.file_manager.get_clients():
            total_cost += client["base_cost"] - client["discount"]

        QMessageBox.information(self, "Общая стоимость", f"Общая стоимость: {total_cost:.2f}")

    def change_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Выбрать файл для сохранения", "", "JSON Files (*.json)")
        if file_name:
            self.file_manager.file_name = file_name
            self.file_manager.save_data()
            QMessageBox.information(self, "Файл изменен", f"Данные сохранены в: {file_name}")
