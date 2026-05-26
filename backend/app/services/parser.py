import re

# ── Known meeting titles the model was trained on ──────────────────────────────
KNOWN_TITLES = {
    "standup", "sync", "review", "planning session", "retrospective",
    "kickoff", "demo", "interview", "1:1", "brainstorm", "strategy session",
    "all-hands", "workshop", "presentation", "check-in",
}

# ── Duration keywords in natural language ──────────────────────────────────────
DURATION_PATTERNS = [
    (r"\b(\d+)\s*hour[s]?\b",        lambda m: int(m.group(1)) * 60),
    (r"\b(\d+)\s*min(?:ute)?[s]?\b", lambda m: int(m.group(1))),
    (r"\bhalf[\s-]an?[\s-]hour\b",   lambda _: 30),
    (r"\ban?\s+hour\b",              lambda _: 60),
    (r"\b90[\s-]min\b",              lambda _: 90),
]

# ── Time parsing helpers ───────────────────────────────────────────────────────

# Matches:  6am  6AM  6:30am  6:30 AM  6 am  noon  midnight
_TIME_RE = re.compile(
    r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM|a\.m\.|p\.m\.)\b"
    r"|\b(noon|midnight)\b",
    re.IGNORECASE,
)

def extract_time_from_command(command: str) -> str | None:
    """
    Parse the first explicit 12-hour time in the command and return HH:MM
    in 24-hour format, or None if no time token is found.
    """
    m = _TIME_RE.search(command)
    if not m:
        return None

    # Special words
    if m.group(4):
        word = m.group(4).lower()
        return "12:00" if word == "noon" else "00:00"

    hour   = int(m.group(1))
    minute = int(m.group(2)) if m.group(2) else 0
    meridiem = m.group(3).lower().replace(".", "")  # "am" or "pm"

    if meridiem == "am":
        # 12 AM  → 00:xx  (midnight)
        if hour == 12:
            hour = 0
    else:  # pm
        # 12 PM stays 12; 1–11 PM add 12
        if hour != 12:
            hour += 12

    return f"{hour:02d}:{minute:02d}"


def extract_title_from_command(command: str) -> str | None:
    lower = command.lower()
    for title in sorted(KNOWN_TITLES, key=len, reverse=True):
        if title in lower:
            return title.title()
    m = re.search(r"\ba\s+([a-z][a-z\s]{1,30}?)\s+(?:with|for)\b", lower)
    if m:
        return m.group(1).strip().title()
    m = re.search(
        r"(?:schedule|book|set up|create|add)\s+(?:a|an)\s+([a-z][a-z\s]{1,30?})\b", lower
    )
    if m:
        return m.group(1).strip().title()
    return None


def extract_duration_from_command(command: str) -> int | None:
    lower = command.lower()
    for pattern, extractor in DURATION_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            return extractor(m)
    return None


def postprocess(parsed: dict, command: str) -> dict:
    """Correct fields that the small T5 model commonly gets wrong."""
    action = parsed.get("action", "")

    # ── Time correction (always override with regex parse of the command) ──────
    # The model frequently maps  6 AM → "16:00"  or  8 AM → "18:00".
    # Our regex is deterministic and correct, so prefer it whenever it fires.
    extracted_time = extract_time_from_command(command)
    if extracted_time:
        for time_key in ("start_time", "old_start_time", "new_start_time", "time"):
            if time_key in parsed:
                parsed[time_key] = extracted_time
        # If the action has a start_time but we got none from the model, inject it
        if action in ("insert", "delete", "add_attendee") and "start_time" not in parsed:
            parsed["start_time"] = extracted_time
        if action == "reminder" and "time" not in parsed:
            parsed["time"] = extracted_time

    # ── Title correction ───────────────────────────────────────────────────────
    if action in ("insert", "delete", "update", "add_attendee"):
        extracted_title = extract_title_from_command(command)
        if extracted_title:
            parsed["title"] = extracted_title

    # ── Duration correction (insert only) ─────────────────────────────────────
    if action == "insert":
        extracted_dur = extract_duration_from_command(command)
        if extracted_dur is not None:
            parsed["duration_minutes"] = extracted_dur
        else:
            parsed.pop("duration_minutes", None)

    return parsed
