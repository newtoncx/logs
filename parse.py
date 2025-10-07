import re
import sys

DAY_RE = re.compile(
    r"^(mon|tues|weds|thurs|fri|sat|sun)\s+"
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+"
    r"(\d+)(?:\s+(.*))?$",
    re.I,
)


def parse_event(e):
    m = re.search(r'\(([^)]*)\)\s*$', e)  # trailing (people)
    people = m.group(1).split() if m else []
    text = re.sub(r'\s*\([^)]*\)\s*$', '', e).strip()
    return {"text": text, "people": people}


def _is_skip(line):
    s = line.strip()
    return (not s) or s in ("(→)", "→") or set(s) <= {"_"}


def parse_file(path):
    """Return (days, failures). Each day is one line; anything else is a failure."""
    days = []
    failures = []
    with open(path, encoding="utf-8-sig") as f:
        physical = f.read().splitlines()

    for lineno, line in enumerate(physical, 1):
        if _is_skip(line):
            continue
        s = line.strip()
        m = DAY_RE.match(s)
        if not m:
            failures.append(f"{path}:{lineno}: {s}")
            continue
        rest = (m.group(4) or "").strip()
        events = [parse_event(e.strip()) for e in rest.split(",") if e.strip()] if rest else []
        days.append((m.group(2).lower(), int(m.group(3)), events, s))
    return days, failures


def format_parse_report(n_days, n_events, failures, verb="parsed"):
    n_fail = len(failures)
    msg = f"{verb} {n_days:,} days, {n_events:,} events, {n_fail:,} lines couldn't be parsed"
    if n_fail:
        msg += ", here they are."
        return msg + "\n" + "\n".join(failures) + "\n"
    return msg + "\n"


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
    days, failures = parse_file(path)
    n_events = sum(len(events) for _mon, _day, events, _raw in days)
    sys.stdout.write(format_parse_report(len(days), n_events, failures))


if __name__ == "__main__":
    main()
