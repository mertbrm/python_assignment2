import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "finance.db"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    currency TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('income','expense')),
    category TEXT,
    note TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    source TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);
"""


class SQLiteStorage:
    """Lightweight SQLite helper around finance entities."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    # Accounts --------------------------------------------------------------
    def list_accounts(self) -> List[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, currency FROM accounts ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    def create_account(
        self, name: str, currency: str, account_id: Optional[int] = None
    ) -> dict:
        if not name:
            raise ValueError("Account name is required")
        if not currency:
            raise ValueError("Currency is required")
        with self._connect() as conn:
            if account_id is None:
                cur = conn.execute(
                    "INSERT INTO accounts(name, currency) VALUES (?, ?)",
                    (name, currency),
                )
            else:
                cur = conn.execute(
                    "INSERT INTO accounts(id, name, currency) VALUES (?, ?, ?)",
                    (account_id, name, currency),
                )
            conn.commit()
            new_id = cur.lastrowid if cur.lastrowid is not None else account_id
        return {"id": new_id, "name": name, "currency": currency}

    def update_account(
        self, account_id: int, name: Optional[str] = None, currency: Optional[str] = None
    ) -> None:
        if name is None and currency is None:
            return
        fields: list[str] = []
        params: list[object] = []
        if name is not None:
            fields.append("name = ?")
            params.append(name)
        if currency is not None:
            fields.append("currency = ?")
            params.append(currency)
        params.append(account_id)
        with self._connect() as conn:
            cur = conn.execute(
                f"UPDATE accounts SET {', '.join(fields)} WHERE id = ?", params
            )
            if cur.rowcount == 0:
                raise ValueError("Account not found")
            conn.commit()

    def delete_account(self, account_id: int) -> None:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            if cur.rowcount == 0:
                raise ValueError("Account not found")
            conn.commit()

    def _ensure_account_exists(self, account_id: int) -> None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id FROM accounts WHERE id = ?", (account_id,)
            ).fetchone()
            if row is None:
                raise ValueError(f"Account {account_id} does not exist")

    # Transactions ---------------------------------------------------------
    def list_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_id: Optional[int] = None,
    ) -> List[dict]:
        query = [
            "SELECT id, account_id, date, amount, type, category, note",
            "FROM transactions",
            "WHERE 1=1",
        ]
        params: list[object] = []
        if start_date:
            query.append("AND date >= ?")
            params.append(start_date)
        if end_date:
            query.append("AND date <= ?")
            params.append(end_date)
        if account_id is not None:
            query.append("AND account_id = ?")
            params.append(account_id)
        query.append("ORDER BY date")
        sql = " ".join(query)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def create_transaction(
        self,
        account_id: int,
        date: str,
        amount: float,
        t_type: str,
        category: str = "",
        note: str = "",
    ) -> dict:
        if t_type not in {"income", "expense"}:
            raise ValueError("type must be 'income' or 'expense'")
        self._ensure_account_exists(account_id)
        stored_amount = float(amount)
        if t_type == "expense":
            stored_amount = -abs(stored_amount)
        else:
            stored_amount = abs(stored_amount)
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO transactions(account_id, date, amount, type, category, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (account_id, date, stored_amount, t_type, category, note),
            )
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "account_id": account_id,
            "date": date,
            "amount": stored_amount,
            "type": t_type,
            "category": category,
            "note": note,
        }

    def delete_transaction(self, transaction_id: int) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM transactions WHERE id = ?", (transaction_id,)
            )
            if cur.rowcount == 0:
                raise ValueError("Transaction not found")
            conn.commit()

    # Income ---------------------------------------------------------------
    def list_income(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_id: Optional[int] = None,
    ) -> List[dict]:
        query = [
            "SELECT id, account_id, date, amount, source",
            "FROM income",
            "WHERE 1=1",
        ]
        params: list[object] = []
        if start_date:
            query.append("AND date >= ?")
            params.append(start_date)
        if end_date:
            query.append("AND date <= ?")
            params.append(end_date)
        if account_id is not None:
            query.append("AND account_id = ?")
            params.append(account_id)
        query.append("ORDER BY date")
        sql = " ".join(query)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def create_income(
        self,
        account_id: int,
        date: str,
        amount: float,
        source: str = "",
    ) -> dict:
        self._ensure_account_exists(account_id)
        stored_amount = abs(float(amount))
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO income(account_id, date, amount, source)
                VALUES (?, ?, ?, ?)
                """,
                (account_id, date, stored_amount, source),
            )
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "account_id": account_id,
            "date": date,
            "amount": stored_amount,
            "source": source,
        }

    def delete_income(self, income_id: int) -> None:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM income WHERE id = ?", (income_id,))
            if cur.rowcount == 0:
                raise ValueError("Income record not found")
            conn.commit()

    def monthly_income(self) -> List[dict]:
        """Aggregate income by YYYY-MM."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT substr(date, 1, 7) AS month, SUM(amount) AS income
                FROM income
                GROUP BY month
                ORDER BY month
                """
            ).fetchall()
        return [dict(row) for row in rows]

    # Utility --------------------------------------------------------------
    def clear_all(self) -> None:
        """Helper used in demos/tests to wipe tables."""
        with self._connect() as conn:
            conn.executescript(
                """
                DELETE FROM transactions;
                DELETE FROM income;
                DELETE FROM accounts;
                """
            )
            conn.commit()
