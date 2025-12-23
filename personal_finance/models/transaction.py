from exceptions import ValidationError


class Transaction:
    def __init__(
        self,
        transaction_id: str,
        account_id: str,
        date: str,
        amount: float,
        description: str,
        category: str,
        transaction_type: str,
    ):
        if not transaction_id:
            raise ValidationError("Transaction ID cannot be empty.")
        self.id = transaction_id
        self.account_id = account_id
        self.date = date  # keep simple: string "YYYY-MM-DD"
        self.amount = float(amount)
        self.description = description
        self.category = category
        self.transaction_type = transaction_type  # "income" or "expense"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "account_id": self.account_id,
            "date": self.date,
            "amount": str(self.amount),
            "description": self.description,
            "category": self.category,
            "transaction_type": self.transaction_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        t_type = data.get("transaction_type", "expense")
        amount = float(data.get("amount", "0"))
        if t_type == "income":
            return IncomeTransaction(
                data["id"],
                data["account_id"],
                data["date"],
                amount,
                data.get("description", ""),
                data.get("category", ""),
            )
        if t_type == "expense":
            return ExpenseTransaction(
                data["id"],
                data["account_id"],
                data["date"],
                amount,
                data.get("description", ""),
                data.get("category", ""),
            )
        return cls(
            data["id"],
            data["account_id"],
            data["date"],
            amount,
            data.get("description", ""),
            data.get("category", ""),
            t_type,
        )


class ExpenseTransaction(Transaction):
    """Expenses are stored as negative amounts."""

    def __init__(
        self,
        transaction_id: str,
        account_id: str,
        date: str,
        amount: float,
        description: str,
        category: str,
    ):
        super().__init__(
            transaction_id,
            account_id,
            date,
            -abs(amount),
            description,
            category,
            "expense",
        )


class IncomeTransaction(Transaction):
    """Income is stored as positive amounts."""

    def __init__(
        self,
        transaction_id: str,
        account_id: str,
        date: str,
        amount: float,
        description: str,
        category: str,
    ):
        super().__init__(
            transaction_id,
            account_id,
            date,
            abs(amount),
            description,
            category,
            "income",
        )
