import os
import re
import sys
from datetime import date

DAY_RE = re.compile(
    r"^(mon|tues|weds|thurs|fri|sat|sun)\s+"
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+"
    r"(\d+)(?:\s+(.*))?$",
    re.I,
)

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

WEEKDAYS = ["mon", "tues", "weds", "thurs", "fri", "sat", "sun"]


def calendar_date(year, month, day):
    return date(year, MONTHS[month], day)


def _year_from_path(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    if stem.isdigit() and len(stem) == 4:
        return int(stem)
    return None


def parse_event(e):
    m = re.search(r'\(([^)]*)\)\s*$', e)  # trailing (people)
    people = m.group(1).split() if m else []
    text = re.sub(r'\s*\([^)]*\)\s*$', '', e).strip()
    return {"text": text, "people": people}


def _is_skip(line):
    s = line.strip()
    return (not s) or s in ("(→)", "→") or set(s) <= {"_"}


def parse_file(path):
    """Return (days, line_failures, weekday_errors). Each day is one line."""
    days = []
    line_failures = []
    weekday_errors = []
    year = _year_from_path(path)
    with open(path, encoding="utf-8-sig") as f:
        physical = f.read().splitlines()

    for lineno, line in enumerate(physical, 1):
        if _is_skip(line):
            continue
        s = line.strip()
        m = DAY_RE.match(s)
        if not m:
            line_failures.append(f"{path}:{lineno}: {s}")
            continue
        weekday, mon, day = m.group(1).lower(), m.group(2).lower(), int(m.group(3))
        rest = (m.group(4) or "").strip()
        events = [parse_event(e.strip()) for e in rest.split(",") if e.strip()] if rest else []
        if year is not None:
            try:
                when = calendar_date(year, mon, day)
            except ValueError:
                line_failures.append(f"{path}:{lineno}: {s} (invalid date)")
                continue
            expected = WEEKDAYS[when.weekday()]
            if weekday != expected:
                weekday_errors.append(
                    f"{path}:{lineno}: {s} (wrote {weekday}, {when.isoformat()} is {expected})"
                )
        days.append((mon, day, events, s))
    return days, line_failures, weekday_errors


def format_parse_report(n_days, n_events, line_failures, verb="parsed", weekday_errors=None):
    n_fail = len(line_failures)
    msg = f"{verb} {n_days:,} days, {n_events:,} events, {n_fail:,} lines couldn't be parsed"
    chunks = [msg]
    if weekday_errors is not None:
        chunks[0] += f", {len(weekday_errors):,} weekday mismatches"
    if n_fail:
        chunks.append("couldn't parse:")
        chunks.extend(line_failures)
    if weekday_errors:
        chunks.append("weekday mismatches:")
        chunks.extend(weekday_errors)
    return "\n".join(chunks) + "\n"


def format_days(days):
    chunks = []
    for mon, day, events, raw in days:
        chunks.append(f"{mon} {day}")
        for ev in events:
            people = f"  [{', '.join(ev['people'])}]" if ev["people"] else ""
            chunks.append(f"  - {ev['text']}{people}")
        chunks.append("")
    return "\n".join(chunks)


def main():
    path = sys.argv[1]
    days, line_failures, weekday_errors = parse_file(path)
    n_events = sum(len(events) for _mon, _day, events, _raw in days)
    sys.stdout.write(
        format_parse_report(len(days), n_events, line_failures, weekday_errors=weekday_errors)
    )


if __name__ == "__main__":
    main()
