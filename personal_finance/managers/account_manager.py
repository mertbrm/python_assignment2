from typing import List
from models.account import Account, CashAccount, BankAccount
from exceptions import ValidationError, NotFoundError


class AccountManager:
    def __init__(self):
        self.accounts: List[Account] = []

    def list_accounts(self) -> List[Account]:
        return self.accounts

    def _find_index(self, account_id: str) -> int:
        for i, acc in enumerate(self.accounts):
            if acc.id == account_id:
                return i
        raise NotFoundError(f"Account with ID '{account_id}' not found.")

    def get_account(self, account_id: str) -> Account:
        idx = self._find_index(account_id)
        return self.accounts[idx]

    def add_account(self, account: Account) -> None:
        if any(a.id == account.id for a in self.accounts):
            raise ValidationError(f"Account with ID '{account.id}' already exists.")
        self.accounts.append(account)

    def create_account(
        self, account_id: str, name: str, account_type: str, currency: str
    ) -> Account:
        if account_type == "cash":
            acc = CashAccount(account_id, name, currency)
        elif account_type == "bank":
            acc = BankAccount(account_id, name, currency)
        else:
            acc = Account(account_id, name, account_type, currency)
        self.add_account(acc)
        return acc

    def update_account(
        self,
        account_id: str,
        name: str | None = None,
        account_type: str | None = None,
        currency: str | None = None,
    ) -> None:
        acc = self.get_account(account_id)
        if name:
            acc.name = name
        if account_type:
            acc.account_type = account_type
        if currency:
            acc.currency = currency

    def delete_account(self, account_id: str) -> None:
        idx = self._find_index(account_id)
        del self.accounts[idx]
