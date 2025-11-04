import datetime
from dz_5_1 import Account


class CheckingAccount(Account):
    """Расчётный счёт"""

    def __init__(self, account_holder, balance=0):
        super().__init__(account_holder, balance)
        self.account_type = "Checking"


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


checking = CheckingAccount("Иcванов Иван", 1000)
checking.deposit(500)
checking.withdraw(200)
checking.withdraw(150000)
checking.get_history()
print(f"Баланс расчетного счета: {checking.get_balance()}")
print(f"Тип счета: {checking.account_type}")

print("\n\n____________________________________\n\n")


savings = SavingsAccount("Сергеев Сергей", 0)
savings.deposit(100)
savings.withdraw(51)
savings.deposit(101)
savings.withdraw(1)
savings.deposit(102)
savings.withdraw(1)
savings.deposit(103)
savings.withdraw(1)
savings.deposit(104)
savings.withdraw(1)

print(savings.get_history(), "\n")
print(savings.get_large_operations(3))
