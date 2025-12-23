import statistics
from datetime import datetime
from typing import List

import numpy as np


def summarize_amounts(records: List[dict]) -> dict:
    amounts = [float(r.get("amount", 0)) for r in records]
    categories: dict[str, float] = {}
    for r in records:
        cat = (r.get("category") or r.get("source") or "uncategorized").strip()
        categories[cat] = categories.get(cat, 0.0) + float(r.get("amount", 0))

    if not amounts:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "min": 0.0,
            "max": 0.0,
            "std": 0.0,
            "by_category": categories,
        }

    mean_val = statistics.mean(amounts)
    median_val = statistics.median(amounts)
    min_val = min(amounts)
    max_val = max(amounts)
    std_val = statistics.pstdev(amounts) if len(amounts) > 1 else 0.0

    return {
        "count": len(amounts),
        "mean": round(mean_val, 2),
        "median": round(median_val, 2),
        "min": round(min_val, 2),
        "max": round(max_val, 2),
        "std": round(std_val, 2),
        "by_category": {k: round(v, 2) for k, v in categories.items()},
    }


def _parse_month(month_str: str) -> datetime:
    return datetime.strptime(month_str, "%Y-%m")


def _add_months(start_month: str, months_to_add: int) -> str:
    dt = _parse_month(start_month)
    month = dt.month - 1 + months_to_add
    year = dt.year + month // 12
    month = month % 12 + 1
    return f"{year:04d}-{month:02d}"


def forecast_income(history: List[dict], months_ahead: int = 3) -> dict:
    """Compute a simple linear regression forecast for monthly income."""
    if months_ahead < 1:
        months_ahead = 1

    if not history:
        return {"history": [], "forecast": []}

    # Ensure history sorted by month
    history_sorted = sorted(history, key=lambda row: row["month"])
    y = np.array([float(row["income"]) for row in history_sorted], dtype=float)
    x = np.arange(len(y), dtype=float)

    if len(y) == 1:
        slope = 0.0
        intercept = y[0]
    else:
        slope, intercept = np.polyfit(x, y, 1)

    last_month = history_sorted[-1]["month"]
    forecast_rows = []
    for i in range(1, months_ahead + 1):
        idx = len(y) + i - 1
        predicted = float(slope * idx + intercept)
        future_month = _add_months(last_month, i)
        forecast_rows.append(
            {
                "month": future_month,
                "predicted_income": round(predicted, 2),
            }
        )

    clean_history = [
        {"month": row["month"], "income": round(float(row["income"]), 2)}
        for row in history_sorted
    ]
    return {"history": clean_history, "forecast": forecast_rows}
