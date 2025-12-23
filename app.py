from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory

from personal_finance.analytics import forecast_income, summarize_amounts
from personal_finance.storage.sqlite_storage import SQLiteStorage

app = Flask(__name__, static_folder="static", static_url_path="")
storage = SQLiteStorage()


def _parse_date(date_str: str) -> str:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Date must be in YYYY-MM-DD format") from exc
    return date_str


def _parse_months(param: str | None, default: int = 3) -> int:
    if param is None:
        return default
    try:
        months = int(param)
    except ValueError as exc:
        raise ValueError("months must be an integer") from exc
    return months if months > 0 else default


@app.errorhandler(ValueError)
def handle_value_error(err: ValueError):
    return jsonify({"error": str(err)}), 400


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# Accounts -----------------------------------------------------------------
@app.route("/accounts", methods=["GET"])
def list_accounts():
    return jsonify(storage.list_accounts())


@app.route("/accounts", methods=["POST"])
def create_account():
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name", "").strip()
    currency = data.get("currency", "").strip()
    account_id = data.get("id")
    result = storage.create_account(name=name, currency=currency, account_id=account_id)
    return jsonify(result), 201


@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id: int):
    data = request.get_json(force=True, silent=True) or {}
    storage.update_account(account_id, name=data.get("name"), currency=data.get("currency"))
    return jsonify({"updated": True})


@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id: int):
    storage.delete_account(account_id)
    return jsonify({"deleted": True})


# Transactions -------------------------------------------------------------
@app.route("/transactions", methods=["GET"])
def get_transactions():
    start = request.args.get("from")
    end = request.args.get("to")
    account_id = request.args.get("account_id")
    if start:
        start = _parse_date(start)
    if end:
        end = _parse_date(end)
    account_filter = int(account_id) if account_id is not None else None
    rows = storage.list_transactions(start_date=start, end_date=end, account_id=account_filter)
    return jsonify(rows)


@app.route("/transactions", methods=["POST"])
def post_transaction():
    data = request.get_json(force=True, silent=True) or {}
    account_id = int(data.get("account_id"))
    date = _parse_date(data.get("date", ""))
    amount = float(data.get("amount"))
    t_type = (data.get("type") or data.get("transaction_type") or "").strip()
    category = data.get("category", "")
    note = data.get("note", data.get("description", ""))
    created = storage.create_transaction(
        account_id=account_id,
        date=date,
        amount=amount,
        t_type=t_type,
        category=category,
        note=note,
    )
    return jsonify(created), 201


@app.route("/transactions/<int:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id: int):
    storage.delete_transaction(transaction_id)
    return jsonify({"deleted": True})


# Income -------------------------------------------------------------------
@app.route("/income", methods=["GET"])
def list_income():
    start = request.args.get("from")
    end = request.args.get("to")
    account_id = request.args.get("account_id")
    if start:
        start = _parse_date(start)
    if end:
        end = _parse_date(end)
    account_filter = int(account_id) if account_id is not None else None
    rows = storage.list_income(start_date=start, end_date=end, account_id=account_filter)
    return jsonify(rows)


@app.route("/income", methods=["POST"])
def create_income():
    data = request.get_json(force=True, silent=True) or {}
    account_id = int(data.get("account_id"))
    date = _parse_date(data.get("date", ""))
    amount = float(data.get("amount"))
    source = data.get("source", "")
    created = storage.create_income(account_id=account_id, date=date, amount=amount, source=source)
    return jsonify(created), 201


@app.route("/income/<int:income_id>", methods=["DELETE"])
def delete_income(income_id: int):
    storage.delete_income(income_id)
    return jsonify({"deleted": True})


# Statistics ---------------------------------------------------------------
@app.route("/stats/summary", methods=["GET"])
def stats_summary():
    start = request.args.get("from")
    end = request.args.get("to")
    kind = (request.args.get("kind") or "transactions").lower()
    if start:
        start = _parse_date(start)
    if end:
        end = _parse_date(end)

    if kind == "income":
        records = storage.list_income(start_date=start, end_date=end)
    else:
        records = storage.list_transactions(start_date=start, end_date=end)
    summary = summarize_amounts(records)
    return jsonify(summary)


@app.route("/stats/income_forecast", methods=["GET"])
def stats_income_forecast():
    months = _parse_months(request.args.get("months"), default=3)
    history = storage.monthly_income()
    payload = forecast_income(history, months_ahead=months)
    return jsonify(payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
