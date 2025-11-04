import datetime
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Account:
    _account_counter = 1000

    def __init__(self, account_holder: str, balance: float = 0):
        self._validation_FIO(account_holder)
        self.holder = account_holder
        self._balance = balance
        self.account_number = f'ACC-{Account._account_counter+1}'

        self.operations_history = []

        initial_operation = {
            'type': 'Создание счета',
            'amount': balance,
            'datetime': datetime.datetime.now(),
            'balance_after': balance,
            'status': 'success'
        }
        self.operations_history.append(initial_operation)

        Account._account_counter += 1

    def _validation_FIO(self, name: str):
        """Валидация ФИО"""
        pattern = r'^[A-ZА-ЯЁ][a-zа-яё]*\s+[A-ZА-ЯЁ][a-zа-яё]*$'
        
        if not re.match(pattern=pattern, string=name.strip()):
            raise ValueError(
                "Имя владельца должно быть в формате «Имя Фамилия» (только два слова, оба с заглавной буквы)")

    def _validation_amount(self, amount: float) -> bool:
        """Валидация данных при фин операциях"""
        if amount <= 0:
            raise ValueError("Сумма не должна быть равна или меньше нуля")

    def deposit(self, amount: float):
        """Пополнение средств со счета"""
        try:
            self._validation_amount(amount)
            self._balance = self._balance + amount
            self.operations_history.append({
                'type': 'Пополнение счета',
                'amount': amount,
                'datetime': datetime.datetime.now(),
                'balance_after': self._balance,
                'status': 'success'
            })

        except ValueError as e:
            self.operations_history.append({
                'type': 'Пополнение счета',
                'amount': amount,
                'datetime': datetime.datetime.now(),
                'balance_after': self._balance,
                'status': 'failed',
                'error': e

            })

    def withdraw(self, amount: float):
        """Снятие средств со счета"""
        try:
            self._validation_amount(amount)
            if amount <= self._balance:
                self._balance = self._balance - amount
                self.operations_history.append({
                    'type': 'Снятие средств',  
                    'amount': amount,
                    'datetime': datetime.datetime.now(),
                    'balance_after': self._balance,
                    'status': 'success'
                })
            else:
                raise ValueError("На счете не достаточно средств")
        except ValueError as e:
            self.operations_history.append({
                'type': 'Снятие средств',
                'amount': amount,
                'datetime': datetime.datetime.now(),
                'balance_after': self._balance,
                'status': 'failed',
                'error': e

            })

    def get_balance(self) -> float:
        """Получение баланса"""
        return self._balance

    def get_history(self, type_operation="all") -> list:
        """Получение истории по фильтру"""
        if type_operation == "all":
            return self.operations_history
        else:
            return [operation for operation in self.operations_history if operation["type"] == type_operation]

    def _create_diagram(self, data):
        """Вывод диаграммы"""
        plt.figure(figsize=(12, 6))
        plt.plot(data['datetime'], data['balance_after'],
                 marker='o', linewidth=2)
        plt.title(f'История операций счета {self.account_number}')
        plt.xlabel('Время операции')
        plt.ylabel('Баланс после операции')
        plt.grid(True, alpha=0.3)

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S\n%d.%m.%Y'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_history(self):
        """Создание диаграммы"""
        if not self.operations_history:
            print("Нет данных для построения графика")
            return

        df_data = pd.DataFrame(self.operations_history)

        df_data['datetime'] = pd.to_datetime(df_data['datetime'])

        self._create_diagram(df_data)

class CheckingAccount(Account):
    """расчётный счёт"""
    def __init__(self, account_holder, balance=0):
        super().__init__(account_holder, balance)
        self.account_type = "Checking"


        
# obj = Account("Степанов Степан")
# time.sleep(1)
# obj.deposit(200)
# time.sleep(1)
# obj.withdraw(50)
# time.sleep(1)
# obj.deposit(100)
# time.sleep(1)
# obj.withdraw(30)
# time.sleep(1)
# obj.plot_history()
