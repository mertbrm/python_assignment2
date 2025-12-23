import csv
from pathlib import Path
from models.account import Account
from models.transaction import Transaction
from models.budget import Budget
from exceptions import StorageError


def _ensure_str_path(filename) -> str:
    return str(filename)


def save_accounts(filename, accounts) -> None:
    filename = _ensure_str_path(filename)
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["id", "name", "account_type", "currency"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for acc in accounts:
                writer.writerow(acc.to_dict())
    except OSError as e:
        raise StorageError(f"Error saving accounts to CSV: {e}")


def load_accounts(filename) -> list[Account]:
    filename = _ensure_str_path(filename)
    if not Path(filename).exists():
        return []
    try:
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [Account.from_dict(row) for row in reader]
    except OSError as e:
        raise StorageError(f"Error loading accounts from CSV: {e}")


def save_transactions(filename, transactions) -> None:
    filename = _ensure_str_path(filename)
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "id",
                "account_id",
                "date",
                "amount",
                "description",
                "category",
                "transaction_type",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in transactions:
                writer.writerow(t.to_dict())
    except OSError as e:
        raise StorageError(f"Error saving transactions to CSV: {e}")


def load_transactions(filename) -> list[Transaction]:
    filename = _ensure_str_path(filename)
    if not Path(filename).exists():
        return []
    try:
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [Transaction.from_dict(row) for row in reader]
    except OSError as e:
        raise StorageError(f"Error loading transactions from CSV: {e}")


def save_budgets(filename, budgets) -> None:
    filename = _ensure_str_path(filename)
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["id", "month", "category", "limit_amount"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for b in budgets:
                writer.writerow(b.to_dict())
    except OSError as e:
        raise StorageError(f"Error saving budgets to CSV: {e}")


def load_budgets(filename) -> list[Budget]:
    filename = _ensure_str_path(filename)
    if not Path(filename).exists():
        return []
    try:
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [Budget.from_dict(row) for row in reader]
    except OSError as e:
        raise StorageError(f"Error loading budgets from CSV: {e}")
