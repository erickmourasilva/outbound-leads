"""SQLite storage for the outreach engine (extract -> segment -> send gradually).

Single source of truth. Replies and conversations live in the CRM that takes over after a reply, not here.
"""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("OUTBOUND_DB", os.path.join(ROOT, "data", "outbound.db"))

# Lead kinds: client (prospect), partner (agency/integrator/reseller), intel (competitor probing)
KINDS = ("client", "partner", "intel")
# Status flow: discovered -> qualified -> approved -> queued -> sent
# Side exits: skipped, failed, do_not_contact
STATUSES = ("discovered", "qualified", "approved", "queued", "sent", "failed", "skipped", "do_not_contact")

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS leads (
    id            INTEGER PRIMARY KEY,
    kind          TEXT NOT NULL CHECK (kind IN ('client','partner','intel')),
    segment       TEXT NOT NULL DEFAULT '',
    name          TEXT NOT NULL,
    handle        TEXT NOT NULL UNIQUE,           -- instagram handle without @, lowercase
    source_kind   TEXT NOT NULL DEFAULT '',       -- news | job | maps | competitor_directory | competitor_followers | manual
    source_ref    TEXT NOT NULL DEFAULT '',       -- competitor or directory the lead came from
    source_url    TEXT NOT NULL DEFAULT '',
    signal        TEXT NOT NULL DEFAULT '',       -- public signal that justifies the contact
    signal_date   TEXT NOT NULL DEFAULT '',
    score         INTEGER NOT NULL DEFAULT 0,
    status        TEXT NOT NULL DEFAULT 'discovered'
                  CHECK (status IN ('discovered','qualified','approved','queued','sent','failed','skipped','do_not_contact')),
    variant       TEXT NOT NULL DEFAULT '',
    message_text  TEXT NOT NULL DEFAULT '',
    scheduled_at  TEXT,
    sent_at       TEXT,
    notes         TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_kind ON leads(kind);

CREATE TABLE IF NOT EXISTS sends (
    id            INTEGER PRIMARY KEY,
    lead_id       INTEGER NOT NULL REFERENCES leads(id),
    sent_at       TEXT NOT NULL,
    result        TEXT NOT NULL,                  -- ok | failed | blocked_by_instagram | not_accepting
    variant       TEXT NOT NULL DEFAULT '',
    message_text  TEXT NOT NULL DEFAULT '',
    error         TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_sends_sent_at ON sends(sent_at);

CREATE TABLE IF NOT EXISTS do_not_contact (
    handle     TEXT PRIMARY KEY,
    reason     TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id         INTEGER PRIMARY KEY,
    at         TEXT NOT NULL,
    level      TEXT NOT NULL DEFAULT 'info',     -- info | warn | pause
    message    TEXT NOT NULL
);
"""

DEFAULT_SETTINGS = {
    "paused": "1",                      # sending stays OFF until the operator turns it on
    "warmup_start": "",                 # YYYY-MM-DD of the first sending day (set when sending starts)
    "base_daily": "5",                  # DMs per day in the first week
    "weekly_step": "5",                 # +N DMs/day each following week
    "max_daily": "30",                  # hard ceiling
    "hours_start": "09:00",
    "hours_end": "20:00",
    "weekdays_only": "1",
    "min_seconds_between": "90",
    "max_seconds_between": "240",
    "timezone": "America/Sao_Paulo",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_handle(handle: str) -> str:
    return handle.strip().lstrip("@").rstrip("/").lower()


@contextmanager
def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA busy_timeout = 10000")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init() -> None:
    with connect() as con:
        con.executescript(SCHEMA)
        for k, v in DEFAULT_SETTINGS.items():
            con.execute("INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)", (k, v))


def get_settings(con) -> dict:
    return {r["key"]: r["value"] for r in con.execute("SELECT key, value FROM settings")}


def log_event(con, message: str, level: str = "info") -> None:
    con.execute("INSERT INTO events(at, level, message) VALUES (?, ?, ?)", (now_utc(), level, message))


def add_lead(con, *, kind: str, name: str, handle: str, segment: str = "", source_kind: str = "",
             source_ref: str = "", source_url: str = "", signal: str = "", signal_date: str = "",
             score: int = 0, status: str = "discovered", variant: str = "", message_text: str = "",
             sent_at: str | None = None, notes: str = "") -> bool:
    """Insert a lead. Returns False when the handle already exists or is on the do-not-contact list."""
    h = normalize_handle(handle)
    if not h:
        return False
    if con.execute("SELECT 1 FROM do_not_contact WHERE handle = ?", (h,)).fetchone():
        return False
    ts = now_utc()
    try:
        con.execute(
            """INSERT INTO leads(kind, segment, name, handle, source_kind, source_ref, source_url, signal,
                                 signal_date, score, status, variant, message_text, sent_at, notes, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (kind, segment, name, h, source_kind, source_ref, source_url, signal, signal_date, score,
             status, variant, message_text, sent_at, notes, ts, ts),
        )
    except sqlite3.IntegrityError:
        return False
    return True
