import csv
import pickle
import json
import os
import sys

# ==========================================
# СУТНОСТІ ТА КЛАС-МЕНЕДЖЕР З МИНУЛИХ РОБІТ
# ==========================================
class Category:
    FOOD = "FOOD"
    TRANSPORT = "TRANSPORT"
    SALARY = "SALARY"
    ENTERTAINMENT = "ENTERTAINMENT"

class Transaction:
    def __init__(self, category: str, amount: float):
        if amount <= 0:
            raise ValueError("Сума транзакції повинна бути більшою за нуль!")
        self.category = category
        self._amount = amount

    @property
    def amount(self) -> float:
        return self._amount

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return self.amount + other
        return self.amount + other.amount

    def __radd__(self, other):
        return self.__add__(other)

class Income(Transaction):
    def __str__(self) -> str:
        return f"Income('{self.category}', amount={self.amount})"

class Expense(Transaction):
    def __str__(self) -> str:
        return f"Expense('{self.category}', amount={self.amount})"

class FinanceAnalytics:
    def __init__(self):
        self.total_analyzed_amount = 0.0
        self.call_count = 0

    def __call__(self, transaction: Transaction) -> float:
        self.call_count += 1
        self.total_analyzed_amount += transaction.amount
        if isinstance(transaction, Expense):
            return round(transaction.amount * 0.015, 2)  # 1.5% комісія на витрати
        return 0.0

class Wallet:
    def __init__(self, initial_balance: float = 10000.0):
        self.balance = initial_balance
        self.transactions = []
        self.analyzer = FinanceAnalytics()
        self.company_name = "Nexus Dev Financial"
        self.page_size = 3

    def load_config(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                config = json.load(file)
                self.company_name = config.get("company_name", "Nexus Dev Financial")
                self.page_size = config.get("page_size", 3)
        except FileNotFoundError:
            pass

    def generate_statement_pages(self):
        for i in range(0, len(self.transactions), self.page_size):
            yield self.transactions[i:i + self.page_size]

    def save_system_state(self, file_path: str = "wallet_backup.bin"):
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)
        print(f"[System] Базу даних успішно збережено в '{file_path}'.")

    def load_system_state(self, file_path: str = "wallet_backup.bin"):
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                loaded = pickle.load(f)
                self.balance = loaded.balance
                self.transactions = loaded.transactions
                self.analyzer = loaded.analyzer
            print(f"[System] Базу даних успішно відновлено.")
        else:
            print(f"[Info] Файл бекапу не знайдено. Початок роботи з чистим гаманцем.")

    def export_sales_report(self, file_path: str = "transactions_report.csv"):
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(["Тип Транзакції", "Категорія", "Сума (UAH)"])
            for tx in self.transactions:
                tx_type = "Дохід" if isinstance(tx, Income) else "Витрата"
                writer.writerow([tx_type, tx.category, tx.amount])
        print(f"[System] Звіт CSV успішно згенеровано у файлі '{file_path}'.")

    def add_transaction(self, tx_type: str, category: str, amount: float):
        if tx_type == "1":
            new_tx = Income(category, amount)
            self.balance += new_tx.amount
        else:
            new_tx = Expense(category, amount)
            fee = self.analyzer(new_tx)
            total_deduction = new_tx.amount + fee
            if self.balance < total_deduction:
                raise ValueError(f"Недостатньо коштів! Необхідно {total_deduction} UAH (включаючи комісію 1.5%).")
            self.balance -= total_deduction
        
        self.transactions.append(new_tx)
        print(f"[Success] Транзакція на '{category}' успішно додана!")

    def display_all(self):
        if not self.transactions:
            print("[Info] База транзакцій порожня.")
            return
        
        print("\n--- Список усіх транзакцій (Посторінково) ---")
        page_gen = self.generate_statement_pages()
        page_num = 1
        for page in page_gen:
            print(f"Сторінка №{page_num}:")
            for tx in page:
                print(f"  - {tx}")
            page_num += 1


# ==========================================
# ІНТЕРФЕЙС КОРИСТУВАЧА
# ==========================================
def show_menu():
    print("\n" + "="*30)
    print("      ГОЛОВНЕ МЕНЮ СИСТЕМИ")
    print("="*30)
    print("1. Показати всі транзакції")
    print("2. Додати (провести) нову транзакцію")
    print("3. Зберегти стан системи")
    print("4. Експортувати звіт у CSV")
    print("0. Вихід із програми")
    print("="*30)


if __name__ == "__main__":
    manager = Wallet()
    
    # Ініціалізація системи при старті
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    manager.load_config(config_path)
    manager.load_system_state()
    
    print(f"\nЛаскаво просимо до {manager.company_name} System v1.0")
    
    # Головний життєвий цикл консольного інтерфейсу
    while True:
        # Обгортка всього циклу меню для перехоплення помилок за твоїм зразком
        try:
            show_menu()
            print(f"Поточний баланс: {manager.balance} UAH")
            choice = input("Оберіть дію: ").strip()
            
            match choice:
                case "1":
                    manager.display_all()
                    
                case "2":
                    tx_type = input("Введіть тип (1 - Дохід, 2 - Витрата): ").strip()
                    if tx_type not in ["1", "2"]:
                        raise ValueError("Некоректний вибір типу операції! Має бути 1 або 2.")
                        
                    print("Доступні категорії: FOOD, TRANSPORT, SALARY, ENTERTAINMENT")
                    category = input("Введіть назву категорії: ").strip().upper()
                    if not category:
                        raise ValueError("Назва категорії не може бути порожньою!")
                        
                    price_input = input("Введіть суму транзакції: ").strip()
                    # Спроба конвертації. Якщо користувач введе букви, Python сам викине ValueError
                    price = float(price_input) 
                    
                    manager.add_transaction(tx_type, category, price)
                    
                case "3":
                    manager.save_system_state()
                    
                case "4":
                    manager.export_sales_report()
                    
                case "0":
                    print("\n[Завершення роботи]. Дякуємо, що користувалися нашою системою!")
                    print("# Гарантоване збереження перед виходом")
                    manager.save_system_state()
                    sys.exit(0)
                    
                case _:
                    print(f"[Warning] Невідома команда! Будь ласка, оберіть пункт від 0 до 4.")
        
        # Твої блоки перехоплення помилок в самому кінці циклу:
        except ValueError as e:
            print(f"\nПомилка введення: {e}")
            print("Перевірте правильність введених даних.")
            
        except IndexError as e:
            print(f"\nПомилка індексу: {e}")
            
        except Exception as e:
            print(f"\nНесподівана помилка: {e}")