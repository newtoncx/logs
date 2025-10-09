import glob
import os
import sqlite3
import sys

from parse import calendar_date, format_parse_report, parse_file
from setup_schema import create_schema

DB_PATH = "logs.db"


def year_files(directory="."):
    return sorted(glob.glob(os.path.join(directory, "[0-9][0-9][0-9][0-9].txt")))


def get_or_create_person(conn, cache, name):
    person_id = cache.get(name)
    if person_id is not None:
        return person_id
    row = conn.execute("SELECT id FROM people WHERE name = ?", (name,)).fetchone()
    if row:
        cache[name] = row[0]
        return row[0]
    cur = conn.execute("INSERT INTO people (name) VALUES (?)", (name,))
    cache[name] = cur.lastrowid
    return cur.lastrowid


def load(db_path=DB_PATH, directory="."):
    if os.path.exists(db_path):
        os.remove(db_path)
    create_schema(db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        people = {}
        n_days = 0
        n_events = 0
        line_failures = []
        weekday_errors = []
        for path in year_files(directory):
            year = int(os.path.splitext(os.path.basename(path))[0])
            days, file_line_failures, file_weekday_errors = parse_file(path)
            line_failures.extend(file_line_failures)
            weekday_errors.extend(file_weekday_errors)
            for month, day, events, raw in days:
                when = calendar_date(year, month, day)
                cur = conn.execute(
                    "INSERT INTO days (date, raw) VALUES (?, ?)",
                    (when.isoformat(), raw),
                )
                day_id = cur.lastrowid
                n_days += 1
                for seq, event in enumerate(events):
                    cur = conn.execute(
                        "INSERT INTO events (day_id, seq, text) VALUES (?, ?, ?)",
                        (day_id, seq, event["text"]),
                    )
                    event_id = cur.lastrowid
                    n_events += 1
                    for name in event["people"]:
                        person_id = get_or_create_person(conn, people, name)
                        conn.execute(
                            "INSERT OR IGNORE INTO event_people (event_id, person_id) VALUES (?, ?)",
                            (event_id, person_id),
                        )
        conn.commit()
        sys.stdout.write(
            format_parse_report(
                n_days, n_events, line_failures, verb="loaded", weekday_errors=weekday_errors
            )
        )
    finally:
        conn.close()


def main():
    load()


if __name__ == "__main__":
    main()
