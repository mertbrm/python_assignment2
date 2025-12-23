from exceptions import ValidationError


class Budget:
    def __init__(self, budget_id: str, month: str, category: str, limit_amount: float):
        if not budget_id:
            raise ValidationError("Budget ID cannot be empty.")
        self.id = budget_id
        self.month = month  # "YYYY-MM"
        self.category = category
        self.limit_amount = float(limit_amount)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "month": self.month,
            "category": self.category,
            "limit_amount": str(self.limit_amount),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        return cls(
            data["id"],
            data["month"],
            data["category"],
            float(data.get("limit_amount", "0")),
        )
