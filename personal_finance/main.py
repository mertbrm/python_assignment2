from managers.account_manager import AccountManager
from managers.transaction_manager import TransactionManager
from managers.budget_manager import BudgetManager
from storage.csv_storage import (
    save_accounts,
    load_accounts,
    save_transactions,
    load_transactions,
    save_budgets,
    load_budgets,
)
from exceptions import FinanceError, NotFoundError, ValidationError, StorageError

ACCOUNTS_FILE = "accounts.csv"
TRANSACTIONS_FILE = "transactions.csv"
BUDGETS_FILE = "budgets.csv"


def print_accounts(account_manager: AccountManager) -> None:
    accounts = account_manager.list_accounts()
    if not accounts:
        print("No accounts.")
        return
    for acc in accounts:
        print(f"{acc.id}: {acc.name} ({acc.account_type}, {acc.currency})")


def print_transactions(transaction_manager: TransactionManager) -> None:
    transactions = transaction_manager.list_transactions()
    if not transactions:
        print("No transactions.")
        return
    for t in transactions:
        print(
            f"{t.id}: {t.date} | {t.account_id} | {t.transaction_type} "
            f"{t.amount} | {t.category} | {t.description}"
        )


def print_budgets(budget_manager: BudgetManager) -> None:
    budgets = budget_manager.list_budgets()
    if not budgets:
        print("No budgets.")
        return
    for b in budgets:
        print(
            f"{b.id}: {b.month} | {b.category} | limit: {b.limit_amount}"
        )


def manage_accounts(account_manager: AccountManager) -> None:
    while True:
        print("\n--- Manage Accounts ---")
        print("1. List accounts")
        print("2. Create account")
        print("3. Update account")
        print("4. Delete account")
        print("5. Back to main menu")
        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                print_accounts(account_manager)
            elif choice == "2":
                account_id = input("ID: ")
                name = input("Name: ")
                account_type = input("Type (cash/bank/other): ").strip()
                currency = input("Currency (e.g. HUF, EUR): ").strip()
                account_manager.create_account(
                    account_id, name, account_type, currency
                )
                print("Account created.")
            elif choice == "3":
                account_id = input("ID to update: ")
                name = input("New name (leave empty to keep): ")
                account_type = input("New type (leave empty to keep): ")
                currency = input("New currency (leave empty to keep): ")
                account_manager.update_account(
                    account_id,
                    name if name else None,
                    account_type if account_type else None,
                    currency if currency else None,
                )
                print("Account updated.")
            elif choice == "4":
                account_id = input("ID to delete: ")
                account_manager.delete_account(account_id)
                print("Account deleted.")
            elif choice == "5":
                return
            else:
                print("Invalid choice.")
        except FinanceError as e:
            print(f"Error: {e}")


def manage_transactions(transaction_manager: TransactionManager) -> None:
    while True:
        print("\n--- Manage Transactions ---")
        print("1. List transactions")
        print("2. Create transaction")
        print("3. Update transaction")
        print("4. Delete transaction")
        print("5. Back to main menu")
        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                print_transactions(transaction_manager)
            elif choice == "2":
                transaction_id = input("ID: ")
                account_id = input("Account ID: ")
                date = input("Date (YYYY-MM-DD): ")
                raw_amount = input("Amount (positive number): ")
                try:
                    amount = float(raw_amount)
                except ValueError:
                    raise ValidationError("Amount must be a number.")
                description = input("Description: ")
                category = input("Category: ")
                t_type = input("Type (income/expense): ").strip()
                if t_type not in ("income", "expense"):
                    raise ValidationError("Type must be 'income' or 'expense'.")
                transaction_manager.create_transaction(
                    transaction_id,
                    account_id,
                    date,
                    amount,
                    description,
                    category,
                    t_type,
                )
                print("Transaction created.")
            elif choice == "3":
                transaction_id = input("ID to update: ")
                date = input("New date (leave empty to keep): ")
                raw_amount = input(
                    "New amount (leave empty to keep current): "
                ).strip()
                amount = None
                if raw_amount:
                    try:
                        amount = float(raw_amount)
                    except ValueError:
                        raise ValidationError("Amount must be a number.")
                description = input(
                    "New description (leave empty to keep): "
                )
                category = input("New category (leave empty to keep): ")
                transaction_manager.update_transaction(
                    transaction_id,
                    date if date else None,
                    amount,
                    description if description else None,
                    category if category else None,
                )
                print("Transaction updated.")
            elif choice == "4":
                transaction_id = input("ID to delete: ")
                transaction_manager.delete_transaction(transaction_id)
                print("Transaction deleted.")
            elif choice == "5":
                return
            else:
                print("Invalid choice.")
        except FinanceError as e:
            print(f"Error: {e}")


