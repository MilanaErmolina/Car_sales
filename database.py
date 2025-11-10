import pyodbc
import hashlib
from datetime import datetime

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        try:
            self.connection = pyodbc.connect(
                'DRIVER={SQL Server};'
                'SERVER=localhost;'
                'DATABASE=AutoTradeCenter;'
                'Trusted_Connection=yes;'
            )
            print("Успешное подключение к базе данных")
        except Exception as e:
            print(f"Ошибка подключения: {e}")
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, first_name, last_name, phone, email, username, password, role, position=None):
        """Регистрация пользователя (клиента или сотрудника)"""
        try:
            cursor = self.connection.cursor()
            password_hash = self.hash_password(password)
            
            # Проверяем, не занят ли логин
            if role == 'Client':
                cursor.execute("SELECT ClientID FROM Clients WHERE Username = ?", username)
            else:
                cursor.execute("SELECT EmployeeID FROM Employees WHERE Username = ?", username)
            
            if cursor.fetchone():
                return False, "Логин уже занят"
            
            if role == 'Client':
                cursor.execute("""
                    INSERT INTO Clients (FirstName, LastName, Phone, Email, Username, PasswordHash)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, first_name, last_name, phone, email, username, password_hash)
            else:
                cursor.execute("""
                    INSERT INTO Employees (FirstName, LastName, Position, Phone, Email, Username, PasswordHash, Role)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, first_name, last_name, position, phone, email, username, password_hash, role)
            
            self.connection.commit()
            return True, "Регистрация успешна"
        except Exception as e:
            print(f"Ошибка регистрации: {e}")
            return False, f"Ошибка регистрации: {str(e)}"
    
    def login_user(self, username, password, role):
        """Авторизация пользователя"""
        try:
            cursor = self.connection.cursor()
            password_hash = self.hash_password(password)
            
            if role == 'Client':
                cursor.execute("""
                    SELECT ClientID, FirstName, LastName FROM Clients 
                    WHERE Username = ? AND PasswordHash = ?
                """, username, password_hash)
            else:
                cursor.execute("""
                    SELECT EmployeeID, FirstName, LastName, Role FROM Employees 
                    WHERE Username = ? AND PasswordHash = ?
                """, username, password_hash)
            
            user = cursor.fetchone()
            return user if user else None
        except Exception as e:
            print(f"Ошибка авторизации: {e}")
            return None
    
    # Методы для работы с автомобилями
    def get_all_cars(self):
        """Получить все автомобили"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Cars ORDER BY CarID")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения автомобилей: {e}")
            return []
    
    def add_car(self, brand, model, year, color, price, status='В наличии'):
        """Добавить автомобиль"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO Cars (Brand, Model, Year, Color, Price, Status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, brand, model, int(year), color, float(price), status)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления автомобиля: {e}")
            return False
    
    def update_car(self, car_id, brand, model, year, color, price, status):
        """Обновить автомобиль"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE Cars SET Brand=?, Model=?, Year=?, Color=?, Price=?, Status=?
                WHERE CarID=?
            """, brand, model, int(year), color, float(price), status, int(car_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления автомобиля: {e}")
            return False
    
    def delete_car(self, car_id):
        """Удалить автомобиль"""
        try:
            cursor = self.connection.cursor()
            
            # Проверяем, нет ли связанных продаж
            cursor.execute("SELECT COUNT(*) FROM Sales WHERE CarID = ?", int(car_id))
            sales_count = cursor.fetchone()[0]
            
            if sales_count > 0:
                return False, "Нельзя удалить автомобиль, так как есть связанные продажи"
            
            cursor.execute("DELETE FROM Cars WHERE CarID=?", int(car_id))
            self.connection.commit()
            return True, "Автомобиль успешно удален"
        except Exception as e:
            print(f"Ошибка удаления автомобиля: {e}")
            return False, f"Ошибка удаления: {str(e)}"
    
    def get_car_by_id(self, car_id):
        """Получить автомобиль по ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Cars WHERE CarID = ?", int(car_id))
            return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка получения автомобиля: {e}")
            return None
    
    def get_available_cars(self):
        """Получить автомобили в наличии"""
        try:
            if not self.ensure_connection():
                return []
            
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT CarID, Brand, Model, Year, Color, Price 
                FROM Cars 
                WHERE Status = 'В наличии'
                ORDER BY Brand, Model
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения доступных автомобилей: {e}")
            return []

    # Методы для работы с клиентами
    def get_all_clients(self):
        """Получить всех клиентов"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ClientID, FirstName, LastName, Phone, Email, Username FROM Clients ORDER BY ClientID")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения клиентов: {e}")
            return []
    
    # Методы для работы с сотрудниками
    def get_all_employees(self):
        """Получить всех сотрудников"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT EmployeeID, FirstName, LastName, Position, Phone, Email, Username, Role FROM Employees ORDER BY EmployeeID")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения сотрудников: {e}")
            return []
    
    # Методы для работы с продажами
    def get_all_sales(self):
        """Получить все продажи"""
        try:
            if not self.ensure_connection():
                return []
            
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT s.SaleID, c.Brand, c.Model, 
                    cl.FirstName + ' ' + cl.LastName as ClientName,
                    e.FirstName + ' ' + e.LastName as EmployeeName,
                    s.SaleDate, s.SalePrice
                FROM Sales s
                JOIN Cars c ON s.CarID = c.CarID
                JOIN Clients cl ON s.ClientID = cl.ClientID
                JOIN Employees e ON s.EmployeeID = e.EmployeeID
                ORDER BY s.SaleID
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения продаж: {e}")
            return []
    
    def add_sale(self, car_id, client_id, employee_id, sale_price):
        """Добавить продажу"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO Sales (CarID, ClientID, EmployeeID, SalePrice)
                VALUES (?, ?, ?, ?)
            """, int(car_id), int(client_id), int(employee_id), float(sale_price))
            
            # Обновляем статус автомобиля
            cursor.execute("UPDATE Cars SET Status='Продано' WHERE CarID=?", int(car_id))
            
            self.connection.commit()
            return True, "Продажа успешно оформлена"
        except Exception as e:
            print(f"Ошибка добавления продажи: {e}")
            return False, f"Ошибка оформления продажи: {str(e)}"
    
    # Методы для работы с заявками на покупку
    def get_all_purchase_requests(self, client_id=None):
        """Получить все заявки на покупку (если указан client_id - только его заявки)"""
        try:
            if not self.ensure_connection():
                return []
            
            cursor = self.connection.cursor()
            
            if client_id:
                # Только заявки конкретного клиента
                cursor.execute("""
                    SELECT pr.RequestID, cl.FirstName + ' ' + cl.LastName as ClientName, 
                        pr.Brand, pr.Model, pr.MaxPrice, pr.RequestDate, pr.Status
                    FROM PurchaseRequests pr
                    JOIN Clients cl ON pr.ClientID = cl.ClientID
                    WHERE pr.ClientID = ?
                    ORDER BY pr.RequestID
                """, int(client_id))
            else:
                # Все заявки (для сотрудников)
                cursor.execute("""
                    SELECT pr.RequestID, cl.FirstName + ' ' + cl.LastName as ClientName, 
                        pr.Brand, pr.Model, pr.MaxPrice, pr.RequestDate, pr.Status
                    FROM PurchaseRequests pr
                    JOIN Clients cl ON pr.ClientID = cl.ClientID
                    ORDER BY pr.RequestID
                """)
            
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения заявок: {e}")
            return []
    
    def add_purchase_request(self, client_id, brand, model, max_price):
        """Добавить заявку на покупку"""
        try:
            if not self.ensure_connection():
                return False
            
            cursor = self.connection.cursor()
            
            # Если цена не указана, устанавливаем NULL
            price_value = float(max_price) if max_price and max_price > 0 else None
            
            cursor.execute("""
                INSERT INTO PurchaseRequests (ClientID, Brand, Model, MaxPrice)
                VALUES (?, ?, ?, ?)
            """, int(client_id), brand, model, price_value)
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления заявки: {e}")
            return False