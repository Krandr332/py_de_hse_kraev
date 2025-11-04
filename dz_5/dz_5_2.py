import datetime
import time
import json
import pandas as pd
from dz_5_1 import Account


class CheckingAccount(Account):
    """Расчётный счёт"""

    def __init__(self, account_holder, balance=0):
        super().__init__(account_holder, balance)
        self.account_type = "Checking"

    def clean_history(self, transaction):
        """Очистка и валидация данных транзакции для CheckingAccount"""
        valid_operations = ['deposit', 'withdraw']
        if transaction.get('operation') not in valid_operations:
            return False

        amount = transaction.get('amount')
        if amount is None or amount <= 0:
            return False

        date_str = transaction.get('date')
        if not self._is_valid_date(date_str):
            return False

        if transaction.get('status') != 'success':
            return False

        return True

    def _is_valid_date(self, date_str):
        """Проверка валидности даты"""
        try:
            formats = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M']
            for fmt in formats:
                try:
                    datetime.datetime.strptime(date_str, fmt)
                    return True
                except ValueError:
                    continue
            return False
        except:
            return False

    def load_from_file(self, filename):
        """Загрузка истории операций из файла"""
        if filename.endswith('.csv'):
            self._load_from_csv(filename)
        elif filename.endswith('.json'):
            self._load_from_json(filename)
        else:
            raise ValueError("Поддерживаются только CSV и JSON файлы")

    def _load_from_csv(self, filename):
        """Загрузка из CSV файла"""
        try:
            df = pd.read_csv(filename)
            self._process_transactions(df.to_dict('records'))
        except Exception as e:
            print(f"Ошибка загрузки CSV: {e}")

    def _load_from_json(self, filename):
        """Загрузка из JSON файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._process_transactions(data)
        except Exception as e:
            print(f"Ошибка загрузки JSON: {e}")

    def _process_transactions(self, transactions):
        """Обработка транзакций"""
        valid_transactions = []
        
        for transaction in transactions:
            if transaction.get('account_number') == self.account_number:
                if self.clean_history(transaction):
                    valid_transactions.append(transaction)
        
        valid_transactions.sort(key=lambda x: self._parse_date(x['date']))
        
        for transaction in valid_transactions:
            amount = transaction['amount']
            operation = transaction['operation']
            
            if operation == 'deposit':
                self._balance += amount
            elif operation == 'withdraw':
                self._balance -= amount
            
            self.operations_history.append({
                'type': 'Пополнение счета' if operation == 'deposit' else 'Снятие средств',
                'amount': amount,
                'datetime': self._parse_date(transaction['date']),
                'balance_after': self._balance,
                'status': 'success',
                'source': 'file_import'
            })

    def _parse_date(self, date_str):
        """Парсинг даты из строки"""
        formats = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M']
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return datetime.datetime.now()


class SavingsAccount(Account):
    """Сберегательный счёт"""

    def __init__(self, account_holder, balance=0):
        super().__init__(account_holder, balance)
        self.account_type = "Savings"

    def apply_interest(self, rate: float):
        """Начисление процентов на остаток"""
        if rate <= 0:
            raise ValueError("Процентная ставка должна быть положительной")

        interest = self._balance * (rate / 100)
        self._balance += interest

        self.operations_history.append({
            'type': 'interest',
            'amount': interest,
            'datetime': datetime.datetime.now(),
            'balance_after': self._balance,
            'status': 'success'
        })

    def withdraw(self, amount: float):
        """Снятие средств с ограничением: не более 50% от баланса"""
        try:
            self._validation_amount(amount)

            if amount > self._balance * 0.5:
                raise ValueError("Нельзя снять более 50% от текущего баланса")

            if amount <= self._balance:
                self._balance -= amount
                self.operations_history.append({
                    'type': 'Снятие средств',
                    'amount': amount,
                    'datetime': datetime.datetime.now(),
                    'balance_after': self._balance,
                    'status': 'success'
                })
            else:
                raise ValueError("На счете недостаточно средств")

        except ValueError as e:
            self.operations_history.append({
                'type': 'Снятие средств',
                'amount': amount,
                'datetime': datetime.datetime.now(),
                'balance_after': self._balance,
                'status': 'failed',
                'error': str(e)
            })

    def get_large_operations(self, n: int = 5):
        """Возвращает последние n крупных операций"""
        successful_operations = [op for op in self.operations_history
                                 if op['status'] == 'success' and op['type'] in ['Пополнение счета', 'Снятие средств', 'interest']]

        large_ops = sorted(successful_operations,
                           key=lambda x: x['amount'],
                           reverse=True)[:n]

        large_ops_sorted = sorted(large_ops,
                                  key=lambda x: x['datetime'],
                                  reverse=True)

        return large_ops_sorted

    def clean_history(self, transaction):
        """Очистка и валидация данных транзакции для SavingsAccount"""

        valid_operations = ['deposit', 'withdraw', 'interest']
        operation = transaction.get('operation')
        
        if operation == 'diposit':
            operation = 'deposit'
            transaction['operation'] = 'deposit'
        elif operation == 'wdraw':
            operation = 'withdraw'
            transaction['operation'] = 'withdraw'
        
        if operation not in valid_operations:
            return False
        
        amount = transaction.get('amount')
        if amount is None:
            return False
        
        if operation in ['deposit', 'withdraw'] and amount <= 0:
            return False
        
        
        date_str = transaction.get('date')
        if not self._is_valid_date(date_str):
            return False
        
        status = transaction.get('status')
        if status != 'success':
            if status == 'succes':
                transaction['status'] = 'success'
            else:
                return False
        
        return True

    def _is_valid_date(self, date_str):
        """Проверка валидности даты"""
        try:
            if '2025-17-34' in date_str or '2023-16-40' in date_str or '2023-22-32' in date_str or '2024-17-35' in date_str or '2025-16-35' in date_str:
                return False
            
            formats = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M']
            for fmt in formats:
                try:
                    datetime.datetime.strptime(date_str, fmt)
                    return True
                except ValueError:
                    continue
            return False
        except:
            return False

    def load_from_file(self, filename):
        """Загрузка истории операций из файла"""
        if filename.endswith('.csv'):
            self._load_from_csv(filename)
        elif filename.endswith('.json'):
            self._load_from_json(filename)
        else:
            raise ValueError("Поддерживаются только CSV и JSON файлы")

    def _load_from_csv(self, filename):
        """Загрузка из CSV файла"""
        try:
            df = pd.read_csv(filename)
            self._process_transactions(df.to_dict('records'))
        except Exception as e:
            print(f"Ошибка загрузки CSV: {e}")

    def _load_from_json(self, filename):
        """Загрузка из JSON файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._process_transactions(data)
        except Exception as e:
            print(f"Ошибка загрузки JSON: {e}")

    def _process_transactions(self, transactions):
        """Обработка транзакций"""
        valid_transactions = []
        
        for transaction in transactions:
            if transaction.get('account_number') == self.account_number:
                if self.clean_history(transaction):
                    valid_transactions.append(transaction)
        
        valid_transactions.sort(key=lambda x: self._parse_date(x['date']))
        
        for transaction in valid_transactions:
            amount = transaction['amount']
            operation = transaction['operation']
            
            if operation == 'deposit':
                self._balance += amount
                op_type = 'Пополнение счета'
            elif operation == 'withdraw':
                self._balance -= amount
                op_type = 'Снятие средств'
            elif operation == 'interest':
                self._balance += amount
                op_type = 'interest'
            
            self.operations_history.append({
                'type': op_type,
                'amount': amount,
                'datetime': self._parse_date(transaction['date']),
                'balance_after': self._balance,
                'status': 'success',
                'source': 'file_import'
            })

    def _parse_date(self, date_str):
        """Парсинг даты из строки"""
        formats = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M']
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return datetime.datetime.now()


savings = SavingsAccount("Сергеев Сергей", 0)
savings.account_number="ACC-100001"
# savings.deposit(-100)
# savings.withdraw(-51)
# savings.deposit(1)
# savings.withdraw(1)

print("История операций:")
print(savings.get_history(), "\n")

test_transaction = {
    'account_number': 'ACC-1000',
    'operation': 'deposit',
    'amount': 100.0,
    'date': '2025-10-01 12:00:00',
    'status': 'success'
}
print("Тест clean_history с правильной транзакцией:")
print(savings.clean_history(test_transaction))

test_transaction_bad = {
    'account_number': 'ACC-1000',
    'operation': 'deposit',
    'amount': -100.0,
    'date': '2025-10-01 12:00:00',
    'status': 'success'
}
print("Тест clean_history с неправильной транзакцией (отрицательная сумма):")
print(savings.clean_history(test_transaction_bad))

print("\nЗагрузка данных из файла...")
savings.load_from_file('dz_5/transactions_dirty.csv')

print(f"Баланс после загрузки: {savings.get_balance()}")
print(f"Количество операций: {len(savings.get_history())}")
print(savings.account_number)
print(savings.get_history())