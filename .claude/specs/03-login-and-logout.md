# Spec: Login and Logout

## Overview
This feature lets an existing user authenticate with their email and password, and end that session on demand. It follows directly from the Registration feature: `create_user()` and the `users` table (with `password_hash`) already exist, but there is no way yet to turn a submitted email/password pair into an authenticated session, no way to know who the current visitor is, and no way to sign out. This step adds session-based login, wires session state into the shared nav, and implements real logout behavior in place of the current stub.

## Depends on
- Step 01/02 — Registration (`users` table, `create_user()`, `register.html`, password hashing with werkzeug)

## Routes
- `POST /login` — authenticate email + password, start a session, redirect to `/` — public
- `GET /login` — already implemented (renders `login.html`) — no change needed
- `GET /logout` — clear the session and redirect to `/` — logged-in (replaces current stub)

## Database changes
No database changes. The `users` table already has `email` and `password_hash` columns, which is everything login needs. Verified against `database/db.py`.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — no structural change; the existing `POST` form to `/login` already matches the new route (currently posts to the literal string `/login` — leave as is or switch to `url_for('login')` for consistency with the rest of the codebase)
  - `templates/base.html` — the nav currently hardcodes "Sign in" / "Get started" links for every visitor. Update it to check session state: when logged in, show a greeting (e.g. the user's name) and a "Logout" link (`url_for('logout')`); when logged out, keep the existing "Sign in" / "Get started" links.

## Files to change
- `app.py`
  - Set `app.secret_key` (required for Flask `session` to sign cookies)
  - Implement `POST /login`: look up the user by email, verify password with `check_password_hash`, store the user id in `session["user_id"]` on success, re-render `login.html` with an error on failure (invalid email or password — use one generic error message for both so login doesn't leak which emails are registered)
  - Implement `GET /logout`: `session.clear()`, redirect to `url_for('landing')`
- `database/db.py`
  - Add `get_user_by_email(email)` — parameterized `SELECT` returning the user row (or `None`)
- `templates/base.html`
  - Read session state to switch the nav between logged-in and logged-out views

## Files to create
None.

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` is already available (its counterpart `generate_password_hash` is already used in `database/db.py`). Flask's built-in `session` needs only `app.secret_key` to be set.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords verified with werkzeug (`check_password_hash`), never compared as plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- DB logic stays in `database/db.py`, never inline in routes
- Use `url_for()` for every internal link — never hardcode URLs
- Login failure must return one generic error message regardless of whether the email exists or the password is wrong (don't leak account existence)
- Do not implement `/profile`, `/expenses/add`, `/expenses/<id>/edit`, or `/expenses/<id>/delete` — those remain stubs for later steps, even when adding nav links

## Definition of done
- [ ] Visiting `/login` and submitting the seeded demo account (`demo@spendly.com` / `demo123`) logs in and redirects to `/`
- [ ] After logging in, the nav on every page shows a logged-in state (greeting + Logout link) instead of "Sign in" / "Get started"
- [ ] Submitting `/login` with a wrong password shows a generic error and does not log the user in
- [ ] Submitting `/login` with an email that doesn't exist shows the same generic error (no distinct message)
- [ ] Visiting `/logout` while logged in clears the session and redirects to `/`, and the nav reverts to the logged-out state
- [ ] Restarting the Flask dev server and reloading `/` does not keep a previous session logged in unless the session cookie is still valid (i.e. no server-side session state is lost in a way that breaks logout)
- [ ] `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete` are untouched and still return their Step-N stub responses
