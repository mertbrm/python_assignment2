from exceptions import ValidationError


class Account:
    def __init__(self, account_id: str, name: str, account_type: str, currency: str):
        if not account_id:
            raise ValidationError("Account ID cannot be empty.")
        self.id = account_id
        self.name = name
        self.account_type = account_type  # e.g. "cash", "bank"
        self.currency = currency

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "account_type": self.account_type,
            "currency": self.currency,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        account_type = data.get("account_type", "other")
        if account_type == "cash":
            return CashAccount(
                data["id"], data["name"], data.get("currency", "HUF")
            )
        if account_type == "bank":
            return BankAccount(
                data["id"], data["name"], data.get("currency", "HUF")
            )
        return cls(
            data["id"],
            data["name"],
            account_type,
            data.get("currency", "HUF"),
        )


class CashAccount(Account):
    """Specialized account stored as cash (wallet)."""

    def __init__(self, account_id: str, name: str, currency: str = "HUF"):
        super().__init__(account_id, name, "cash", currency)


class BankAccount(Account):
    """Specialized account stored in a bank."""

    def __init__(self, account_id: str, name: str, currency: str = "HUF"):
        super().__init__(account_id, name, "bank", currency)
