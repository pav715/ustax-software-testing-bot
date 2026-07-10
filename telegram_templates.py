"""Professional Telegram job posts — clean channel style, not spammy."""
import hashlib
from datetime import datetime, timedelta

IST = timedelta(hours=5, minutes=30)

BRANDS = {
    "tax": {"label": "US Tax Jobs", "icon": "💼"},
    "testing": {"label": "Tax Software QA", "icon": "🧪"},
    "mortgage": {"label": "Mortgage & Loan", "icon": "🏠"},
}

TIME_SLOTS = [
    (8, 11, "morning"),
    (12, 15, "afternoon"),
    (16, 18, "late_afternoon"),
    (19, 21, "evening"),
    (22, 23, "night"),
]

# Friendly opener — line 1 for notification, kept professional
HOOKS = {
    "morning": [
        "☕ *Good morning* — a new opportunity is open for you",
        "🌅 *Morning update* — fresh role posted, see details below",
        "☀️ *New day, new opening* — worth a look 👇",
        "💼 *Morning hire alert* — role details below",
    ],
    "afternoon": [
        "🌞 *Afternoon update* — new opportunity available",
        "💼 *New role posted* — details below",
        "📋 *Fresh opening* — check if this fits you",
        "👀 *New opportunity* — see company & role below",
    ],
    "late_afternoon": [
        "⚡ *Evening update* — new role just posted",
        "💼 *Before you log off* — one opening to review",
        "📋 *New opportunity* — details below",
        "👀 *Fresh role alert* — see below",
    ],
    "evening": [
        "🌆 *Evening update* — new opportunity available",
        "💼 *New opening tonight* — details below",
        "📋 *Fresh role* — check details below",
        "👀 *Opportunity alert* — see below",
    ],
    "night": [
        "🌙 *Night update* — new role posted",
        "💼 *Late opening* — details below",
        "📋 *Fresh opportunity* — see below",
        "👀 *New role* — check before tomorrow",
    ],
    "default": [
        "💼 *New opportunity* — details below",
        "📋 *Fresh opening* — see company & role",
        "👀 *New role posted* — check below",
        "✨ *Job update* — details below",
    ],
}

CTAS = [
    "*Apply here* 👇",
    "*View & apply* 👇",
    "*Interested? Apply below* 👇",
    "*Tap to apply* 👇",
]

# Short, clean separators only — no heavy grids or symbol spam
LINES = [
    "────────────────────────",
    "━━━━━━━━━━━━━━━━━━━━━━━━",
    "────────────────────────",
    "━━━━━━━━━━━━━━━━━━━━━━━━",
]


def _ist_hour():
    return (datetime.utcnow() + IST).hour


def _theme_slot():
    h = _ist_hour()
    for start, end, slot in TIME_SLOTS:
        if start <= h <= end:
            return slot
    return "default"


def _pick(pool, job, salt=""):
    key = f"{job.get('title', '')}|{job.get('company', '')}|{_ist_hour()}|{salt}"
    idx = int(hashlib.md5(key.encode()).hexdigest(), 16) % len(pool)
    return pool[idx]


def _layout_idx(job):
    key = f"{job.get('title', '')}|{job.get('company', '')}|layout"
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % 4


def render_job_post(
    brand_key,
    job,
    escape,
    company,
    title,
    location,
    experience,
    qualification,
    posted_str,
    url,
    source="",
    posted_today=False,
    salary="",
):
    hook = _pick(HOOKS.get(_theme_slot(), HOOKS["default"]), job, "hook")
    cta = _pick(CTAS, job, "cta")
    layout = _layout_idx(job)
    line = LINES[layout]

    co, ti, lo = escape(company), escape(title), escape(location)
    ex = escape(experience) if experience else ""
    ps = escape(posted_str) if posted_str else ""

    meta = []
    if ex:
        meta.append(f"Experience : {ex}")
    if ps:
        meta.append(f"Posted : {ps}")
    if salary and salary.lower() not in ("not mentioned", ""):
        meta.append(f"Salary : {escape(salary)}")
    meta_line = "  ·  ".join(meta) if meta else ""

    apply = f"\n{cta}\n{url}"
    if source:
        apply += f"\n\n_via {escape(source)}_"

    if layout == 0:
        # Card — single clean block
        body = [
            hook, "",
            line,
            f"Company : *{co}*",
            f"Role       : *{ti}*",
            f"Location : *{lo}*",
        ]
        if meta_line:
            body.append(meta_line)
        body.extend([line, apply])

    elif layout == 1:
        # Company first — bold & clear
        body = [
            hook, "",
            f"🏢 *{co}*",
            f"💼 *{ti}*",
            f"📍 {lo}",
        ]
        if meta_line:
            body.append(f"_{meta_line}_")
        body.extend(["", apply])

    elif layout == 2:
        # Compact — good for mobile scan
        body = [
            hook, "",
            line,
            f"*Company*  ·  *{co}*",
            f"*Role*         ·  *{ti}*",
            f"*Location*  ·  *{lo}*",
        ]
        if meta_line:
            body.append(f"_{meta_line}_")
        body.extend([line, apply])

    else:
        # Minimal — least visual noise
        body = [
            hook, "",
            f"*{co}* — *{ti}*",
            f"📍 {lo}",
        ]
        if meta_line:
            body.append(f"_{meta_line}_")
        body.extend(["", apply])

    return "\n".join(body)
