import re


def parse_event(e):
    m = re.search(r'\(([^)]*)\)\s*$', e)  # trailing (people)
    people = m.group(1).split() if m else []
    text = re.sub(r'\s*\([^)]*\)\s*$', '', e).strip()
    return {"text": text, "people": people}


def parse_day(line):  # "weds jan 1 a, b (x), c"
    wd, mon, day, rest = re.match(r'(\w+)\s+(\w+)\s+(\d+)\s+(.*)', line).groups()
    return mon, int(day), [parse_event(e.strip()) for e in rest.split(",")]
