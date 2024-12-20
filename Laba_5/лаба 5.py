import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class Tariff:
    def __init__(self, name, price, discount=None):
        self.name = name
        self.price = price
        self.discount = discount

    def calculate_price(self):
        if self.discount:
            return self.price - self.discount
        return self.price


class Client:
    def __init__(self, name, tariff):
        self.name = name
        self.tariff = tariff

    def calculate_revenue(self):
        return self.tariff.calculate_price()


class DatabaseManager:
    def __init__(self, db_name="data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_database()

    def init_database(self):
        self.cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS tariffs (
            name TEXT PRIMARY KEY,
            price REAL NOT NULL CHECK(price > 0 AND price < 10000),
            discount REAL
        )""")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            name TEXT PRIMARY KEY,
            tariff_name TEXT NOT NULL,
            FOREIGN KEY(tariff_name) REFERENCES tariffs(name)
        )""")
        self.conn.commit()

    def save_tariffs(self, tariffs):
        self.cursor.execute("DELETE FROM tariffs")
        for tariff in tariffs:
            self.cursor.execute("INSERT INTO tariffs (name, price, discount) VALUES (?, ?, ?)",
                                (tariff.name, tariff.price, tariff.discount))
        self.conn.commit()

    def save_clients(self, clients):
        self.cursor.execute("DELETE FROM clients")
        for client in clients:
            self.cursor.execute(""" 
            INSERT INTO clients (name, tariff_name) VALUES (?, ?)""",
                                (client.name, client.tariff.name))
        self.conn.commit()

    def load_tariffs(self):
        self.cursor.execute("SELECT * FROM tariffs")
        return [Tariff(name, price, discount) for name, price, discount in self.cursor.fetchall()]

    def load_clients(self, tariffs):
        self.cursor.execute("SELECT * FROM clients")
        clients = []
        for name, tariff_name in self.cursor.fetchall():
            tariff = next((t for t in tariffs if t.name == tariff_name), None)
            if tariff:
                clients.append(Client(name, tariff))
        return clients

    def close(self):
        self.conn.close()


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cargo Manager")
        self.geometry("600x600")

        self.tariffs = []
        self.clients = []

        self.db_manager = DatabaseManager()

        self.setup_tabs()

    def setup_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=1, fill="both")

        self.tariff_tab = ttk.Frame(self.notebook)
        self.client_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tariff_tab, text="Тарифы")
        self.notebook.add(self.client_tab, text="Клиенты")

        self.setup_tariff_tab()
        self.setup_client_tab()

        self.save_button = tk.Button(self, text="Сохранить в базу данных", command=self.save_to_database)
        self.save_button.pack(pady=10)

        self.load_button = tk.Button(self, text="Загрузить из базы данных", command=self.load_from_database)
        self.load_button.pack(pady=10)

        self.calculate_button = tk.Button(self, text="Подсчитать общую стоимость клиентов",
                                          command=self.calculate_total_revenue)
        self.calculate_button.pack(pady=10)

    def setup_tariff_tab(self):
        tk.Label(self.tariff_tab, text="Название тарифа:").grid(row=0, column=0, padx=5, pady=5)
        self.tariff_name_entry = tk.Entry(self.tariff_tab)
        self.tariff_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.tariff_tab, text="Цена:").grid(row=1, column=0, padx=5, pady=5)
        self.tariff_price_entry = tk.Entry(self.tariff_tab)
        self.tariff_price_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.tariff_tab, text="Тип тарифа:").grid(row=2, column=0, padx=5, pady=5)
        self.tariff_type_var = tk.StringVar(value="normal")

        self.tariff_type_frame = ttk.Frame(self.tariff_tab)
        self.tariff_type_frame.grid(row=2, column=1, padx=5, pady=5)

        self.tariff_type_normal_rb = tk.Radiobutton(self.tariff_type_frame, text="Обычный",
                                                    variable=self.tariff_type_var, value="normal")
        self.tariff_type_normal_rb.grid(row=0, column=0, padx=5, pady=5)

        self.tariff_type_discount_rb = tk.Radiobutton(self.tariff_type_frame, text="Скидочный",
                                                      variable=self.tariff_type_var, value="discount")
        self.tariff_type_discount_rb.grid(row=0, column=1, padx=5, pady=5)

        self.discount_label = tk.Label(self.tariff_tab, text="Скидка:")
        self.discount_label.grid(row=3, column=0, padx=5, pady=5)
        self.discount_entry = tk.Entry(self.tariff_tab)
        self.discount_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(self.tariff_tab, text="Добавить тариф", command=self.add_tariff).grid(row=4, column=0, columnspan=2,
                                                                                        pady=10)
        self.edit_tariff_button = tk.Button(self.tariff_tab, text="Редактировать тариф", command=self.edit_tariff)
        self.edit_tariff_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.tariff_listbox = tk.Listbox(self.tariff_tab, width=40, height=10)
        self.tariff_listbox.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    def setup_client_tab(self):
        tk.Label(self.client_tab, text="Имя клиента:").grid(row=0, column=0, padx=5, pady=5)
        self.client_name_entry = tk.Entry(self.client_tab)
        self.client_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.client_tab, text="Выберите тариф:").grid(row=1, column=0, padx=5, pady=5)
        self.tariff_var = tk.StringVar()
        self.tariff_dropdown = ttk.Combobox(self.client_tab, textvariable=self.tariff_var)
        self.tariff_dropdown.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.client_tab, text="Добавить клиента", command=self.add_client).grid(row=2, column=0, columnspan=2,
                                                                                          pady=10)
        self.edit_client_button = tk.Button(self.client_tab, text="Редактировать клиента", command=self.edit_client)
        self.edit_client_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.client_listbox = tk.Listbox(self.client_tab, width=40, height=10)
        self.client_listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def add_tariff(self):
        try:
            name = self.tariff_name_entry.get()
            price = float(self.tariff_price_entry.get())
            tariff_type = self.tariff_type_var.get()
            discount = None
            if tariff_type == "discount":
                discount = float(self.discount_entry.get()) if self.discount_entry.get() else None

            if name and 0 < price < 10000:
                tariff = Tariff(name, price, discount)
                self.tariffs.append(tariff)
                self.update_tariff_listbox()
                self.update_tariff_dropdown()
                self.tariff_name_entry.delete(0, tk.END)
                self.tariff_price_entry.delete(0, tk.END)
                self.discount_entry.delete(0, tk.END)
            else:
                raise ValueError("Некорректные данные")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное название и цену тарифа")

    def add_client(self):
        try:
            name = self.client_name_entry.get()
            if not name.isalpha():
                raise ValueError("Имя клиента должно содержать только буквы")
            tariff_name = self.tariff_var.get()
            tariff = next((t for t in self.tariffs if t.name == tariff_name), None)
            if name and tariff:
                client = Client(name, tariff)
                self.clients.append(client)
                self.update_client_listbox()
                self.client_name_entry.delete(0, tk.END)
            else:
                raise ValueError("Некорректное имя или тариф")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def edit_tariff(self):
        selected_index = self.tariff_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Ошибка", "Выберите тариф для редактирования")
            return

        selected_tariff = self.tariffs[selected_index[0]]
        new_name = self.tariff_name_entry.get() or selected_tariff.name
        try:
            new_price = float(self.tariff_price_entry.get())
            new_discount = float(self.discount_entry.get()) if self.discount_entry.get() else None

            selected_tariff.name = new_name
            selected_tariff.price = new_price
            selected_tariff.discount = new_discount
            self.update_tariff_listbox()
            self.update_tariff_dropdown()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные данные для редактирования")

    def edit_client(self):
        selected_index = self.client_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Ошибка", "Выберите клиента для редактирования")
            return

        selected_client = self.clients[selected_index[0]]
        new_name = self.client_name_entry.get() or selected_client.name
        try:
            if not new_name.isalpha():
                raise ValueError("Имя клиента должно содержать только буквы")
            tariff_name = self.tariff_var.get()
            new_tariff = next((t for t in self.tariffs if t.name == tariff_name), selected_client.tariff)

            selected_client.name = new_name
            selected_client.tariff = new_tariff
            self.update_client_listbox()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def update_tariff_listbox(self):
        self.tariff_listbox.delete(0, tk.END)
        for tariff in self.tariffs:
            price = tariff.calculate_price()
            self.tariff_listbox.insert(tk.END, f"{tariff.name} - {price} руб.")

    def update_client_listbox(self):
        self.client_listbox.delete(0, tk.END)
        for client in self.clients:
            self.client_listbox.insert(tk.END, f"{client.name} - {client.tariff.name}")

    def update_tariff_dropdown(self):
        self.tariff_dropdown["values"] = [tariff.name for tariff in self.tariffs]

    def save_to_database(self):
        self.db_manager.save_tariffs(self.tariffs)
        self.db_manager.save_clients(self.clients)
        messagebox.showinfo("Успех", "Данные сохранены в базу данных")

    def load_from_database(self):
        self.tariffs = self.db_manager.load_tariffs()
        self.clients = self.db_manager.load_clients(self.tariffs)
        self.update_tariff_listbox()
        self.update_client_listbox()
        self.update_tariff_dropdown()

    def calculate_total_revenue(self):
        total_revenue = sum(client.calculate_revenue() for client in self.clients)
        self.show_total_revenue_window(total_revenue)

    def show_total_revenue_window(self, total_revenue):
        revenue_window = tk.Toplevel(self)
        revenue_window.title("Общая стоимость клиентов")

        label = tk.Label(revenue_window, text=f"Общая стоимость клиентов: {total_revenue:.2f} руб.")
        label.pack(padx=10, pady=10)

        close_button = tk.Button(revenue_window, text="Закрыть", command=revenue_window.destroy)
        close_button.pack(pady=10)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
