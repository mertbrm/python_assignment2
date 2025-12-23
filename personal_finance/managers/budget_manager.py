from typing import List
from models.budget import Budget
from managers.transaction_manager import TransactionManager
from exceptions import ValidationError, NotFoundError


class BudgetManager:
    def __init__(self, transaction_manager: TransactionManager):
        self.budgets: List[Budget] = []
        self.transaction_manager = transaction_manager

    def list_budgets(self) -> List[Budget]:
        return self.budgets

    def _find_index(self, budget_id: str) -> int:
        for i, b in enumerate(self.budgets):
            if b.id == budget_id:
                return i
        raise NotFoundError(f"Budget with ID '{budget_id}' not found.")

    def get_budget(self, budget_id: str) -> Budget:
        idx = self._find_index(budget_id)
        return self.budgets[idx]

    def add_budget(self, budget: Budget) -> None:
        if any(b.id == budget.id for b in self.budgets):
            raise ValidationError(f"Budget with ID '{budget.id}' already exists.")
        self.budgets.append(budget)

    def create_budget(
        self, budget_id: str, month: str, category: str, limit_amount: float
    ) -> Budget:
        b = Budget(budget_id, month, category, limit_amount)
        self.add_budget(b)
        return b

    def update_budget(
        self,
        budget_id: str,
        month: str | None = None,
        category: str | None = None,
        limit_amount: float | None = None,
    ) -> None:
        b = self.get_budget(budget_id)
        if month:
            b.month = month
        if category:
            b.category = category
        if limit_amount is not None:
            b.limit_amount = float(limit_amount)

    def delete_budget(self, budget_id: str) -> None:
        idx = self._find_index(budget_id)
        del self.budgets[idx]

    def check_budget_status(self, month: str, category: str) -> tuple[float, float]:
        """
        Returns (spent, remaining) for the given month and category.
        If no budget is found, raises NotFoundError.
        """
        budget = None
        for b in self.budgets:
            if b.month == month and b.category == category:
                budget = b
                break
        if budget is None:
            raise NotFoundError(
                f"No budget found for month '{month}' and category '{category}'."
            )
        spent = self.transaction_manager.get_total_for_month_and_category(
            month, category
        )
        remaining = budget.limit_amount - spent
        return spent, remaining
