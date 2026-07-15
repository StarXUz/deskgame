import asyncio
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "tournament.sqlite3"

write_lock = asyncio.Lock()


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                team_name TEXT NOT NULL,
                district TEXT,
                school TEXT,
                team_code TEXT,
                player_code TEXT,
                player_qr_token TEXT UNIQUE,
                age_group TEXT NOT NULL,
                game_type TEXT NOT NULL,
                seed_rank INTEGER NOT NULL UNIQUE,
                is_active INTEGER NOT NULL DEFAULT 1,
                is_transition INTEGER NOT NULL DEFAULT 0,
                transition_choice TEXT,
                identity_label TEXT NOT NULL DEFAULT '正常'
            );

            CREATE TABLE IF NOT EXISTS rounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_no INTEGER NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT '未开始'
            );

            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_id INTEGER NOT NULL,
                table_no TEXT NOT NULL,
                age_group TEXT NOT NULL,
                game_type TEXT NOT NULL,
                player_ids_json TEXT NOT NULL,
                is_bye INTEGER NOT NULL DEFAULT 0,
                participant_count INTEGER NOT NULL,
                has_free_agent INTEGER NOT NULL DEFAULT 0,
                seat_no TEXT,
                token TEXT UNIQUE,
                token_created_at TEXT,
                submitted_at TEXT,
                FOREIGN KEY(round_id) REFERENCES rounds(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                round_id INTEGER NOT NULL,
                table_id INTEGER NOT NULL,
                table_rank INTEGER,
                round_score INTEGER NOT NULL DEFAULT 0,
                is_absent INTEGER NOT NULL DEFAULT 0,
                is_advanced INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(player_id) REFERENCES players(id) ON DELETE CASCADE,
                FOREIGN KEY(round_id) REFERENCES rounds(id) ON DELETE CASCADE,
                FOREIGN KEY(table_id) REFERENCES tables(id) ON DELETE CASCADE,
                UNIQUE(player_id, round_id)
            );

            CREATE TABLE IF NOT EXISTS judges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                initial_password TEXT,
                claimed_by TEXT,
                note TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login_at TEXT
            );

            CREATE TABLE IF NOT EXISTS judge_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judge_id INTEGER NOT NULL,
                round_id INTEGER NOT NULL,
                table_id INTEGER NOT NULL,
                judge_name TEXT,
                submitted_at TEXT NOT NULL,
                client_ip TEXT,
                user_agent TEXT,
                scores_json TEXT NOT NULL,
                FOREIGN KEY(judge_id) REFERENCES judges(id) ON DELETE CASCADE,
                FOREIGN KEY(round_id) REFERENCES rounds(id) ON DELETE CASCADE,
                FOREIGN KEY(table_id) REFERENCES tables(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS score_corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_id INTEGER NOT NULL,
                table_id INTEGER NOT NULL,
                original_judge_submission_id INTEGER,
                operator_name TEXT NOT NULL,
                reason TEXT NOT NULL,
                corrected_at TEXT NOT NULL,
                old_scores_json TEXT NOT NULL,
                new_scores_json TEXT NOT NULL,
                FOREIGN KEY(round_id) REFERENCES rounds(id) ON DELETE CASCADE,
                FOREIGN KEY(table_id) REFERENCES tables(id) ON DELETE CASCADE,
                FOREIGN KEY(original_judge_submission_id) REFERENCES judge_submissions(id) ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_players_pool
                ON players(age_group, game_type, is_active);
            CREATE INDEX IF NOT EXISTS idx_players_code
                ON players(player_code);
            CREATE INDEX IF NOT EXISTS idx_players_team
                ON players(team_name, game_type, identity_label);
            CREATE INDEX IF NOT EXISTS idx_tables_round
                ON tables(round_id);
            CREATE INDEX IF NOT EXISTS idx_tables_round_submitted
                ON tables(round_id, submitted_at);
            CREATE INDEX IF NOT EXISTS idx_scores_round
                ON scores(round_id);
            CREATE INDEX IF NOT EXISTS idx_scores_player
                ON scores(player_id);
            CREATE INDEX IF NOT EXISTS idx_scores_round_player
                ON scores(round_id, player_id);
            CREATE INDEX IF NOT EXISTS idx_judge_submissions_judge
                ON judge_submissions(judge_id);
            CREATE INDEX IF NOT EXISTS idx_judge_submissions_table
                ON judge_submissions(table_id);
            CREATE INDEX IF NOT EXISTS idx_score_corrections_table
                ON score_corrections(table_id, corrected_at DESC);
            """
        )
        for round_no in range(1, 7):
            conn.execute(
                "INSERT OR IGNORE INTO rounds(round_no, status) VALUES(?, '未开始')",
                (round_no,),
            )
        _ensure_columns(conn)


def _ensure_columns(conn: sqlite3.Connection) -> None:
    player_columns = {row["name"] for row in conn.execute("PRAGMA table_info(players)").fetchall()}
    table_columns = {row["name"] for row in conn.execute("PRAGMA table_info(tables)").fetchall()}
    judge_submission_columns = {row["name"] for row in conn.execute("PRAGMA table_info(judge_submissions)").fetchall()}
    player_additions = {
        "district": "ALTER TABLE players ADD COLUMN district TEXT",
        "school": "ALTER TABLE players ADD COLUMN school TEXT",
        "team_code": "ALTER TABLE players ADD COLUMN team_code TEXT",
        "player_code": "ALTER TABLE players ADD COLUMN player_code TEXT",
        "player_qr_token": "ALTER TABLE players ADD COLUMN player_qr_token TEXT",
        "is_transition": "ALTER TABLE players ADD COLUMN is_transition INTEGER NOT NULL DEFAULT 0",
        "transition_choice": "ALTER TABLE players ADD COLUMN transition_choice TEXT",
        "identity_label": "ALTER TABLE players ADD COLUMN identity_label TEXT NOT NULL DEFAULT '正常'",
    }
    table_additions = {
        "has_free_agent": "ALTER TABLE tables ADD COLUMN has_free_agent INTEGER NOT NULL DEFAULT 0",
        "seat_no": "ALTER TABLE tables ADD COLUMN seat_no TEXT",
    }
    for column, sql in player_additions.items():
        if column not in player_columns:
            conn.execute(sql)
    for column, sql in table_additions.items():
        if column not in table_columns:
            conn.execute(sql)
    if "judge_name" not in judge_submission_columns:
        conn.execute("ALTER TABLE judge_submissions ADD COLUMN judge_name TEXT")


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]
