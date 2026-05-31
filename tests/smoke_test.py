import os
import sqlite3
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "support_requests.db"
        os.environ["DATABASE_PATH"] = str(temp_path)

        import app as support_app

        support_app.init_db()
        client = support_app.app.test_client()

        index_response = client.get("/")
        assert_equal(index_response.status_code, 200, "GET / should return HTML")

        list_response = client.get("/api/requests")
        assert_equal(list_response.status_code, 200, "GET /api/requests should succeed")
        requests = list_response.get_json()["requests"]
        assert_equal(len(requests), 3, "Seeded request count")

        status_report = client.get("/api/reports/status").get_json()["counts"]
        priority_report = client.get("/api/reports/priority").get_json()["counts"]
        assert_equal(
            status_report,
            [
                {"label": "open", "count": 1},
                {"label": "blocked", "count": 1},
                {"label": "resolved", "count": 1},
            ],
            "Initial status report",
        )
        assert_equal(
            priority_report,
            [
                {"label": "low", "count": 0},
                {"label": "medium", "count": 1},
                {"label": "high", "count": 1},
                {"label": "critical", "count": 1},
            ],
            "Initial priority report",
        )

        create_response = client.post(
            "/api/requests",
            json={
                "requester": "Smoke Test",
                "category": "Reporting",
                "priority": "critical",
                "status": "open",
                "owner": "Elliot",
                "notes": "Created during smoke verification.",
            },
        )
        assert_equal(create_response.status_code, 201, "POST /api/requests should create")
        created = create_response.get_json()

        update_response = client.patch(
            f"/api/requests/{created['id']}",
            json={"status": "resolved", "owner": "Casey"},
        )
        assert_equal(update_response.status_code, 200, "PATCH /api/requests should update")
        updated = update_response.get_json()
        assert_equal(updated["status"], "resolved", "Updated request status")
        assert_equal(updated["owner"], "Casey", "Updated request owner")

        invalid_response = client.post(
            "/api/requests",
            json={
                "requester": "Smoke Test",
                "category": "   ",
                "priority": "critical",
                "status": "open",
                "owner": "Elliot",
            },
        )
        assert_equal(invalid_response.status_code, 400, "Blank category should fail")

        missing_response = client.patch("/api/requests/999", json={"status": "resolved"})
        assert_equal(missing_response.status_code, 404, "Missing request should 404")

        status_after = client.get("/api/reports/status").get_json()["counts"]
        priority_after = client.get("/api/reports/priority").get_json()["counts"]
        assert_equal(
            status_after,
            [
                {"label": "open", "count": 1},
                {"label": "blocked", "count": 1},
                {"label": "resolved", "count": 2},
            ],
            "Status report after update",
        )
        assert_equal(
            priority_after,
            [
                {"label": "low", "count": 0},
                {"label": "medium", "count": 1},
                {"label": "high", "count": 1},
                {"label": "critical", "count": 2},
            ],
            "Priority report after create",
        )

        with sqlite3.connect(temp_path) as connection:
            status_rows = connection.execute(
                "select status, count(*) from support_requests group by status order by status"
            ).fetchall()
            priority_rows = connection.execute(
                "select priority, count(*) from support_requests group by priority order by priority"
            ).fetchall()

        assert_equal(
            status_rows,
            [("blocked", 1), ("open", 1), ("resolved", 2)],
            "Direct SQL status totals",
        )
        assert_equal(
            priority_rows,
            [("critical", 2), ("high", 1), ("medium", 1)],
            "Direct SQL priority totals",
        )

        print("Smoke test passed.")


if __name__ == "__main__":
    main()
