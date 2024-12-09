from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
import re


class AddEditClientDialog(QDialog):
    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить клиента" if client is None else "Редактировать клиента")
        self.layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.layout.addWidget(QLabel("Имя клиента:"))
        self.layout.addWidget(self.name_input)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Обычный", "Скидочный"])
        self.layout.addWidget(QLabel("Тип клиента:"))
        self.layout.addWidget(self.type_combo)

        self.cost_input = QLineEdit()
        self.layout.addWidget(QLabel("Базовая стоимость:"))
        self.layout.addWidget(self.cost_input)

        self.discount_input = QLineEdit()
        self.layout.addWidget(QLabel("Скидка:"))
        self.layout.addWidget(self.discount_input)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_client)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)
        if client:
            self.name_input.setText(client["name"])
            self.type_combo.setCurrentText(client["type"])
            self.cost_input.setText(str(client["base_cost"]))
            self.discount_input.setText(str(client.get("discount", 0)))

    def save_client(self):
        try:
            name = self.name_input.text().strip()
            if not name or not re.match("^[A-Za-zА-Яа-яЁё]+$", name):
                raise ValueError("Имя должно содержать только буквы.")

            client_type = self.type_combo.currentText()
            base_cost = float(self.cost_input.text())
            discount = float(self.discount_input.text() or 0)

            if base_cost < 0 or discount < 0:
                raise ValueError("Стоимость и скидка не могут быть отрицательными.")
            if discount > base_cost:
                raise ValueError("Скидка не может превышать стоимость.")

            self.client_data = (name, client_type, base_cost, discount)
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def get_client_data(self):
        return self.client_data
