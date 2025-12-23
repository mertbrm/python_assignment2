from typing import List
from models.transaction import Transaction, ExpenseTransaction, IncomeTransaction
from managers.account_manager import AccountManager
from exceptions import ValidationError, NotFoundError


class TransactionManager:
    def __init__(self, account_manager: AccountManager):
        self.transactions: List[Transaction] = []
        self.account_manager = account_manager

    def list_transactions(self) -> List[Transaction]:
        return self.transactions

    def _find_index(self, transaction_id: str) -> int:
        for i, t in enumerate(self.transactions):
            if t.id == transaction_id:
                return i
        raise NotFoundError(f"Transaction with ID '{transaction_id}' not found.")

    def get_transaction(self, transaction_id: str) -> Transaction:
        idx = self._find_index(transaction_id)
        return self.transactions[idx]

    def add_transaction(self, transaction: Transaction) -> None:
        # Check account exists
        self.account_manager.get_account(transaction.account_id)
        if any(t.id == transaction.id for t in self.transactions):
            raise ValidationError(
                f"Transaction with ID '{transaction.id}' already exists."
            )
        self.transactions.append(transaction)

    def create_transaction(
        self,
        transaction_id: str,
        account_id: str,
        date: str,
        amount: float,
        description: str,
        category: str,
        transaction_type: str,
    ) -> Transaction:
        if transaction_type == "income":
            t = IncomeTransaction(
                transaction_id, account_id, date, amount, description, category
            )
        else:
            t = ExpenseTransaction(
                transaction_id, account_id, date, amount, description, category
            )
        self.add_transaction(t)
        return t

    def update_transaction(
        self,
        transaction_id: str,
        date: str | None = None,
        amount: float | None = None,
        description: str | None = None,
        category: str | None = None,
    ) -> None:
        t = self.get_transaction(transaction_id)
        if date:
            t.date = date
        if amount is not None:
            if t.transaction_type == "income":
                t.amount = abs(float(amount))
            else:
                t.amount = -abs(float(amount))
        if description:
            t.description = description
        if category:
            t.category = category

    def delete_transaction(self, transaction_id: str) -> None:
        idx = self._find_index(transaction_id)
        del self.transactions[idx]

    def get_total_for_month_and_category(self, month: str, category: str) -> float:
        """
        Month format: 'YYYY-MM'. Expenses are negative numbers.
        This returns the absolute total spent for that category and month.
        """
        total = 0.0
        for t in self.transactions:
            if t.date.startswith(month) and t.category == category:
                if t.transaction_type == "expense":
                    total += -t.amount
        return total
