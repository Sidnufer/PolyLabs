import os
import json
from PyQt5.QtWidgets import QMessageBox


class FileManager:
    def __init__(self, file_name="clients.json"):
        self.file_name = file_name
        self.data = []
        self.load_data()

    def load_data(self):
        """Загрузка данных из файла."""
        if not os.path.exists(self.file_name):
            self.data = []
            self.save_data()  # Создать файл, если его нет
            return

        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except json.JSONDecodeError:
            QMessageBox.warning(None, "Ошибка", f"Файл {self.file_name} поврежден. Создаем новый файл.")
            self.data = []
            self.save_data()

    def save_data(self):
        """Сохранение данных в файл."""
        try:
            with open(self.file_name, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось сохранить данные: {str(e)}")

    def add_client(self, name, client_type, base_cost, discount=0):
        """Добавление клиента."""
        self.data.append({
            "name": name,
            "type": client_type,
            "base_cost": round(base_cost, 2),
            "discount": round(discount, 2),
        })
        self.save_data()

    def delete_client(self, index):
        """Удаление клиента по индексу."""
        if 0 <= index < len(self.data):
            del self.data[index]
            self.save_data()
        else:
            raise IndexError("Индекс клиента выходит за пределы списка.")

    def get_clients(self):
        """Получение списка клиентов."""
        return self.data

    def update_client(self, index, name, client_type, base_cost, discount=0):
        """Обновление данных клиента."""
        if 0 <= index < len(self.data):
            self.data[index] = {
                "name": name,
                "type": client_type,
                "base_cost": round(base_cost, 2),
                "discount": round(discount, 2),
            }
            self.save_data()
        else:
            raise IndexError("Индекс клиента выходит за пределы списка.")
