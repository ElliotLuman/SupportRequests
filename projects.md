# Internal Workflow API Reporter

## Why It Matches

This project matches Illumynt's emphasis on internal systems, frontend and backend application support, APIs, SQL, reports, testing, GitHub, and translating business requirements into technical work. It gives Elliot a practical example to discuss without pretending to have ITAD or reverse logistics production experience.

## One-Hour Scope

Build a small local Python Flask API with SQLite storage and a simple JavaScript dashboard that tracks internal support requests, validates required fields, and reports request counts by status.

## Tech Stack

Python, Flask, SQLite, SQL, JavaScript, HTML/CSS, GitHub, pytest-style validation checklist.

## Features

- REST-style endpoints for creating, listing, and updating support requests.
- SQLite table for requester, category, priority, status, owner, and notes.
- SQL report for open, blocked, and resolved work.
- Small JavaScript dashboard that fetches API data and renders a status table.
- Validation for missing category, invalid status, and empty owner.
- Markdown test checklist covering API responses, SQL output, and dashboard behavior.

## File Structure

- `app.py`
- `schema.sql`
- `static/dashboard.js`
- `templates/index.html`
- `tests/test-checklist.md`
- `README.md`

## Implementation Steps

1. Define request fields and allowed statuses.
2. Create the SQLite schema and seed sample records.
3. Add Flask routes for create, list, update, and report.
4. Write SQL queries for status and priority summaries.
5. Build a minimal JavaScript dashboard using `fetch`.
6. Document setup, run commands, and validation cases.

## Test Or Demo Plan

Run the Flask app locally, create three sample requests, update one status, verify the SQL report totals, and confirm the dashboard refreshes from the API output.

## Resume Entry

Internal Workflow API Reporter

- Built Python/Flask internal workflow app with SQLite reporting, JavaScript dashboard, API endpoints, and validation tests for support-request tracking.

## Interview Talking Points

- How the app turns simple business requirements into database fields and API behavior.
- Why validation and test checklists matter for internal systems.
- How SQL reporting supports operational visibility.
- How the project could integrate with GitHub issues, Jira, Power BI, or ITAD workflow data later.
