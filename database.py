import pyodbc
import hashlib

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        """Установка соединения с базой данных"""
        connection_strings = [
            'DRIVER={SQL Server};SERVER=localhost;DATABASE=AutoTradeCenter;Trusted_Connection=yes;',
            'DRIVER={SQL Server};SERVER=.;DATABASE=AutoTradeCenter;Trusted_Connection=yes;',
            'DRIVER={SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=AutoTradeCenter;Trusted_Connection=yes;',
            'DRIVER={SQL Server};SERVER=.\\SQLEXPRESS;DATABASE=AutoTradeCenter;Trusted_Connection=yes;',
        ]
        
        for conn_str in connection_strings:
            try:
                self.connection = pyodbc.connect(conn_str)
                print(f"Успешное подключение через: {conn_str}")
                return True
            except Exception as e:
                print(f"Не удалось подключиться через {conn_str}: {e}")
                continue
        
        print("Все попытки подключения не удались")
        return False
    
    def ensure_connection(self):
        """Проверка и восстановление соединения"""
        try:
            if self.connection is None:
                return self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception:
            return self.connect()
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, first_name, last_name, phone, email, username, password, role, position=None):
        """Регистрация пользователя"""
        try:
            if not self.ensure_connection():
                return False, "Нет соединения с базой данных"
            
            cursor = self.connection.cursor()
            password_hash = self.hash_password(password)
            
            if role == 'Client':
                cursor.execute("SELECT ClientID FROM Clients WHERE Username = ?", username)
                if cursor.fetchone():
                    return False, "Логин уже занят"
                
                cursor.execute("""
                    INSERT INTO Clients (FirstName, LastName, Phone, Email, Username, PasswordHash)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, first_name, last_name, phone, email, username, password_hash)
            else:
                cursor.execute("SELECT EmployeeID FROM Employees WHERE Username = ?", username)
                if cursor.fetchone():
                    return False, "Логин уже занят"
                
                cursor.execute("""
                    INSERT INTO Employees (FirstName, LastName, Position, Phone, Email, Username, PasswordHash, Role)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, first_name, last_name, position, phone, email, username, password_hash, role)
            
            self.connection.commit()
            return True, "Регистрация успешна"
        except Exception as e:
            return False, f"Ошибка регистрации: {str(e)}"
    
    def login_user(self, username, password, role):
        """Авторизация пользователя"""
        try:
            if not self.ensure_connection():
                return None
            
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
            
            return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка авторизации: {e}")
            return None
    
    def get_all_cars(self):
        """Получить все автомобили"""
        try:
            if not self.ensure_connection():
                return []
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Cars ORDER BY CarID")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения автомобилей: {e}")
            return []
    
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
    
    def add_car(self, brand, model, year, color, price, status='В наличии'):
        """Добавить автомобиль"""
        try:
            if not self.ensure_connection():
                return False
            
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
            if not self.ensure_connection():
                return False
            
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
            if not self.ensure_connection():
                return False, "Нет соединения с базой данных"
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM Sales WHERE CarID = ?", int(car_id))
            sales_count = cursor.fetchone()[0]
            
            if sales_count > 0:
                return False, "Нельзя удалить автомобиль, так как есть связанные продажи"
            
            cursor.execute("DELETE FROM Cars WHERE CarID=?", int(car_id))
            self.connection.commit()
            return True, "Автомобиль успешно удален"
        except Exception as e:
            return False, f"Ошибка удаления: {str(e)}"
    
    def get_car_by_id(self, car_id):
        """Получить автомобиль по ID"""
        try:
            if not self.ensure_connection():
                return None
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Cars WHERE CarID = ?", int(car_id))
            return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка получения автомобиля: {e}")
            return None
    
    def get_all_clients(self):
        """Получить всех клиентов"""
        try:
            if not self.ensure_connection():
                return []
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT ClientID, FirstName, LastName, Phone, Email, Username FROM Clients ORDER BY ClientID")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения клиентов: {e}")
            return []
    
    def delete_client(self, client_id):
        """Удалить клиента"""
        try:
            if not self.ensure_connection():
                return False, "Нет соединения с базой данных"
            
            cursor = self.connection.cursor()
            
            # Проверяем, нет ли связанных заявок или продаж
            cursor.execute("SELECT COUNT(*) FROM PurchaseRequests WHERE ClientID = ?", int(client_id))
            requests_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Sales WHERE ClientID = ?", int(client_id))
            sales_count = cursor.fetchone()[0]
            
            if requests_count > 0 or sales_count > 0:
                return False, "Нельзя удалить клиента, так как есть связанные заявки или продажи"
            
            cursor.execute("DELETE FROM Clients WHERE ClientID=?", int(client_id))
            self.connection.commit()
            return True, "Клиент успешно удален"
        except Exception as e:
            return False, f"Ошибка удаления: {str(e)}"
    
    def get_all_employees(self):
        """Получить всех сотрудников"""
        try:
            if not self.ensure_connection():
                return []
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT EmployeeID, FirstName, LastName, Position, Phone, Email, Username, Role FROM Employees ORDER BY EmployeeID")
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения сотрудников: {e}")
            return []
    
    def delete_employee(self, employee_id):
        """Удалить сотрудника"""
        try:
            if not self.ensure_connection():
                return False, "Нет соединения с базой данных"
            
            cursor = self.connection.cursor()
            
            # Проверяем, нет ли связанных продаж
            cursor.execute("SELECT COUNT(*) FROM Sales WHERE EmployeeID = ?", int(employee_id))
            sales_count = cursor.fetchone()[0]
            
            if sales_count > 0:
                return False, "Нельзя удалить сотрудника, так как есть связанные продажи. Сначала удалите или перепривяжите продажи."
            
            cursor.execute("DELETE FROM Employees WHERE EmployeeID=?", int(employee_id))
            self.connection.commit()
            return True, "Сотрудник успешно удален"
        except Exception as e:
            return False, f"Ошибка удаления: {str(e)}"
    
    def get_all_sales(self):
        """Получить все продажи с именами клиентов и автомобилей"""
        try:
            if not self.ensure_connection():
                return []
            
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT s.SaleID, c.Brand, c.Model, c.Year, c.Color,
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
            if not self.ensure_connection():
                return False, "Нет соединения с базой данных"
            
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO Sales (CarID, ClientID, EmployeeID, SalePrice)
                VALUES (?, ?, ?, ?)
            """, int(car_id), int(client_id), int(employee_id), float(sale_price))
            
            cursor.execute("UPDATE Cars SET Status='Продано' WHERE CarID=?", int(car_id))
            
            self.connection.commit()
            return True, "Продажа успешно оформлена"
        except Exception as e:
            return False, f"Ошибка оформления продажи: {str(e)}"
    
    def get_all_purchase_requests(self, client_id=None):
        """Получить все заявки на покупку"""
        try:
            if not self.ensure_connection():
                return []
            
            cursor = self.connection.cursor()
            
            if client_id:
                cursor.execute("""
                    SELECT pr.RequestID, 
                        cl.FirstName + ' ' + cl.LastName as ClientName,
                        pr.Brand, pr.Model, pr.MaxPrice, pr.RequestDate, pr.Status
                    FROM PurchaseRequests pr
                    JOIN Clients cl ON pr.ClientID = cl.ClientID
                    WHERE pr.ClientID = ?
                    ORDER BY pr.RequestID
                """, int(client_id))
            else:
                cursor.execute("""
                    SELECT pr.RequestID, 
                        cl.FirstName + ' ' + cl.LastName as ClientName,
                        pr.Brand, pr.Model, pr.MaxPrice, pr.RequestDate, pr.Status
                    FROM PurchaseRequests pr
                    JOIN Clients cl ON pr.ClientID = cl.ClientID
                    ORDER BY pr.RequestID
                """)
            
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения заявок: {e}")
            return []
    
    def get_purchase_request_by_id(self, request_id):
        """Получить заявку по ID"""
        try:
            if not self.ensure_connection():
                return None
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM PurchaseRequests WHERE RequestID = ?", int(request_id))
            return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка получения заявки: {e}")
            return None
    
    def get_available_cars_by_model(self, brand, model):
        """Получить доступные автомобили по марке и модели"""
        try:
            if not self.ensure_connection():
                return []
            
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT CarID, Brand, Model, Year, Color, Price 
                FROM Cars 
                WHERE Status = 'В наличии' AND Brand = ? AND Model = ?
                ORDER BY Year DESC
            """, brand, model)
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения автомобилей по модели: {e}")
            return []
    
    def add_purchase_request(self, client_id, car_id, brand, model, max_price):
        """Добавить заявку на покупку"""
        try:
            if not self.ensure_connection():
                return False
            
            cursor = self.connection.cursor()
            price_value = float(max_price) if max_price and max_price > 0 else None
                
            cursor.execute("""
                INSERT INTO PurchaseRequests (ClientID, CarID, Brand, Model, MaxPrice, Status)
                VALUES (?, ?, ?, ?, ?, 'Рассматривается')
            """, int(client_id), int(car_id), brand, model, price_value)
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления заявки: {e}")
            return False
    
    def delete_purchase_request(self, request_id):
        """Удалить заявку на покупку"""
        try:
            if not self.ensure_connection():
                return False, "Нет соединения с базой данных"
            
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM PurchaseRequests WHERE RequestID=?", int(request_id))
            self.connection.commit()
            return True, "Заявка успешно удалена"
        except Exception as e:
            return False, f"Ошибка удаления: {str(e)}"
    
    def get_client_sales(self, client_id):
        """Получить продажи конкретного клиента"""
        try:
            if not self.ensure_connection():
                return []
            
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT s.SaleID, c.Brand, c.Model, c.Year, c.Color,
                    e.FirstName + ' ' + e.LastName as EmployeeName,
                    s.SaleDate, s.SalePrice
                FROM Sales s
                JOIN Cars c ON s.CarID = c.CarID
                JOIN Employees e ON s.EmployeeID = e.EmployeeID
                WHERE s.ClientID = ?
                ORDER BY s.SaleDate DESC
            """, int(client_id))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения продаж клиента: {e}")
            return []
    
    def create_sale_from_selection(self, client_id, car_id, employee_id, sale_price):
        """Создать продажу из выбранных клиента и автомобиля"""
        try:
            if not self.ensure_connection():
                return False, "Нет соединения с базой данных"
            
            cursor = self.connection.cursor()
            
            # Проверяем, доступен ли автомобиль
            cursor.execute("SELECT Status FROM Cars WHERE CarID = ?", int(car_id))
            car = cursor.fetchone()
            
            if not car:
                return False, "Автомобиль не найден"
            
            if car[0] != 'В наличии':
                return False, "Автомобиль уже продан или недоступен"
            
            # Создаем продажу
            cursor.execute("""
                INSERT INTO Sales (CarID, ClientID, EmployeeID, SalePrice)
                VALUES (?, ?, ?, ?)
            """, int(car_id), int(client_id), int(employee_id), float(sale_price))
            
            # Обновляем статус автомобиля
            cursor.execute("UPDATE Cars SET Status='Продано' WHERE CarID=?", int(car_id))
            
            self.connection.commit()
            return True, "Продажа успешно оформлена"
        except Exception as e:
            return False, f"Ошибка оформления продажи: {str(e)}"