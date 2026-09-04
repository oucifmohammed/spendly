import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash

from datetime import date, datetime

from database.db import (
    get_db,
    init_db,
    seed_db,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_recent_expenses,
    get_monthly_total,
    get_monthly_transaction_count,
    get_monthly_category_totals,
)

app = Flask(__name__)
app.secret_key = "dev-only-secret-key-change-in-production"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name or not email or not password:
        return render_template("register.html", error="All fields are required.")

    if len(password) < 8:
        return render_template(
            "register.html", error="Password must be at least 8 characters long."
        )

    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        return render_template(
            "register.html", error="An account with this email already exists."
        )

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = get_user_by_email(email)

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return redirect(url_for("landing"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    today = date.today()
    year, month = today.year, today.month

    db_user = get_user_by_id(user_id)
    initials = "".join(part[0].upper() for part in db_user["name"].split()[:2]) or "?"
    member_since = datetime.strptime(db_user["created_at"][:10], "%Y-%m-%d").strftime("%B %Y")
    user = {
        "name": db_user["name"],
        "email": db_user["email"],
        "initials": initials,
        "member_since": member_since,
    }

    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    this_month_total = get_monthly_total(user_id, year, month)
    last_month_total = get_monthly_total(user_id, prev_year, prev_month)
    if last_month_total == 0:
        spend_delta, spend_trend = "No data for last month", "neutral"
    elif this_month_total == last_month_total:
        spend_delta, spend_trend = "No change vs last month", "neutral"
    else:
        pct_change = (this_month_total - last_month_total) / last_month_total * 100
        spend_delta = f"{pct_change:+.1f}% vs last month"
        spend_trend = "negative" if pct_change > 0 else "positive"

    this_month_count = get_monthly_transaction_count(user_id, year, month)
    last_month_count = get_monthly_transaction_count(user_id, prev_year, prev_month)
    count_delta = f"{this_month_count - last_month_count:+d} vs last month"

    category_totals = get_monthly_category_totals(user_id, year, month)
    if category_totals:
        top = category_totals[0]
        top_percent = (top["total"] / this_month_total * 100) if this_month_total else 0
        top_value, top_delta = top["category"], f"{top_percent:.0f}% of spend"
    else:
        top_value, top_delta = "—", "No data"

    stats = [
        {"label": "Total Spent", "value": f"₹{this_month_total:,.2f}", "delta": spend_delta, "trend": spend_trend},
        {"label": "Transactions", "value": str(this_month_count), "delta": count_delta, "trend": "neutral"},
        {"label": "Top Category", "value": top_value, "delta": top_delta, "trend": "neutral"},
    ]

    recent_expenses = get_recent_expenses(user_id, limit=5)
    transactions = [
        {
            "date": datetime.strptime(row["date"], "%Y-%m-%d").strftime("%b %d, %Y"),
            "description": row["description"] or "",
            "category": row["category"],
            "amount": f"₹{row['amount']:,.2f}",
        }
        for row in recent_expenses
    ]

    category_total_for_month = get_monthly_total(user_id, year, month)
    category_rows = get_monthly_category_totals(user_id, year, month)
    categories = []
    for row in category_rows:
        amount = row["total"]
        raw_percent = (amount / category_total_for_month * 100) if category_total_for_month else 0
        bar_percent = max(5, min(100, int(round(raw_percent / 5) * 5)))
        categories.append({
            "category": row["category"],
            "amount": f"₹{amount:,.2f}",
            "percent": round(raw_percent),
            "width_class": f"bar-w-{bar_percent}",
        })

    return render_template(
        "profile.html", user=user, stats=stats,
        transactions=transactions, categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


with app.app_context():
    init_db()
    seed_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
