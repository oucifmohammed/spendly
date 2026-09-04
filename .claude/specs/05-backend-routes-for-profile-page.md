# Spec: Backend Routes for Profile Page

## Overview
Step 4 built `/profile` with a fully designed layout but every value it shows — user info, summary stats, recent transactions, category breakdown — is a hardcoded Python dict in `app.py`. This step is the "backend-connection step" that spec 04 explicitly deferred: replace that hardcoded data with real queries against the `users` and `expenses` tables, scoped to the logged-in user, so the profile page reflects that user's actual account and spending instead of the demo mock.

## Depends on
- Step 1: Database setup (`users`/`expenses` schema, `get_db()`)
- Step 2: Registration (accounts exist to query)
- Step 3: Login and Logout (`session["user_id"]` is set for the current visitor)
- Step 4: Profile Page (route, auth guard, `templates/profile.html`, `static/css/profile.css` already exist and are not changing shape)

## Routes
- `GET /profile` — already exists — logged-in only (unchanged: redirect to `/login` if `session.get("user_id")` is absent). No new routes; this step changes the view function's body only, not its signature or access level.

## Database changes
No schema changes — `users` and `expenses` already have every column needed. Verified against `database/db.py`. New read-only query functions are added to `database/db.py` (see below), but no new tables or columns.

## Templates
- **Create:** none
- **Modify:** none — `templates/profile.html` already consumes `user`, `stats`, `transactions`, `categories` with the exact field names below; the route must keep producing those same shapes so the template needs no changes.

## Files to change
- `app.py` — rewrite the `/profile` view to:
  - Fetch the current user via a new `get_user_by_id()` call instead of hardcoding `user`
  - Compute `stats`, `transactions`, and `categories` from the database instead of hardcoded lists
- `database/db.py` — add:
  - `get_user_by_id(user_id)` — parameterized `SELECT * FROM users WHERE id = ?`, returns row or `None`
  - `get_recent_expenses(user_id, limit=5)` — parameterized `SELECT ... WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?`
  - `get_monthly_total(user_id, year, month)` — parameterized `SUM(amount)` for that user/month (0 if none)
  - `get_monthly_transaction_count(user_id, year, month)` — parameterized `COUNT(*)` for that user/month
  - `get_monthly_category_totals(user_id, year, month)` — parameterized `GROUP BY category` totals for that user/month, ordered by total descending

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never string-format SQL, never interpolate `user_id`/dates into a query string
- Passwords hashed with werkzeug (unchanged in this step — no auth logic touched)
- Use CSS variables — never hardcode hex values (n/a, no CSS touched — listed for consistency)
- All templates extend `base.html` (n/a, no templates touched — listed for consistency)
- All new query functions live in `database/db.py` only — no inline SQL in `app.py`
- Every query must filter by the logged-in user's `user_id` — never return another user's rows
- "Total Spent", "Transactions", and "Category Breakdown" are scoped to the **current calendar month** (matches the Step 4 mock's framing)
- Top Category's `delta` is that category's percentage share of the month's total spend (e.g. `"35% of spend"`), not a month-over-month comparison; its `trend` is always `"neutral"`
- Total Spent's `delta`/`trend` compares this month's total to last month's total: `trend="negative"` if spend increased, `"positive"` if it decreased, `"neutral"` if there's no prior-month data or no change
- Transactions' `delta` compares this month's count to last month's count; `trend` is always `"neutral"`
- Category bar widths must map each category's percentage to the nearest available `bar-w-*` CSS class (5% increments, `bar-w-5` through `bar-w-100`) — never emit a width class that doesn't exist in `profile.css`
- Currency values are formatted as `₹{amount:,.2f}` strings in the route before being passed to the template — `profile.html` prints values directly with no Jinja number filters
- Dates in the transactions table are formatted as `"%b %d, %Y"` (e.g. `Aug 24, 2026`) in the route before being passed to the template
- If the user has zero expenses this month, stats must show zero values, `transactions` must be an empty list, and `categories` must be an empty list — the page must render without error, never raise
- Do not implement `/expenses/add`, `/expenses/<id>/edit`, or `/expenses/<id>/delete` — those remain stubs for later steps

## Definition of done
- [ ] Visiting `/profile` without being logged in still redirects to `/login`
- [ ] Visiting `/profile` logged in as the seeded demo user shows that user's real name, email, and member-since date — not the hardcoded "Demo User" placeholder
- [ ] Total Spent reflects the actual sum of the logged-in user's expenses dated in the current calendar month
- [ ] Transactions reflects the actual count of the logged-in user's expenses dated in the current calendar month
- [ ] Top Category reflects the category with the highest spend for the logged-in user this month, with its correct percentage share
- [ ] Recent Transactions shows the logged-in user's actual expense rows, most recent first, with formatted date/amount strings — not the hardcoded mock rows
- [ ] Category Breakdown shows the logged-in user's actual per-category totals and percentages for the current month, with `bar-w-*` classes matching the percentages
- [ ] Registering a second account with its own expenses and viewing `/profile` while logged in as that account shows only that account's data, never the demo user's
- [ ] A logged-in user with zero expenses this month sees the page render successfully with zero/empty states, no server error
- [ ] `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete` are untouched and still return their Step-N stub responses
