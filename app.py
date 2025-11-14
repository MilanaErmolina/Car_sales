import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from datetime import datetime
import re

class CarDealershipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoTradeCenter - Система управления")
        self.root.geometry("1200x700")
        
        self.db = Database()
        self.current_user = None
        self.user_role = None
        
        self.show_login_screen()
    
    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Экран авторизации"""
        self.clear_window()
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True)
        
        ttk.Label(main_frame, text="Авторизация", font=('Arial', 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Выбор роли
        ttk.Label(main_frame, text="Роль:").grid(row=1, column=0, sticky='w', pady=5)
        self.role_var = tk.StringVar(value="Client")
        role_combo = ttk.Combobox(main_frame, textvariable=self.role_var, 
                                  values=["Client", "Admin", "Manager"],
                                  state="readonly")
        role_combo.grid(row=1, column=1, pady=5, padx=5, sticky='ew')
        
        # Поля ввода
        ttk.Label(main_frame, text="Логин:").grid(row=2, column=0, sticky='w', pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Пароль:").grid(row=3, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.grid(row=3, column=1, pady=5, padx=5)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Войти", command=self.login).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Регистрация", command=self.show_registration_screen).pack(side='left', padx=5)
    
    def show_registration_screen(self):
        """Экран регистрации"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True)
        
        ttk.Label(main_frame, text="Регистрация", font=('Arial', 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Поля для ввода
        fields = [
            ("Имя:", "first_name"),
            ("Фамилия:", "last_name"),
            ("Телефон:", "phone"),
            ("Email:", "email"),
            ("Логин:", "username"),
            ("Пароль:", "password"),
            ("Подтверждение пароля:", "confirm_password")
        ]
        
        self.reg_entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i+1, column=0, sticky='w', pady=5)
            entry = ttk.Entry(main_frame, width=30)
            if "password" in field:
                entry.config(show="*")
            entry.grid(row=i+1, column=1, pady=5, padx=5)
            self.reg_entries[field] = entry
        
        # Выбор роли и должности
        ttk.Label(main_frame, text="Роль:").grid(row=8, column=0, sticky='w', pady=5)
        self.reg_role_var = tk.StringVar(value="Client")
        role_combo = ttk.Combobox(main_frame, textvariable=self.reg_role_var,
                                 values=["Client", "Admin", "Manager"], 
                                 state="readonly")
        role_combo.grid(row=8, column=1, pady=5, padx=5, sticky='ew')
        role_combo.bind('<<ComboboxSelected>>', self.on_role_change)
        
        ttk.Label(main_frame, text="Должность:").grid(row=9, column=0, sticky='w', pady=5)
        self.position_entry = ttk.Entry(main_frame, width=30)
        self.position_entry.grid(row=9, column=1, pady=5, padx=5)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Зарегистрироваться", command=self.register).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Назад", command=self.show_login_screen).pack(side='left', padx=5)
    
    def on_role_change(self, event):
        """Обработка изменения роли при регистрации"""
        if self.reg_role_var.get() == "Client":
            self.position_entry.config(state='disabled')
        else:
            self.position_entry.config(state='normal')
    
    def register(self):
        """Регистрация пользователя"""
        # Проверяем подключение к БД
        if not self.db.ensure_connection():
            messagebox.showerror("Ошибка", "Нет подключения к базе данных. Проверьте настройки подключения.")
            return
        
        data = {field: entry.get() for field, entry in self.reg_entries.items()}
        
        # Проверка заполнения полей
        required_fields = ['first_name', 'last_name', 'phone', 'username', 'password']
        for field in required_fields:
            if not data[field]:
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
        
        # Проверка пароля
        if data['password'] != data['confirm_password']:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return
        
        role = self.reg_role_var.get()
        position = self.position_entry.get() if role != "Client" else None
        
        if role != "Client" and not position:
            messagebox.showerror("Ошибка", "Укажите должность для сотрудника")
            return
        
        # Получаем email (может быть пустым)
        email = data.get('email', '')
        
        success, message = self.db.register_user(
            data['first_name'], data['last_name'], data['phone'], 
            email, data['username'], data['password'], 
            role, position
        )
        
        if success:
            messagebox.showinfo("Успех", message)
            self.show_login_screen()
        else:
            messagebox.showerror("Ошибка", message)
    
    def login(self):
        """Авторизация пользователя"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return
        
        user = self.db.login_user(username, password, role)
        if user:
            self.current_user = user
            self.user_role = role
            messagebox.showinfo("Успех", f"Добро пожаловать, {user[1]} {user[2]}!")
            self.show_main_screen()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
    
    def show_main_screen(self):
        """Главный экран приложения"""
        self.clear_window()
        
        # Создание меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню в зависимости от роли
        if self.user_role == "Client":
            client_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Меню", menu=client_menu)
            client_menu.add_command(label="Просмотр автомобилей", command=self.show_cars)
            client_menu.add_command(label="Мои заявки", command=self.show_purchase_requests)
            client_menu.add_command(label="Подать заявку", command=self.show_add_request)
            client_menu.add_command(label="Мои покупки", command=self.show_client_sales)
            client_menu.add_separator()
            client_menu.add_command(label="Выйти", command=self.logout)
        else:
            admin_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Меню", menu=admin_menu)
            admin_menu.add_command(label="Автомобили", command=self.show_cars)
            
            if self.user_role == "Admin":
                admin_menu.add_command(label="Клиенты", command=self.show_clients)
                admin_menu.add_command(label="Сотрудники", command=self.show_employees)
            
            admin_menu.add_command(label="Продажи", command=self.show_sales)
            admin_menu.add_command(label="Заявки", command=self.show_purchase_requests)
            admin_menu.add_command(label="Создать заявку", command=self.show_admin_request)
            admin_menu.add_command(label="Оформить продажу", command=self.show_create_sale)
            admin_menu.add_separator()
            admin_menu.add_command(label="Выйти", command=self.logout)
        
        # Приветствие
        welcome_label = ttk.Label(self.root, text=f"Добро пожаловать, {self.current_user[1]} {self.current_user[2]}!",
                                 font=('Arial', 14))
        welcome_label.pack(pady=20)
        
        # Показываем автомобили по умолчанию
        self.show_cars()
    
    def logout(self):
        """Выход из системы"""
        self.current_user = None
        self.user_role = None
        self.show_login_screen()
    
    def clear_content(self):
        """Очистка основного контента"""
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()
    
    def show_cars(self):
        """Показать список автомобилей"""
        self.clear_content()
        
        # Заголовок
        ttk.Label(self.root, text="Автомобили в наличии", font=('Arial', 16)).pack(pady=10)
        
        # Фильтр статуса
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=10)
        
        ttk.Label(filter_frame, text="Статус:").pack(side='left', padx=5)
        self.status_filter = tk.StringVar(value="В наличии")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter,
                                values=["Все", "В наличии", "Продано", "На ремонте"],
                                state="readonly", width=15)
        status_combo.pack(side='left', padx=5)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_cars())

        # Кнопки для администраторов и менеджеров
        if self.user_role != "Client":
            button_frame = ttk.Frame(self.root)
            button_frame.pack(pady=10)
            
            ttk.Button(button_frame, text="Добавить автомобиль", 
                      command=self.show_add_car).pack(side='left', padx=5)
        
        # Таблица автомобилей
        self.create_cars_table()
        
        self.refresh_cars()

    def create_cars_table(self):
        """Создание таблицы автомобилей"""
        columns = ("ID", "Марка", "Модель", "Год", "Цвет", "Цена", "Статус")
        self.cars_tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.cars_tree.heading(col, text=col)
            self.cars_tree.column(col, width=100)
        
        self.cars_tree.pack(pady=10, fill='both', expand=True)
        
        # Кнопки управления для администраторов и менеджеров
        if self.user_role != "Client":
            control_frame = ttk.Frame(self.root)
            control_frame.pack(pady=10)
            
            ttk.Button(control_frame, text="Редактировать", 
                    command=lambda: self.edit_car(self.cars_tree)).pack(side='left', padx=5)
            ttk.Button(control_frame, text="Удалить", 
                    command=lambda: self.delete_car(self.cars_tree)).pack(side='left', padx=5)

    def refresh_cars(self):
        """Обновление списка автомобилей"""
        for item in self.cars_tree.get_children():
            self.cars_tree.delete(item)
        
        status_filter = self.status_filter.get()
        cars = self.db.get_all_cars()
        
        for car in cars:
            status = car[6]
            # Фильтрация по статусу
            if status_filter != "Все" and status != status_filter:
                continue
                
            display_status = status
            self.cars_tree.insert("", "end", values=(
                car[0], car[1], car[2], car[3], car[4], car[5], display_status
            ))

    def show_add_car(self):
        """Окно добавления автомобиля"""
        self.add_edit_car_window()
    
    def add_edit_car_window(self, car_data=None):
        """Окно добавления/редактирования автомобиля"""
        window = tk.Toplevel(self.root)
        window.title("Добавить автомобиль" if not car_data else "Редактировать автомобиль")
        window.geometry("400x400")
        
        # Фрейм для полей ввода
        form_frame = ttk.Frame(window, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        ttk.Label(form_frame, text="Марка:").grid(row=0, column=0, sticky='w', pady=5)
        brand_entry = ttk.Entry(form_frame, width=30)
        brand_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Модель:").grid(row=1, column=0, sticky='w', pady=5)
        model_entry = ttk.Entry(form_frame, width=30)
        model_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Год:").grid(row=2, column=0, sticky='w', pady=5)
        year_entry = ttk.Entry(form_frame, width=30)
        year_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Цвет:").grid(row=3, column=0, sticky='w', pady=5)
        color_entry = ttk.Entry(form_frame, width=30)
        color_entry.grid(row=3, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Цена:").grid(row=4, column=0, sticky='w', pady=5)
        price_entry = ttk.Entry(form_frame, width=30)
        price_entry.grid(row=4, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Статус:").grid(row=5, column=0, sticky='w', pady=5)
        status_combo = ttk.Combobox(form_frame, values=["В наличии", "Продано", "На ремонте"], state="readonly")
        status_combo.set("В наличии")
        status_combo.grid(row=5, column=1, pady=5, padx=5)
        
        # Заполнение данных при редактировании
        if car_data:
            brand_entry.insert(0, car_data[1])
            model_entry.insert(0, car_data[2])
            year_entry.insert(0, str(car_data[3]))
            color_entry.insert(0, car_data[4])
            price_entry.insert(0, str(car_data[5]))
            status_combo.set(car_data[6])
    
        def save_car():
            # Валидация данных
            if not all([brand_entry.get(), model_entry.get(), year_entry.get(), price_entry.get()]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
            
            try:
                year = int(year_entry.get())
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Год и цена должны быть числами")
                return
            
            if self.db.add_car(brand_entry.get(), model_entry.get(), year, 
                             color_entry.get(), price, status_combo.get()):
                messagebox.showinfo("Успех", "Автомобиль добавлен!")
                window.destroy()
                self.show_cars()
            else:
                messagebox.showerror("Ошибка", "Ошибка при добавлении автомобиля")
        
        def update_car():
            # Валидация данных
            if not all([brand_entry.get(), model_entry.get(), year_entry.get(), price_entry.get()]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
            
            try:
                year = int(year_entry.get())
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Год и цена должны быть числами")
                return
            
            if self.db.update_car(car_data[0], brand_entry.get(), model_entry.get(), year,
                                color_entry.get(), price, status_combo.get()):
                messagebox.showinfo("Успех", "Автомобиль обновлен!")
                window.destroy()
                self.show_cars()
            else:
                messagebox.showerror("Ошибка", "Ошибка при обновлении автомобиля")
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=save_car if not car_data else update_car).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=window.destroy).pack(side='left', padx=5)
    
    def edit_car(self, tree):
        """Редактирование выбранного автомобиля"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите автомобиль для редактирования")
            return
        
        car_data = tree.item(selected[0])['values']
        if car_data[6] == 'Продано':
            messagebox.showwarning("Предупреждение", "Нельзя редактировать проданный автомобиль")
            return
        
        self.add_edit_car_window(car_data)
    
    def delete_car(self, tree):
        """Удаление выбранного автомобиля"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите автомобиль для удаления")
            return
        
        car_data = tree.item(selected[0])['values']
        
        if messagebox.askyesno("Подтверждение", 
                              f"Вы уверены, что хотите удалить автомобиль {car_data[1]} {car_data[2]}?"):
            success, message = self.db.delete_car(car_data[0])
            if success:
                messagebox.showinfo("Успех", message)
                self.show_cars()
            else:
                messagebox.showerror("Ошибка", message)
    
    def show_clients(self):
        """Показать список клиентов"""
        self.clear_content()
        
        ttk.Label(self.root, text="Клиенты", font=('Arial', 16)).pack(pady=10)
        
        columns = ("ID", "Имя", "Фамилия", "Телефон", "Email", "Логин")
        tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        clients = self.db.get_all_clients()
        for client in clients:
            tree.insert("", "end", values=client)
        
        tree.pack(pady=10, fill='both', expand=True)
        
        # Кнопка удаления только для администратора
        if self.user_role == "Admin":
            control_frame = ttk.Frame(self.root)
            control_frame.pack(pady=10)
            
            ttk.Button(control_frame, text="Удалить клиента", 
                      command=lambda: self.delete_client(tree)).pack(side='left', padx=5)
    
    def show_employees(self):
        """Показать список сотрудников"""
        self.clear_content()
        
        ttk.Label(self.root, text="Сотрудники", font=('Arial', 16)).pack(pady=10)
        
        columns = ("ID", "Имя", "Фамилия", "Должность", "Телефон", "Email", "Логин", "Роль")
        tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        employees = self.db.get_all_employees()
        for employee in employees:
            tree.insert("", "end", values=employee)
        
        tree.pack(pady=10, fill='both', expand=True)
        
        # Кнопка удаления только для администратора
        if self.user_role == "Admin":
            control_frame = ttk.Frame(self.root)
            control_frame.pack(pady=10)
            
            ttk.Button(control_frame, text="Удалить сотрудника", 
                      command=lambda: self.delete_employee(tree)).pack(side='left', padx=5)
    
    def delete_employee(self, tree):
        """Удаление выбранного сотрудника"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для удаления")
            return
         
        try:
            employee_data = tree.item(selected[0])['values']
            
            # Извлекаем числовой ID из первого столбца
            employee_id = employee_data[0]
            
            # Если ID - это строка, извлекаем из нее число
            if isinstance(employee_id, str):
                # Удаляем все нечисловые символы
                import re
                employee_id = re.sub(r'[^\d]', '', employee_id)
                
            # Преобразуем в целое число
            employee_id = int(employee_id)
            
            if messagebox.askyesno("Подтверждение", 
                                f"Вы уверены, что хотите удалить сотрудника {employee_data[1]} {employee_data[2]}?"):
                success, message = self.db.delete_employee(employee_id)
                if success:
                    messagebox.showinfo("Успех", message)
                    self.show_employees()
                else:
                    messagebox.showerror("Ошибка", message)
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат ID сотрудника: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении сотрудника: {e}")
        
    def show_sales(self):
        """Показать список продаж"""
        self.clear_content()
    
        ttk.Label(self.root, text="Продажи", font=('Arial', 16)).pack(pady=10)
        
        # Кнопка обновления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Обновить", 
                command=self.refresh_sales).pack(side='left', padx=5)
        
        # Создаем таблицу
        self.create_sales_table()
        self.refresh_sales()

    def create_sales_table(self):
        """Создание таблицы продаж"""
        columns = ("ID", "Марка", "Модель", "Год", "Цвет", "Клиент", "Сотрудник", "Дата", "Цена")
        self.sales_tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)
        
        # Настраиваем колонки
        column_widths = {
            "ID": 50, "Марка": 100, "Модель": 100, "Год": 70, 
            "Цвет": 80, "Клиент": 120, "Сотрудник": 120, "Дата": 100, "Цена": 100
        }
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=column_widths.get(col, 100))
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sales_tree.pack(pady=10, fill='both', expand=True, padx=10)
        scrollbar.pack(side='right', fill='y', padx=(0, 10), pady=10)

    def refresh_sales(self):
        """Обновление списка продаж"""
        if hasattr(self, 'sales_tree'):
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
        
        sales = self.db.get_all_sales()
        
        for sale in sales:
            # Исправление: безопасное форматирование даты
            if sale[7]:
                try:
                    sale_date = datetime.strptime(sale[7], "%Y-%m-%d").strftime("%d.%m.%Y")
                except ValueError:
                    sale_date = sale[7]  # или установите значение по умолчанию
            else:
                sale_date = ""
            
            # Форматируем цену
            sale_price = f"{sale[8]:,.2f} руб." if sale[8] else ""
            
            self.sales_tree.insert("", "end", values=(
                sale[0],  # ID продажи
                sale[1],  # Марка
                sale[2],  # Модель
                sale[3],  # Год
                sale[4],  # Цвет
                sale[5],  # Клиент (имя)
                sale[6],  # Сотрудник (имя)
                sale_date,
                sale_price
            ))
    
    def show_purchase_requests(self):
        """Показать заявки на покупку"""
        self.clear_content()
        
        if self.user_role == "Client":
            ttk.Label(self.root, text="Мои заявки на покупку", font=('Arial', 16)).pack(pady=10)
            button_frame = ttk.Frame(self.root)
            button_frame.pack(pady=10)
            ttk.Button(button_frame, text="Подать новую заявку", 
                    command=self.show_add_request).pack(side='left', padx=5)
        else:
            ttk.Label(self.root, text="Все заявки на покупку", font=('Arial', 16)).pack(pady=10)
            button_frame = ttk.Frame(self.root)
            button_frame.pack(pady=10)
            ttk.Button(button_frame, text="Создать заявку", 
                    command=self.show_admin_request).pack(side='left', padx=5)

        # Получаем заявки в зависимости от роли
        if self.user_role == "Client":
            requests = self.db.get_all_purchase_requests(self.current_user[0])
        else:
            requests = self.db.get_all_purchase_requests()
        
        # Создаем таблицу
        columns = ("ID", "Клиент", "Марка", "Модель", "Макс. цена", "Дата", "Статус")
        tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)
        
        # Настраиваем колонки
        tree.column("ID", width=50)
        tree.column("Клиент", width=150)
        tree.column("Марка", width=100)
        tree.column("Модель", width=100)
        tree.column("Макс. цена", width=100)
        tree.column("Дата", width=100)
        tree.column("Статус", width=100)
        
        for col in columns:
            tree.heading(col, text=col)
        
        # Заполняем данными
        for req in requests:
            max_price = f"{req[4]:,.2f} руб." if req[4] else "Не указана"
            
            # Безопасное форматирование даты
            request_date = ""
            if req[5]:
                if hasattr(req[5], 'strftime'):
                    # Если это объект даты
                    request_date = req[5].strftime("%d.%m.%Y")
                else:
                    # Если это строка, оставляем как есть
                    request_date = str(req[5])
            
            tree.insert("", "end", values=(
                req[0], req[1], req[2], req[3], max_price, request_date, req[6]
            ))
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(pady=10, fill='both', expand=True, padx=10)
        scrollbar.pack(side='right', fill='y', padx=(0, 10), pady=10)
        
        # Кнопки управления для администраторов
        if self.user_role != "Client":
            control_frame = ttk.Frame(self.root)
            control_frame.pack(pady=10)
            
            ttk.Button(control_frame, text="Удалить заявку", 
                    command=lambda: self.delete_purchase_request(tree)).pack(side='left', padx=5)

    def delete_purchase_request(self, tree):
        """Удаление заявки"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку для удаления")
            return
        
        request_data = tree.item(selected[0])['values']
        
        if messagebox.askyesno("Подтверждение", 
                            f"Вы уверены, что хотите удалить заявку #{request_data[0]}?"):
            success, message = self.db.delete_purchase_request(request_data[0])
            if success:
                messagebox.showinfo("Успех", message)
                self.show_purchase_requests()
            else:
                messagebox.showerror("Ошибка", message)

    def delete_client(self, tree):
        """Удаление выбранного клиента"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента для удаления")
            return
        
        try:
            client_data = tree.item(selected[0])['values']
            
            # Извлекаем числовой ID из первого столбца
            client_id = client_data[0]
            
            # Если ID - это строка, извлекаем из нее число
            if isinstance(client_id, str):
                # Удаляем все нечисловые символы
                import re
                client_id = re.sub(r'[^\d]', '', client_id)
                
            # Преобразуем в целое число
            client_id = int(client_id)
            
            if messagebox.askyesno("Подтверждение", 
                                f"Вы уверены, что хотите удалить клиента {client_data[1]} {client_data[2]}?"):
                success, message = self.db.delete_client(client_id)
                if success:
                    messagebox.showinfo("Успех", message)
                    self.show_clients()
                else:
                    messagebox.showerror("Ошибка", message)
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат ID клиента: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении клиента: {e}")

    def show_admin_request(self):
        """Окно создания заявки для администратора/менеджера"""
        window = tk.Toplevel(self.root)
        window.title("Создание заявки на покупку")
        window.geometry("500x400")
        
        main_frame = ttk.Frame(window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Создание заявки на покупку", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Выбор клиента
        ttk.Label(main_frame, text="Клиент:").pack(anchor='w', pady=5)
        clients = self.db.get_all_clients()
        client_var = tk.StringVar()
        client_combo = ttk.Combobox(main_frame, textvariable=client_var, state="readonly", width=50)
        client_combo['values'] = [f"{client[0]} - {client[1]} {client[2]} ({client[3]})" for client in clients]
        if clients:
            client_combo.current(0)
        client_combo.pack(fill='x', pady=5)
        
        # Выбор автомобиля
        ttk.Label(main_frame, text="Автомобиль:").pack(anchor='w', pady=5)
        available_cars = self.db.get_available_cars()
        car_var = tk.StringVar()
        car_combo = ttk.Combobox(main_frame, textvariable=car_var, state="readonly", width=50)
        car_combo['values'] = [f"{car[0]} - {car[1]} {car[2]} {car[3]}г. ({car[4]}) - {car[5]:,.2f} руб." for car in available_cars]
        if available_cars:
            car_combo.current(0)
        car_combo.pack(fill='x', pady=5)
        
        # Максимальная цена
        ttk.Label(main_frame, text="Максимальная цена:").pack(anchor='w', pady=5)
        price_entry = ttk.Entry(main_frame, width=30)
        
        # Автозаполнение цены при выборе автомобиля
        def on_car_select(event):
            if car_combo.get():
                try:
                    car_id = int(car_combo.get().split(' - ')[0])
                    car = self.db.get_car_by_id(car_id)
                    if car:
                        price_entry.delete(0, tk.END)
                        price_entry.insert(0, str(car[5]))
                except:
                    pass
        
        car_combo.bind('<<ComboboxSelected>>', on_car_select)
        
        price_entry.pack(fill='x', pady=5)
        
        def create_request():
            if not client_combo.get():
                messagebox.showerror("Ошибка", "Выберите клиента")
                return
            
            if not car_combo.get():
                messagebox.showerror("Ошибка", "Выберите автомобиль")
                return
            
            if not price_entry.get():
                messagebox.showerror("Ошибка", "Укажите максимальную цену")
                return
            
            try:
                client_id = int(client_combo.get().split(' - ')[0])
                car_id = int(car_combo.get().split(' - ')[0])
                max_price = float(price_entry.get())
                
                if max_price <= 0:
                    messagebox.showerror("Ошибка", "Цена должна быть положительным числом")
                    return
                
                # Получаем информацию об автомобиле
                car = self.db.get_car_by_id(car_id)
                if not car:
                    messagebox.showerror("Ошибка", "Автомобиль не найден")
                    return
                
                # Создаем заявку
                success = self.db.add_purchase_request(
                    client_id,
                    car_id,     # CarID из выбранного автомобиля
                    car[1],     # Brand
                    car[2],     # Model
                    max_price
                )
                
                if success:
                    messagebox.showinfo("Успех", "Заявка успешно создана!")
                    window.destroy()
                    self.show_purchase_requests()
                else:
                    messagebox.showerror("Ошибка", "Ошибка при создании заявки")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную цену")
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Подтвердить заявку", 
                  command=create_request).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=window.destroy).pack(side='left', padx=5)
    
    def show_add_request(self):
        """Окно подачи заявки на покупку для клиента"""
        if self.user_role == "Client":
            self.show_car_selection_for_request()
        else:
            self.show_admin_request()

    def show_client_sales(self):
        """Показать покупки текущего клиента"""
        self.clear_content()
        
        ttk.Label(self.root, text="Мои покупки", font=('Arial', 16)).pack(pady=10)
        
        # Получаем продажи клиента
        sales = self.db.get_client_sales(self.current_user[0])
        
        if not sales:
            ttk.Label(self.root, text="У вас пока нет покупок", 
                    font=('Arial', 12), foreground='gray').pack(pady=50)
            return
        
        # Создаем таблицу
        columns = ("ID", "Марка", "Модель", "Год", "Цвет", "Менеджер", "Дата", "Цена")
        tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)
        
        # Настраиваем колонки
        tree.column("ID", width=50)
        tree.column("Марка", width=100)
        tree.column("Модель", width=100)
        tree.column("Год", width=70)
        tree.column("Цвет", width=80)
        tree.column("Менеджер", width=120)
        tree.column("Дата", width=100)
        tree.column("Цена", width=100)
        
        for col in columns:
            tree.heading(col, text=col)
        
        # Заполняем данными
        for sale in sales:
            # Форматируем дату
            sale_date = sale[6]
            if hasattr(sale_date, 'strftime'):
                # Если это объект даты
                sale_date = sale_date.strftime("%d.%m.%Y")
            elif not sale_date:
                sale_date = ""
            # Форматируем цену
            sale_price = f"{sale[7]:,.2f} руб." if sale[7] else ""
            
            tree.insert("", "end", values=(
                sale[0],  # ID
                sale[1],  # Марка
                sale[2],  # Модель
                sale[3],  # Год
                sale[4],  # Цвет
                sale[5],  # Менеджер
                sale_date,
                sale_price
            ))
        
        tree.pack(pady=10, fill='both', expand=True)
    
    def show_car_selection_for_request(self):
        """Показ доступных автомобилей для выбора (для клиентов)"""
        window = tk.Toplevel(self.root)
        window.title("Выбор автомобиля для заявки")
        window.geometry("800x600")
        
        main_frame = ttk.Frame(window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Выберите автомобиль для заявки:", 
                  font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Получаем доступные автомобили
        available_cars = self.db.get_available_cars()
        
        if not available_cars:
            ttk.Label(main_frame, text="Нет доступных автомобилей в наличии", 
                      foreground='red').pack(pady=20)
            ttk.Button(main_frame, text="Закрыть", 
                      command=window.destroy).pack(pady=10)
            return
        
        # Создаем таблицу с автомобилями
        columns = ("ID", "Марка", "Модель", "Год", "Цвет", "Цена")
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=12)
        
        # Настраиваем колонки
        tree.column("ID", width=50)
        tree.column("Марка", width=120)
        tree.column("Модель", width=120)
        tree.column("Год", width=80)
        tree.column("Цвет", width=100)
        tree.column("Цена", width=120)
        
        for col in columns:
            tree.heading(col, text=col)
        
        # Заполняем данными (группируем по марке и модели)
        displayed_cars = set()
        for car in available_cars:
            car_key = (car[1], car[2])  # Марка и модель
            
            if car_key not in displayed_cars:
                price_formatted = f"{car[5]:,.2f} руб." if car[5] else "Цена не указана"
                tree.insert("", "end", values=(
                    car[0],  # ID первого автомобиля с такой маркой/моделью
                    car[1],  # Марка
                    car[2],  # Модель
                    car[3],  # Год
                    car[4],  # Цвет
                    price_formatted
                ))
                displayed_cars.add(car_key)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(pady=10, fill='both', expand=True)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        def on_car_select():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Предупреждение", "Выберите автомобиль из списка")
                return
            
            car_data = tree.item(selected[0])['values']
            window.destroy()
            self.show_request_confirmation(car_data)
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Выбрать автомобиль", 
                  command=on_car_select).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=window.destroy).pack(side='left', padx=5)
    
    def show_request_confirmation(self, car_data):
        """Окно подтверждения заявки с указанием цены"""
        window = tk.Toplevel(self.root)
        window.title("Подтверждение заявки")
        window.geometry("500x500")
        window.resizable(False, False)
        
        main_frame = ttk.Frame(window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Информация о выбранном автомобиле
        ttk.Label(main_frame, text="Выбранный автомобиль:", 
                  font=('Arial', 12, 'bold')).pack(pady=10)
        
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(pady=10, fill='x')

        style = ttk.Style()
        style.configure('Bold.TLabel', font=('Arial', 10, 'bold'))
        
        ttk.Label(info_frame, text="Марка:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        ttk.Label(info_frame, text=car_data[1], font=('Arial', 10)).grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(info_frame, text="Модель:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        ttk.Label(info_frame, text=car_data[2], font=('Arial', 10)).grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Label(info_frame, text="Год:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        ttk.Label(info_frame, text=car_data[3], font=('Arial', 10)).grid(row=2, column=1, sticky='w', pady=5)
        
        ttk.Label(info_frame, text="Цвет:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        ttk.Label(info_frame, text=car_data[4], font=('Arial', 10)).grid(row=3, column=1, sticky='w', pady=5)
        
        ttk.Label(info_frame, text="Цена в каталоге:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=5)
        ttk.Label(info_frame, text=car_data[5], font=('Arial', 10)).grid(row=4, column=1, sticky='w', pady=5)
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Поле для указания максимальной цены
        ttk.Label(main_frame, text="Укажите максимальную цену, которую вы готовы заплатить:", 
                  font=('Arial', 10)).pack(pady=10)
        
        price_frame = ttk.Frame(main_frame)
        price_frame.pack(pady=10)
        
        ttk.Label(price_frame, text="Цена (руб.):").pack(side='left', padx=5)
        price_entry = ttk.Entry(price_frame, width=20, font=('Arial', 10))
        price_entry.pack(side='left', padx=5)
        
        # Предзаполняем цену из каталога
        try:
            # Извлекаем число из форматированной строки цены
            catalog_price_str = car_data[5].replace(' руб.', '').replace(',', '')
            catalog_price = float(''.join(filter(str.isdigit, catalog_price_str)))
            price_entry.insert(0, str(int(catalog_price)))
        except:
            pass

        # Функция для обработки нажатия Enter
        def on_enter(event):
            submit_request()
        
        # Привязываем обработчик нажатия Enter к полю ввода цены
        price_entry.bind('<Return>', on_enter)

        # Функция для подачи заявки
        def submit_request():
            if not price_entry.get():
                messagebox.showerror("Ошибка", "Укажите максимальную цену")
                return
            
            try:
                max_price = float(price_entry.get())
                if max_price <= 0:
                    messagebox.showerror("Ошибка", "Цена должна быть положительным числом")
                    return
                
                if max_price > 1000000000:  # 1 миллиард
                    messagebox.showerror("Ошибка", "Слишком большая цена. Максимум 1 000 000 000 руб.")
                    return
                
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную цену")
                return
            
            # Создаем заявку с привязкой к CarID
            success = self.db.add_purchase_request(
                self.current_user[0],  # ClientID
                car_data[0],           # CarID (ID автомобиля)
                car_data[1],           # Brand
                car_data[2],           # Model
                max_price
            )
            
            if success:
                messagebox.showinfo("Успех", "Заявка успешно подана!")
                window.destroy()
                self.show_purchase_requests()
            else:
                messagebox.showerror("Ошибка", "Ошибка при подаче заявки")
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=30)

        # Основная кнопка "Подать заявку"
        submit_button = ttk.Button(button_frame, text="Подтвердить заявку", 
                                   command=submit_request)
        submit_button.pack(side='left', padx=5)
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Отмена", 
            command=window.destroy,
            width=15
        )
        cancel_button.pack(side='left', padx=10)

        price_entry.focus_set()
    
    def show_create_sale(self):
        """Окно оформления продажи для администратора/менеджера"""
        window = tk.Toplevel(self.root)
        window.title("Оформление продажи")
        window.geometry("500x450")
        
        main_frame = ttk.Frame(window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Оформление продажи", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Выбор клиента
        ttk.Label(main_frame, text="Клиент:").pack(anchor='w', pady=5)
        clients = self.db.get_all_clients()
        client_var = tk.StringVar()
        client_combo = ttk.Combobox(main_frame, textvariable=client_var, state="readonly", width=50)
        client_combo['values'] = [f"{client[0]} - {client[1]} {client[2]} ({client[3]})" for client in clients]
        if clients:
            client_combo.current(0)
        client_combo.pack(fill='x', pady=5)
        
        # Выбор автомобиля
        ttk.Label(main_frame, text="Автомобиль:").pack(anchor='w', pady=5)
        available_cars = self.db.get_available_cars()
        car_var = tk.StringVar()
        car_combo = ttk.Combobox(main_frame, textvariable=car_var, state="readonly", width=50)
        car_combo['values'] = [f"{car[0]} - {car[1]} {car[2]} {car[3]}г. ({car[4]}) - {car[5]:,.2f} руб." for car in available_cars]
        if available_cars:
            car_combo.current(0)
        car_combo.pack(fill='x', pady=5)
        
        # Цена продажи
        ttk.Label(main_frame, text="Цена продажи:").pack(anchor='w', pady=5)
        price_entry = ttk.Entry(main_frame, width=30)
        
        # Автозаполнение цены при выборе автомобиля
        def on_car_select(event):
            if car_combo.get():
                try:
                    car_id = int(car_combo.get().split(' - ')[0])
                    car = self.db.get_car_by_id(car_id)
                    if car:
                        price_entry.delete(0, tk.END)
                        price_entry.insert(0, str(car[5]))
                except:
                    pass
        
        car_combo.bind('<<ComboboxSelected>>', on_car_select)
        
        price_entry.pack(fill='x', pady=5)
        
        # Информация о менеджере
        ttk.Label(main_frame, text="Менеджер:").pack(anchor='w', pady=5)
        ttk.Label(main_frame, text=f"{self.current_user[1]} {self.current_user[2]}").pack(anchor='w', pady=5)
        
        def confirm_sale():
            if not client_combo.get():
                messagebox.showerror("Ошибка", "Выберите клиента")
                return
            
            if not car_combo.get():
                messagebox.showerror("Ошибка", "Выберите автомобиль")
                return
            
            try:
                client_id = int(client_combo.get().split(' - ')[0])
                car_id = int(car_combo.get().split(' - ')[0])
                sale_price = float(price_entry.get())
                
                if sale_price <= 0:
                    messagebox.showerror("Ошибка", "Цена должна быть положительным числом")
                    return
                
                success, message = self.db.create_sale_from_selection(client_id, car_id, self.current_user[0], sale_price)
                if success:
                    messagebox.showinfo("Успех", message)
                    window.destroy()
                    self.show_sales()
                else:
                    messagebox.showerror("Ошибка", message)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную цену")
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=30)
        
        ttk.Button(button_frame, text="Подтвердить продажу", 
                  command=confirm_sale).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=window.destroy).pack(side='left', padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = CarDealershipApp(root)
    root.mainloop()