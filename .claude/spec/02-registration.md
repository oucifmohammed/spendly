# Spec: Registration

## Overview
Implements account creation for Spendly. The `GET /register` route already renders `register.html`, but there is no backend logic to actually create a user — submitting the form does nothing. This step wires up `POST /register` so visitors can create an account backed by the `users` table (added in Step 1), with hashed passwords and duplicate-email handling. Login/session logic is out of scope — after a successful registration the user is redirected to the login page.

## Depends on
Step 1 — Database Setup. Requires the `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) and `get_db()` to already exist in `database/db.py`.

## Routes
- `POST /register` — accepts the registration form, creates a user, redirects to login on success or re-renders the form with an error on failure — public

`GET /register` already exists and is unchanged; only the route's allowed methods and body grow to handle `POST`.

## Database changes
No database changes. The `users` table created in Step 1 already has every column registration needs (`name`, `email`, `password_hash`).

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — the form's `action="/register"` is hardcoded; change it to `action="{{ url_for('register') }}"` per the no-hardcoded-URLs rule. No other markup changes — the `{% if error %}` block already in the template is reused to surface validation/duplicate-email errors.

## Files to change
- `app.py` — change the `/register` route to accept `methods=["GET", "POST"]`; on `POST`, read `name`/`email`/`password` from the form, validate them, call the new `create_user()` helper, and either redirect to `/login` on success or re-render `register.html` with an `error` message on failure.
- `database/db.py` — add `create_user(name, email, password)`: hashes the password with `werkzeug.security.generate_password_hash` (same pattern already used in `seed_db()`), inserts the row with a parameterized query, and returns the new user's id. Duplicate-email inserts raise `sqlite3.IntegrityError` naturally (the `email` column is already `UNIQUE`) — let it propagate so the route can catch it and show a friendly error.
- `templates/register.html` — fix the hardcoded form action (see Templates above).

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security` is already used in `database/db.py`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- All DB logic (the insert, the password hashing) lives in `database/db.py`, not inline in the route
- Validate required fields (`name`, `email`, `password` all non-empty) and a minimum password length of 8 characters (matches the existing "Min. 8 characters" placeholder) before calling `create_user()`
- Catch the duplicate-email case (`sqlite3.IntegrityError`) in the route and re-render `register.html` with `error="An account with this email already exists."` — never let the exception surface as a 500
- Use `redirect(url_for('login'))` on success — no hardcoded `/login` path

## Definition of done
- [ ] `GET /register` still renders the registration form correctly
- [ ] Submitting valid name/email/password creates a new row in `users` with a hashed password (verify via sqlite3 CLI or a Python script — `password_hash` must not equal the plaintext password and must start with a werkzeug hash prefix)
- [ ] After successful registration, the browser is redirected to `/login`
- [ ] Submitting a duplicate email re-renders `register.html` with a visible error and does not create a second row for that email
- [ ] Submitting with any required field empty shows a validation error and inserts no row
- [ ] Submitting a password under 8 characters shows a validation error and inserts no row
- [ ] All new SQL statements use `?` placeholders — no string formatting
- [ ] `templates/register.html`'s form no longer hardcodes `/register` as its action
