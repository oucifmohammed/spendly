import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash

from database.db import get_db, init_db, seed_db, create_user, get_user_by_email

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

    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "initials": "DU",
        "member_since": "March 2024",
    }

    stats = [
        {"label": "Total Spent", "value": "$1,248.50"},
        {"label": "Transactions", "value": "24"},
        {"label": "Top Category", "value": "Food"},
    ]

    transactions = [
        {"date": "Aug 24, 2026", "description": "Grocery shopping", "category": "Food", "amount": "$45.50"},
        {"date": "Aug 22, 2026", "description": "Monthly bus pass", "category": "Transport", "amount": "$30.00"},
        {"date": "Aug 20, 2026", "description": "Electricity bill", "category": "Bills", "amount": "$85.00"},
        {"date": "Aug 18, 2026", "description": "Movie tickets", "category": "Entertainment", "amount": "$22.99"},
        {"date": "Aug 15, 2026", "description": "New shoes", "category": "Shopping", "amount": "$150.00"},
    ]

    categories = [
        {"category": "Food", "amount": "$437.00", "percent": 35, "width_class": "bar-w-35"},
        {"category": "Transport", "amount": "$249.70", "percent": 20, "width_class": "bar-w-20"},
        {"category": "Bills", "amount": "$324.60", "percent": 25, "width_class": "bar-w-25"},
        {"category": "Entertainment", "amount": "$112.40", "percent": 10, "width_class": "bar-w-10"},
        {"category": "Shopping", "amount": "$124.80", "percent": 10, "width_class": "bar-w-10"},
    ]

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
