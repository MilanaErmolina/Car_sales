import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class CarDealershipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автосалон - Система управления")
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
                                 values=["Client", "Admin", "Manager", "Consultant", "Accountant"],
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
                                 values=["Client", "Admin", "Manager", "Consultant", "Accountant"],
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
        
        # обновлено
        
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

        # до этого момента обновлено

        if self.db.register_user(data['first_name'], data['last_name'], data['phone'], 
                               data['email'], data['username'], data['password'], 
                               role, position):
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            self.show_login_screen()
        else:
            messagebox.showerror("Ошибка", "Ошибка регистрации. Возможно, логин уже занят.")
    

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
            client_menu.add_separator()
            client_menu.add_command(label="Выйти", command=self.logout)
        else:
            admin_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Меню", menu=admin_menu)
            admin_menu.add_command(label="Автомобили", command=self.show_cars)
            admin_menu.add_command(label="Клиенты", command=self.show_clients)
            admin_menu.add_command(label="Сотрудники", command=self.show_employees)
            admin_menu.add_command(label="Продажи", command=self.show_sales)
            admin_menu.add_command(label="Заявки", command=self.show_purchase_requests)
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
    
    def show_cars(self):
        """Показать список автомобилей"""
        self.clear_content()
        
        # Заголовок
        ttk.Label(self.root, text="Автомобили в наличии", font=('Arial', 16)).pack(pady=10)
        
        # Кнопки для администраторов
        if self.user_role != "Client":
            button_frame = ttk.Frame(self.root)
            button_frame.pack(pady=10)
            
            ttk.Button(button_frame, text="Добавить автомобиль", 
                      command=self.show_add_car).pack(side='left', padx=5)
        
        # Таблица автомобилей
        columns = ("ID", "Марка", "Модель", "Год", "Цвет", "Цена", "Статус")
        tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Заполнение данными
        cars = self.db.get_all_cars()
        for car in cars:
            tree.insert("", "end", values=car)
        
        tree.pack(pady=10, fill='both', expand=True)
        
        # Кнопки управления для администраторов
        if self.user_role != "Client":
            control_frame = ttk.Frame(self.root)
            control_frame.pack(pady=10)
            
            ttk.Button(control_frame, text="Редактировать", 
                      command=lambda: self.edit_car(tree)).pack(side='left', padx=5)
            ttk.Button(control_frame, text="Удалить", 
                      command=lambda: self.delete_car(tree)).pack(side='left', padx=5)
            if self.user_role in ["Admin", "Manager"]:
                ttk.Button(control_frame, text="Продать автомобиль", 
                          command=lambda: self.sell_car(tree)).pack(side='left', padx=5)
    
    def show_add_car(self):
        """Окно добавления автомобиля"""
        self.add_edit_car_window()
    
    def add_edit_car_window(self, car_data=None):
        """Окно добавления/редактирования автомобиля"""
        window = tk.Toplevel(self.root)
        window.title("Добавить автомобиль" if not car_data else "Редактировать автомобиль")
        window.geometry("400x300")

        form_frame = ttk.Frame(window, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        ttk.Label(window, text="Марка:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        brand_entry = ttk.Entry(window, width=30)
        brand_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(window, text="Модель:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        model_entry = ttk.Entry(window, width=30)
        model_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(window, text="Год:").grid(row=2, column=0, sticky='w', pady=5, padx=5)
        year_entry = ttk.Entry(window, width=30)
        year_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(window, text="Цвет:").grid(row=3, column=0, sticky='w', pady=5, padx=5)
        color_entry = ttk.Entry(window, width=30)
        color_entry.grid(row=3, column=1, pady=5, padx=5)
        
        ttk.Label(window, text="Цена:").grid(row=4, column=0, sticky='w', pady=5, padx=5)
        price_entry = ttk.Entry(window, width=30)
        price_entry.grid(row=4, column=1, pady=5, padx=5)
        
        ttk.Label(window, text="Статус:").grid(row=5, column=0, sticky='w', pady=5, padx=5)
        status_combo = ttk.Combobox(window, values=["В наличии", "Продано", "На ремонте"], state="readonly")
        status_combo.set("В наличии")
        status_combo.grid(row=5, column=1, pady=5, padx=5)
        
        # Заполнение данных при редактировании
        if car_data:
            brand_entry.insert(0, car_data[1])
            model_entry.insert(0, car_data[2])
            year_entry.insert(0, car_data[3])
            color_entry.insert(0, car_data[4])
            price_entry.insert(0, car_data[5])
            status_combo.set(car_data[6])
        
        def save_car():
            if not all([brand_entry.get(), model_entry.get(), year_entry.get(), price_entry.get()]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
        
            try:
                year = int(year_entry.get())
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Год и цена должны быть числами")
                return
        
            if self.db.add_car(brand_entry.get(), model_entry.get(), year_entry.get(),
                             color_entry.get(), price_entry.get(), status_combo.get()):
                messagebox.showinfo("Успех", "Автомобиль добавлен!")
                window.destroy()
                self.show_cars()
            else:
                messagebox.showerror("Ошибка", "Ошибка при добавлении автомобиля")
        
        def update_car():
            if not all([brand_entry.get(), model_entry.get(), year_entry.get(), price_entry.get()]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
        
            try:
                year = int(year_entry.get())
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Год и цена должны быть числами")
                return

            if self.db.update_car(car_data[0], brand_entry.get(), model_entry.get(), year_entry.get(),
                                color_entry.get(), price_entry.get(), status_combo.get()):
                messagebox.showinfo("Успех", "Автомобиль обновлен!")
                window.destroy()
                self.show_cars()
            else:
                messagebox.showerror("Ошибка", "Ошибка при обновлении автомобиля")
        
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
            if self.db.delete_car(car_data[0]):
                messagebox.showinfo("Успех", "Автомобиль удален!")
                self.show_cars()
            else:
                messagebox.showerror("Ошибка", "Ошибка при удалении автомобиля")
    
    def sell_car(self, tree):
        """Продажа автомобиля"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите автомобиль для продажи")
            return
        
        car_data = tree.item(selected[0])['values']

        if car_data[6] == "Продано":
            messagebox.showwarning("Предупреждение", "Этот автомобиль уже продан")
            return
        
        self.show_sell_car_window(car_data)
    
    def show_sell_car_window(self, car_data):
        """Окно продажи автомобиля"""
        window = tk.Toplevel(self.root)
        window.title("Продажа автомобиля")
        window.geometry("400x300")

        # Основной фрейм
        main_frame = ttk.Frame(window, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Информация об автомобиле
        ttk.Label(main_frame, text=f"Продажа автомобиля:", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        ttk.Label(main_frame, text=f"{car_data[1]} {car_data[2]}", font=('Arial', 11)).grid(row=1, column=0, columnspan=2, pady=5, sticky='w')
        ttk.Label(main_frame, text=f"Год: {car_data[3]}, Цвет: {car_data[4]}").grid(row=2, column=0, columnspan=2, pady=2, sticky='w')
        ttk.Label(main_frame, text=f"Цена в каталоге: {car_data[5]:,.2f} руб.").grid(row=3, column=0, columnspan=2, pady=2, sticky='w')
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, pady=10, sticky='ew')
        
        ttk.Label(window, text=f"Продажа: {car_data[1]} {car_data[2]}").pack(pady=10)
        
        # Выбор клиента
        ttk.Label(main_frame, text="Выберите клиента:").grid(row=5, column=0, sticky='w', pady=5)
        clients = self.db.get_all_clients()
        client_var = tk.StringVar()
        client_combo = ttk.Combobox(main_frame, textvariable=client_var, state="readonly", width=30)
        client_combo['values'] = [f"{client[0]} - {client[1]} {client[2]} ({client[3]})" for client in clients]
        if clients:
            client_combo.current(0)
        client_combo.grid(row=5, column=1, pady=5, padx=5, sticky='ew')
            
       # Цена продажи
        ttk.Label(main_frame, text="Цена продажи:").grid(row=6, column=0, sticky='w', pady=5)
        price_entry = ttk.Entry(main_frame, width=30)
        price_entry.insert(0, str(car_data[5]))
        price_entry.grid(row=6, column=1, pady=5, padx=5, sticky='ew')
        
        # Информация о сотруднике
        ttk.Label(main_frame, text="Продавец:").grid(row=7, column=0, sticky='w', pady=5)
        ttk.Label(main_frame, text=f"{self.current_user[1]} {self.current_user[2]}").grid(row=7, column=1, sticky='w', pady=5)
            
        def confirm_sale():
            if not client_combo.get():
                messagebox.showerror("Ошибка", "Выберите клиента")
                return
            
            try:
                client_id = int(client_combo.get().split(' - ')[0])
                sale_price = float(price_entry.get())
                
                if sale_price <= 0:
                    messagebox.showerror("Ошибка", "Цена должна быть положительным числом")
                    return
                
                success, message = self.db.add_sale(car_data[0], client_id, self.current_user[0], sale_price)
                if success:
                    messagebox.showinfo("Успех", message)
                    window.destroy()
                    self.show_cars()
                else:
                    messagebox.showerror("Ошибка", message)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную цену")

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Подтвердить продажу", 
                command=confirm_sale, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена", 
                command=window.destroy).pack(side='left', padx=5)
        
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
    
    def show_sales(self):
        """Показать список продаж"""
        self.clear_content()
        
        ttk.Label(self.root, text="Продажи", font=('Arial', 16)).pack(pady=10)
        
        columns = ("ID", "Марка", "Модель", "Клиент", "Сотрудник", "Дата", "Цена")
        tree = ttk.Treeview(self.root, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        sales = self.db.get_all_sales()
        for sale in sales:
            tree.insert("", "end", values=sale)
        
        tree.pack(pady=10, fill='both', expand=True)
    
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
            ttk.Button(button_frame, text="Добавить заявку", 
                    command=self.show_add_request).pack(side='left', padx=5)
        
        # Получаем заявки в зависимости от роли
        if self.user_role == "Client":
            requests = self.db.get_all_purchase_requests(self.current_user[0])  # Только свои заявки
        else:
            requests = self.db.get_all_purchase_requests()  # Все заявки
        
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
            # Форматируем цену
            max_price = f"{req[4]:,.2f} руб." if req[4] else "Не указана"
            # Форматируем дату
            request_date = req[5].strftime("%d.%m.%Y") if req[5] else ""
            
            tree.insert("", "end", values=(
                req[0],  # ID
                req[1],  # Клиент (уже объединенное имя)
                req[2],  # Марка
                req[3],  # Модель
                max_price,
                request_date,
                req[6]   # Статус
            ))
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(pady=10, fill='both', expand=True, padx=10)
        scrollbar.pack(side='right', fill='y', padx=(0, 10), pady=10)
        
    def show_add_request(self):
        """Окно добавления заявки на покупку"""
        window = tk.Toplevel(self.root)
        window.title("Новая заявка на покупку")
        window.geometry("400x300")
        
        main_frame = ttk.Frame(window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Марка автомобиля:").grid(row=0, column=0, sticky='w', pady=5)
        brand_entry = ttk.Entry(main_frame, width=30)
        brand_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Модель автомобиля:").grid(row=1, column=0, sticky='w', pady=5)
        model_entry = ttk.Entry(main_frame, width=30)
        model_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Максимальная цена:").grid(row=2, column=0, sticky='w', pady=5)
        price_entry = ttk.Entry(main_frame, width=30)
        price_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Если это сотрудник, показываем выбор клиента
        client_id = None
        if self.user_role != "Client":
            ttk.Label(main_frame, text="Клиент:").grid(row=3, column=0, sticky='w', pady=5)
            clients = self.db.get_all_clients()
            client_var = tk.StringVar()
            client_combo = ttk.Combobox(main_frame, textvariable=client_var, state="readonly", width=28)
            client_combo['values'] = [f"{client[0]} - {client[1]} {client[2]}" for client in clients]
            if clients:
                client_combo.current(0)
            client_combo.grid(row=3, column=1, pady=5, padx=5)
        else:
            # Для клиента используем его собственный ID
            client_id = self.current_user[0]
        
        def save_request():
            if self.user_role != "Client":
                if not client_combo.get():
                    messagebox.showerror("Ошибка", "Выберите клиента")
                    return
                client_id = int(client_combo.get().split(' - ')[0])
            
            if not brand_entry.get() or not model_entry.get():
                messagebox.showerror("Ошибка", "Заполните марку и модель автомобиля")
                return
            
            try:
                max_price = float(price_entry.get()) if price_entry.get() else 0
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную цену")
                return
            
            if self.db.add_purchase_request(client_id, brand_entry.get(), model_entry.get(), max_price):
                messagebox.showinfo("Успех", "Заявка добавлена!")
                window.destroy()
                self.show_purchase_requests()
            else:
                messagebox.showerror("Ошибка", "Ошибка при добавлении заявки")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Сохранить", command=save_request).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена", command=window.destroy).pack(side='left', padx=5)
        
    def clear_content(self):
        """Очистка основного контента"""
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CarDealershipApp(root)
    root.mainloop()