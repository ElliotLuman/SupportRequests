# Test Checklist

## Manual Verification

- [ ] Create a virtual environment with `python3 -m venv .venv`.
- [ ] Install dependencies with `pip install -r requirements.txt`.
- [ ] Run `python tests/smoke_test.py` and confirm it prints `Smoke test passed.`
- [ ] Start the app with `flask --app app run --debug`.
- [ ] Open `http://127.0.0.1:5000` and confirm the dashboard HTML renders.
- [ ] Initialize the database with `sqlite3 support_requests.db < schema.sql`.
- [ ] Run `sqlite3 support_requests.db "select id, requester, status from support_requests order by id;"` and confirm the seeded rows include `open`, `blocked`, and `resolved`.
- [ ] Request `http://127.0.0.1:5000/api/requests` and confirm it returns the seeded requests as JSON.
- [ ] `POST /api/requests` with a valid JSON body returns `201` and the created request.
- [ ] `PATCH /api/requests/<id>` with a valid JSON body returns `200` and the updated request.
- [ ] Creating with a blank `category` returns `400`.
- [ ] Creating or updating with an invalid `status` returns `400`.
- [ ] Creating or updating with an invalid `priority` returns `400`.
- [ ] Creating or updating with a blank `owner` returns `400`.
- [ ] Patching a missing request ID returns `404`.
- [ ] `GET /api/reports/status` returns counts for `open`, `blocked`, and `resolved`.
- [ ] `GET /api/reports/priority` returns counts for `low`, `medium`, `high`, and `critical`.
- [ ] Direct SQL `GROUP BY` totals match the report endpoint totals.
- [ ] Opening `/` shows seeded requests and both summary sections after the database is initialized.
- [ ] Creating a request from the page refreshes the request table and summary counts.
- [ ] Updating status or owner from the page refreshes the request table and summary counts.
- [ ] Invalid form submission shows a visible error in the page.
- [ ] Confirm the dashboard no longer shows an API error after loading.
