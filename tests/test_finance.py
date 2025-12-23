import pytest

from personal_finance.managers.account_manager import AccountManager
from personal_finance.managers.transaction_manager import TransactionManager
from personal_finance.managers.budget_manager import BudgetManager

from personal_finance.models.account import Account
from personal_finance.models.transaction import ExpenseTransaction
from personal_finance.models.budget import Budget

from personal_finance.storage.csv_storage import save_accounts, load_accounts
from personal_finance.exceptions import ValidationError, NotFoundError


def test_add_account_unit():
    """Unit test: adding a single account."""
    m = AccountManager()
    m.add_account(Account("A1", "Wallet", "cash", "HUF"))
    assert len(m.accounts) == 1
    assert m.accounts[0].name == "Wallet"


def test_transaction_needs_existing_account_integration():
    """Integration: transaction must be linked to existing account."""
    acc_mgr = AccountManager()
    acc_mgr.add_account(Account("A1", "Wallet", "cash", "HUF"))
    tr_mgr = TransactionManager(acc_mgr)

    expense = ExpenseTransaction(
        "T1", "A1", "2025-11-18", 100.0, "Groceries", "food"
    )
    tr_mgr.add_transaction(expense)

    assert len(tr_mgr.transactions) == 1
    assert tr_mgr.transactions[0].account_id == "A1"


def test_save_and_load_accounts_system(tmp_path):
    """System test: save + load accounts via CSV."""
    acc_mgr = AccountManager()
    acc_mgr.add_account(Account("A1", "Wallet", "cash", "HUF"))

    csv_path = tmp_path / "accounts.csv"
    save_accounts(csv_path, acc_mgr.accounts)

    loaded = load_accounts(csv_path)
    assert len(loaded) == 1
    assert loaded[0].id == "A1"
    assert loaded[0].name == "Wallet"


def test_budget_status_with_expense():
    acc_mgr = AccountManager()
    acc_mgr.add_account(Account("A1", "Wallet", "cash", "HUF"))
    tr_mgr = TransactionManager(acc_mgr)
    bud_mgr = BudgetManager(tr_mgr)

    bud_mgr.create_budget("B1", "2025-11", "food", 200.0)
    e = ExpenseTransaction("T1", "A1", "2025-11-10", 50.0, "Groceries", "food")
    tr_mgr.add_transaction(e)

    spent, remaining = bud_mgr.check_budget_status("2025-11", "food")
    assert spent == 50.0
    assert remaining == 150.0