def manage_budgets(budget_manager: BudgetManager) -> None:
    while True:
        print("\n--- Manage Budgets ---")
        print("1. List budgets")
        print("2. Create budget")
        print("3. Update budget")
        print("4. Delete budget")
        print("5. Check budget status")
        print("6. Back to main menu")
        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                print_budgets(budget_manager)
            elif choice == "2":
                budget_id = input("ID: ")
                month = input("Month (YYYY-MM): ")
                category = input("Category: ")
                raw_limit = input("Limit amount: ")
                try:
                    limit_amount = float(raw_limit)
                except ValueError:
                    raise ValidationError("Limit amount must be a number.")
                budget_manager.create_budget(
                    budget_id, month, category, limit_amount
                )
                print("Budget created.")
            elif choice == "3":
                budget_id = input("ID to update: ")
                month = input("New month (leave empty to keep): ")
                category = input("New category (leave empty to keep): ")
                raw_limit = input(
                    "New limit amount (leave empty to keep): "
                ).strip()
                limit_amount = None
                if raw_limit:
                    try:
                        limit_amount = float(raw_limit)
                    except ValueError:
                        raise ValidationError("Limit amount must be a number.")
                budget_manager.update_budget(
                    budget_id,
                    month if month else None,
                    category if category else None,
                    limit_amount,
                )
                print("Budget updated.")
            elif choice == "4":
                budget_id = input("ID to delete: ")
                budget_manager.delete_budget(budget_id)
                print("Budget deleted.")
            elif choice == "5":
                month = input("Month (YYYY-MM): ")
                category = input("Category: ")
                spent, remaining = budget_manager.check_budget_status(
                    month, category
                )
                print(
                    f"Spent: {spent:.2f}, Remaining: {remaining:.2f}"
                )
            elif choice == "6":
                return
            else:
                print("Invalid choice.")
        except FinanceError as e:
            print(f"Error: {e}")


def save_all(account_manager, transaction_manager, budget_manager):
    save_accounts(ACCOUNTS_FILE, account_manager.list_accounts())
    save_transactions(
        TRANSACTIONS_FILE, transaction_manager.list_transactions()
    )
    save_budgets(BUDGETS_FILE, budget_manager.list_budgets())
    print("Data saved to CSV files.")


def load_all(account_manager, transaction_manager, budget_manager):
    accounts = load_accounts(ACCOUNTS_FILE)
    account_manager.accounts = accounts

    from models.transaction import Transaction  # ensure class loaded

    transactions = load_transactions(TRANSACTIONS_FILE)
    transaction_manager.transactions = transactions

    budgets = load_budgets(BUDGETS_FILE)
    budget_manager.budgets = budgets

    print("Data loaded from CSV files.")


def main():
    account_manager = AccountManager()
    transaction_manager = TransactionManager(account_manager)
    budget_manager = BudgetManager(transaction_manager)

    while True:
        print("\n=== Personal Finance Manager ===")
        print("1. Manage Accounts")
        print("2. Manage Transactions")
        print("3. Manage Budgets")
        print("4. Save to CSV")
        print("5. Load from CSV")
        print("6. Exit")
        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                manage_accounts(account_manager)
            elif choice == "2":
                manage_transactions(transaction_manager)
            elif choice == "3":
                manage_budgets(budget_manager)
            elif choice == "4":
                save_all(account_manager, transaction_manager, budget_manager)
            elif choice == "5":
                load_all(account_manager, transaction_manager, budget_manager)
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")
        except FinanceError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
