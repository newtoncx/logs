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


def logical_lines(raw_lines):
    """Join wrapped continuations; drop blanks, rules, and (→) markers."""
    out = []
    for line in raw_lines:
        if _is_skip(line):
            continue
        s = line.strip()
        if DAY_RE.match(s) or s.startswith("-") or not out:
            out.append(s)
        else:
            out[-1] = out[-1].rstrip() + " " + s
    return out


def parse_file(path):
    with open(path, encoding="utf-8-sig") as f:
        lines = logical_lines(f.read().splitlines())

    days = []
    i = 0
    while i < len(lines):
        m = DAY_RE.match(lines[i])
        if not m:
            i += 1
            continue
        mon, day, rest = m.group(2).lower(), int(m.group(3)), (m.group(4) or "").strip()
        i += 1
        if rest:
            events = [parse_event(e.strip()) for e in rest.split(",") if e.strip()]
        else:
            events = []
        days.append((mon, day, events, lines[i]))
    return days


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
    text = format_days(parse_file(path))
    sys.stdout.write(text if text.endswith("\n") else text + "\n")


if __name__ == "__main__":
    main()
