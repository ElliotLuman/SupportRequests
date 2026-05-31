import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE_PATH = BASE_DIR / "support_requests.db"
ALLOWED_STATUSES = ("open", "blocked", "resolved")
ALLOWED_PRIORITIES = ("low", "medium", "high", "critical")


def get_database_path():
    return Path(os.environ.get("DATABASE_PATH", DEFAULT_DATABASE_PATH))


def get_db_connection():
    connection = sqlite3.connect(get_database_path())
    connection.row_factory = sqlite3.Row
    return connection


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


def row_to_dict(row):
    return dict(row) if row is not None else None


def init_db():
    schema_path = BASE_DIR / "schema.sql"

    with sqlite3.connect(get_database_path()) as connection:
        connection.executescript(schema_path.read_text())
        connection.commit()


def fetch_request_by_id(connection, request_id):
    return connection.execute(
        """
        SELECT
            id,
            requester,
            category,
            priority,
            status,
            owner,
            notes,
            created_at,
            updated_at
        FROM support_requests
        WHERE id = ?
        """,
        (request_id,),
    ).fetchone()


def validate_request_payload(payload, *, partial=False):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."

    allowed_fields = {"requester", "category", "priority", "status", "owner", "notes"}
    required_fields = {"requester", "category", "priority", "status", "owner"}

    unknown_fields = sorted(set(payload) - allowed_fields)
    if unknown_fields:
        return f"Unknown fields: {', '.join(unknown_fields)}."

    if partial and not payload:
        return "At least one updatable field is required."

    if not partial:
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}."

    text_fields = {"requester", "category", "owner"}
    for field in text_fields:
        if field in payload and not str(payload[field]).strip():
            return f"{field.capitalize()} cannot be blank."

    if "status" in payload and payload["status"] not in ALLOWED_STATUSES:
        return f"Status must be one of: {', '.join(ALLOWED_STATUSES)}."

    if "priority" in payload and payload["priority"] not in ALLOWED_PRIORITIES:
        return f"Priority must be one of: {', '.join(ALLOWED_PRIORITIES)}."

    if "notes" in payload and payload["notes"] is None:
        return "Notes cannot be null."

    return None


def normalize_request_payload(payload):
    normalized = {}

    for key, value in payload.items():
        if key in {"requester", "category", "priority", "status", "owner"}:
            normalized[key] = str(value).strip()
        elif key == "notes":
            normalized[key] = str(value).strip()

    return normalized


def fetch_group_counts(connection, column_name, allowed_values):
    placeholders = ", ".join("?" for _ in allowed_values)
    rows = connection.execute(
        f"""
        SELECT {column_name} AS label, COUNT(*) AS count
        FROM support_requests
        WHERE {column_name} IN ({placeholders})
        GROUP BY {column_name}
        """,
        allowed_values,
    ).fetchall()

    counts_by_label = {row["label"]: row["count"] for row in rows}
    return [
        {"label": value, "count": counts_by_label.get(value, 0)}
        for value in allowed_values
    ]


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/requests")
    def list_requests():
        with get_db_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    requester,
                    category,
                    priority,
                    status,
                    owner,
                    notes,
                    created_at,
                    updated_at
                FROM support_requests
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()

        return jsonify({"requests": rows_to_dicts(rows)})

    @app.post("/api/requests")
    def create_request():
        payload = request.get_json(silent=True)
        error = validate_request_payload(payload, partial=False)
        if error:
            return jsonify({"error": error}), 400

        request_data = normalize_request_payload(payload)

        with get_db_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO support_requests (
                    requester,
                    category,
                    priority,
                    status,
                    owner,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    request_data["requester"],
                    request_data["category"],
                    request_data["priority"],
                    request_data["status"],
                    request_data["owner"],
                    request_data.get("notes", ""),
                ),
            )
            created_row = fetch_request_by_id(connection, cursor.lastrowid)
            connection.commit()

        return jsonify(row_to_dict(created_row)), 201

    @app.patch("/api/requests/<int:request_id>")
    def update_request(request_id):
        payload = request.get_json(silent=True)
        error = validate_request_payload(payload, partial=True)
        if error:
            return jsonify({"error": error}), 400

        request_data = normalize_request_payload(payload)

        with get_db_connection() as connection:
            existing_row = fetch_request_by_id(connection, request_id)
            if existing_row is None:
                return jsonify({"error": f"Support request {request_id} was not found."}), 404

            assignments = [f"{field} = ?" for field in request_data]
            assignments.append("updated_at = STRFTIME('%Y-%m-%d %H:%M:%f', 'now')")
            values = list(request_data.values()) + [request_id]

            connection.execute(
                f"""
                UPDATE support_requests
                SET {", ".join(assignments)}
                WHERE id = ?
                """,
                values,
            )
            updated_row = fetch_request_by_id(connection, request_id)
            connection.commit()

        return jsonify(row_to_dict(updated_row))

    @app.get("/api/reports/status")
    def status_report():
        with get_db_connection() as connection:
            counts = fetch_group_counts(connection, "status", ALLOWED_STATUSES)

        return jsonify({"counts": counts})

    @app.get("/api/reports/priority")
    def priority_report():
        with get_db_connection() as connection:
            counts = fetch_group_counts(connection, "priority", ALLOWED_PRIORITIES)

        return jsonify({"counts": counts})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
