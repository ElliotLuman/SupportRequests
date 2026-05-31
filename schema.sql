DROP TABLE IF EXISTS support_requests;

CREATE TABLE support_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL CHECK (status IN ('open', 'blocked', 'resolved')),
    owner TEXT NOT NULL,
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'now')),
    updated_at TEXT NOT NULL DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'now'))
);

INSERT INTO support_requests (
    requester,
    category,
    priority,
    status,
    owner,
    notes
) VALUES
    (
        'Alex Rivera',
        'Access',
        'high',
        'open',
        'Elliot',
        'Needs access to the reporting folder before month-end close.'
    ),
    (
        'Jordan Lee',
        'Incident',
        'critical',
        'blocked',
        'Casey',
        'Waiting on upstream vendor confirmation for intermittent API failures.'
    ),
    (
        'Taylor Morgan',
        'Hardware',
        'medium',
        'resolved',
        'Riley',
        'Replacement scanner deployed and verified with receiving team.'
    );
