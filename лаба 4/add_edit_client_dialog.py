import re
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox


class AddEditClientDialog(QDialog):
    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить клиента" if client is None else "Редактировать клиента")

        self.layout = QVBoxLayout()

        # Поле ввода имени клиента
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя клиента (только буквы)")
        self.layout.addWidget(QLabel("Имя клиента:"))
        self.layout.addWidget(self.name_input)

        # Выбор типа клиента
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Обычный", "Скидочный"])
        self.layout.addWidget(QLabel("Тип клиента:"))
        self.layout.addWidget(self.type_combo)

        # Поле ввода базовой стоимости
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("Базовая стоимость")
        self.layout.addWidget(QLabel("Базовая стоимость:"))
        self.layout.addWidget(self.cost_input)

        # Поле ввода скидки
        self.discount_input = QLineEdit()
        self.discount_input.setPlaceholderText("Размер скидки (только для скидочного клиента)")
        self.layout.addWidget(QLabel("Размер скидки:"))
        self.layout.addWidget(self.discount_input)

        # Кнопка сохранения
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_client)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        # Если редактируем клиента, заполняем поля
        if client:
            self.name_input.setText(client["name"])
            self.type_combo.setCurrentText(client["type"])
            self.cost_input.setText(str(client["base_cost"]))
            self.discount_input.setText(str(client.get("discount", 0)))

        # Включаем/отключаем поле скидки в зависимости от типа клиента
        self.type_combo.currentTextChanged.connect(self.toggle_discount_input)

    def toggle_discount_input(self, text):
        """Активирует или деактивирует поле скидки в зависимости от типа клиента."""
        if text == "Скидочный":
            self.discount_input.setEnabled(True)
        else:
            self.discount_input.setEnabled(False)
            self.discount_input.setText("0")

    def save_client(self):
        try:
            # Проверка имени клиента
            name = self.name_input.text().strip()
            if not name or not re.match("^[A-Za-zА-Яа-яЁё]+$", name):
                raise ValueError("Имя клиента должно содержать только буквы.")

            # Проверка базовой стоимости
            base_cost = float(self.cost_input.text())
            if base_cost < 0:
                raise ValueError("Базовая стоимость не может быть отрицательной.")
            if base_cost > 10000:
                raise ValueError("Базовая стоимость не может превышать 10000.")

            # Проверка скидки
            discount = float(self.discount_input.text()) if self.type_combo.currentText() == "Скидочный" else 0
            if discount < 0:
                raise ValueError("Скидка не может быть отрицательной.")
            if discount > base_cost:
                raise ValueError("Скидка не может превышать базовую стоимость.")
            if discount > 5000:
                raise ValueError("Скидка не может превышать 5000.")

            # Сохраняем данные клиента
            self.client_data = (name, self.type_combo.currentText(), base_cost, discount)
            self.accept()

        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def get_client_data(self):
        """Возвращает данные клиента."""
        return self.client_data
