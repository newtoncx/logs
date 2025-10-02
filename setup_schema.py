import sqlite3

SCHEMA = """
CREATE TABLE days (
    id      INTEGER PRIMARY KEY,
    date    TEXT NOT NULL UNIQUE,
    raw     TEXT NOT NULL
);
CREATE TABLE events (
    id        INTEGER PRIMARY KEY,
    day_id    INTEGER NOT NULL REFERENCES days(id),
    seq       INTEGER NOT NULL,
    text      TEXT NOT NULL,
    category  TEXT,
    UNIQUE (day_id, seq)
);
CREATE TABLE people (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE event_people (
    event_id  INTEGER NOT NULL REFERENCES events(id),
    person_id INTEGER NOT NULL REFERENCES people(id),
    PRIMARY KEY (event_id, person_id)
);
"""


def create_schema(db_path="logs.db"):
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
    finally:
        conn.close()


def main():
    create_schema()


if __name__ == "__main__":
    main()
