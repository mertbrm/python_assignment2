# Personal Finance API (Assignment 2)

Flask-based REST API using SQLite storage with basic statistics and income forecasting.

## Setup

1. Create / activate a virtual environment.
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the API (creates `finance.db` automatically):

```
python app.py
```

4. Open the bundled frontend:

- Visit http://localhost:5000/ in your browser. All actions use the API directly (no Postman/curl needed).

## Key Endpoints

- `GET /health` — quick status check.
- `POST /accounts` — `{ "name": "Wallet", "currency": "USD" }`.
- `POST /transactions` — `{ "account_id": 1, "date": "2025-01-05", "amount": 120, "type": "expense", "category": "food" }`.
- `POST /income` — `{ "account_id": 1, "date": "2025-01-15", "amount": 800, "source": "salary" }`.
- `GET /transactions?from=2025-01-01&to=2025-01-31` — filter by date range.
- `GET /stats/summary?kind=transactions&from=2025-01-01&to=2025-01-31` — mean/median/min/max/std plus category totals.
- `GET /stats/income_forecast?months=3` — linear forecast of next N months based on stored income.

Frontend page features:

- Create accounts, transactions (income/expense), and income entries.
- View recent records and summary stats (mean/median/min/max/std, category totals).
- Run income forecast for the next N months and display history + predictions.

## Notes

- SQLite file is stored at `finance.db` in the project root.
- Expenses are stored as negative amounts so category sums are intuitive.
- Foreign keys are enforced; create an account before adding transactions or income.
