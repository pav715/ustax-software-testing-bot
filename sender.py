"""
Telegram sender — formats and sends job posts to the channel.
Updated: 2026-07-04
"""
import requests
import re
import time
from datetime import datetime, date, timedelta
import config
from telegram_templates import render_job_post

API = f"https://api.telegram.org/bot{config.BOT_TOKEN}"
BRAND = "testing"


def _escape(text):
    """Escape Telegram Markdown v1 special characters."""
    if not text:
        return ""
    for ch in ["_", "*", "`", "["]:
        text = text.replace(ch, f"\\{ch}")
    return text


def _post(text, chat_id=None, retry=2):
    cid = str(chat_id or config.CHAT_ID)
    if not cid or cid == "None":
        print("[Telegram] ERROR: CHAT_ID not set.")
        return False
    if not config.BOT_TOKEN:
        print("[Telegram] ERROR: BOT_TOKEN not set.")
        return False
    try:
        for attempt in range(retry):
            try:
                r = requests.post(
                    f"{API}/sendMessage",
                    json={
                        "chat_id":                  cid,
                        "text":                     text,
                        "parse_mode":               "Markdown",
                        "disable_web_page_preview": False,
                    },
                    timeout=15,
                )
                if r.status_code == 200:
                    return True
                elif attempt < retry - 1:
                    time.sleep(1)
                    continue
            except requests.Timeout:
                if attempt < retry - 1:
                    time.sleep(2)
                    continue
                raise

        # Fallback: plain text (no markdown)
        r2 = requests.post(
            f"{API}/sendMessage",
            json={
                "chat_id":                  cid,
                "text":                     re.sub(r"[*_`\[\]]", "", text),
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        return r2.status_code == 200

    except Exception as e:
        print(f"[Telegram] Send error: {e}")
        return False


def _format_posted(posted, fetched_at=""):
    """Date only — no time."""
    IST_OFFSET = timedelta(hours=5, minutes=30)
    p = str(posted or "").strip()

    if p and re.match(r"\d{4}-\d{2}-\d{2}", p):
        try:
            dt = datetime.fromisoformat(p[:19])
            if len(p) >= 16:
                dt = dt + IST_OFFSET
            return dt.strftime("%d %b %Y")
        except Exception:
            pass

    if p and re.search(r"\d{1,2}\s+\w+\s+\d{4}", p):
        m = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", p)
        if m:
            return m.group(1)

    if p and not re.search(r"\d:\d{2}", p):
        return p

    if fetched_at:
        try:
            dt = datetime.fromisoformat(str(fetched_at)[:19])
            return (dt + IST_OFFSET).strftime("%d %b %Y")
        except Exception:
            pass

    return date.today().strftime("%d %b %Y")


def _urgency_tag(posted):
    """Return urgency label — all jobs are today-only so always 'Posted Today'."""
    if not posted:
        return ""
    try:
        posted_date = date.fromisoformat(str(posted)[:10])
        if (date.today() - posted_date).days == 0:
            return "🔴 *Posted Today!*\n"
    except Exception:
        pass
    return ""



def _qualification(title):
    t = title.lower()
    if any(x in t for x in ["senior", "manager", "lead"]):
        return "Graduate / Post-Graduate (Accounting / Finance / Commerce)"
    elif any(x in t for x in ["software", "programmer", "developer"]):
        return "B.Com / B.Tech / BCA (Computer / Accounting preferred)"
    else:
        return "Graduate / Post-Graduate (Accounting / Finance preferred)"


_CITY_STATE = {
    "hyderabad": ("Hyderabad", "Telangana"),
    "secunderabad": ("Hyderabad", "Telangana"),
    "bangalore": ("Bangalore", "Karnataka"),
    "bengaluru": ("Bangalore", "Karnataka"),
    "chennai": ("Chennai", "Tamil Nadu"),
    "mumbai": ("Mumbai", "Maharashtra"),
    "navi mumbai": ("Mumbai", "Maharashtra"),
    "pune": ("Pune", "Maharashtra"),
    "delhi": ("Delhi", "Delhi"),
    "new delhi": ("Delhi", "Delhi"),
    "noida": ("Noida", "Uttar Pradesh"),
    "gurgaon": ("Gurgaon", "Haryana"),
    "gurugram": ("Gurugram", "Haryana"),
    "kolkata": ("Kolkata", "West Bengal"),
    "ahmedabad": ("Ahmedabad", "Gujarat"),
    "kochi": ("Kochi", "Kerala"),
    "cochin": ("Kochi", "Kerala"),
    "visakhapatnam": ("Visakhapatnam", "Andhra Pradesh"),
    "vizag": ("Visakhapatnam", "Andhra Pradesh"),
    "jaipur": ("Jaipur", "Rajasthan"),
    "indore": ("Indore", "Madhya Pradesh"),
    "chandigarh": ("Chandigarh", "Chandigarh"),
    "coimbatore": ("Coimbatore", "Tamil Nadu"),
    "lucknow": ("Lucknow", "Uttar Pradesh"),
}

_BAD = ("metropolitan", "anywhere", "all areas", "preferred", "west india", "south india")


def _format_location(loc):
    """City, State — clean short format."""
    loc = (loc or "").strip()
    if not loc:
        return "India"
    ll = loc.lower()
    if "remote" in ll:
        return "Remote"

    parts = [p.strip() for p in loc.split(",") if p.strip()]
    if len(parts) >= 2:
        city, state = parts[0], parts[1]
        if state.lower() not in ("india", "in") and len(city) <= 30 and len(state) <= 35:
            if not any(x in city.lower() or x in state.lower() for x in _BAD):
                return f"{city}, {state}"

    for key, (city, state) in sorted(_CITY_STATE.items(), key=lambda x: -len(x[0])):
        if key in ll:
            return f"{city}, {state}"

    for city in getattr(config, "LOCATIONS", []):
        cl = city.lower()
        if cl in ll:
            for key, (c, s) in _CITY_STATE.items():
                if key == cl or c.lower() == cl:
                    return f"{c}, {s}"
            return city

    first = parts[0] if parts else ""
    if first and len(first) <= 25 and not any(x in first.lower() for x in _BAD):
        return first.title()
    return "India"


def _experience_display(job, title):
    exp = (job.get("_experience") or job.get("experience") or "").strip()
    if exp and exp.lower() not in ("not mentioned", "n/a", ""):
        return exp
    return "See job description ↓"


def _posted_today(posted):
    if not posted:
        return False
    try:
        return (date.today() - date.fromisoformat(str(posted)[:10])).days == 0
    except Exception:
        return False


def format_job(job):
    title   = job.get("title", "")
    company = job.get("company", "")
    loc     = job.get("location", "India / Remote")
    url     = job.get("url", "")
    source  = job.get("source", "")
    posted  = job.get("posted", "")

    qual   = job.get("_qualification") or _qualification(title)
    exp    = _experience_display(job, title)
    salary = job.get("_salary", "")
    loc_str = _format_location(loc)
    posted_str = _format_posted(posted, job.get("fetched_at", ""))

    return render_job_post(
        BRAND,
        job,
        _escape,
        company,
        title,
        loc_str,
        exp,
        qual if qual and qual.lower() not in ("not mentioned", "") else "",
        posted_str,
        url,
        source=source,
        posted_today=_posted_today(posted),
        salary=salary,
    )


def send_job(job):
    msg = format_job(job)
    ok  = _post(msg)
    if ok:
        time.sleep(2)
    return ok


def send_daily_summary(stats):
    """Send daily summary at 9 AM IST."""
    today    = stats.get("date", date.today().isoformat())
    sent     = stats.get("sent", 0)
    companies = stats.get("companies", {})

    lines = [
        "📊 *US Tax Software Testing — Daily Summary*",
        f"📅 {today}",
        "",
        f"✅ *Jobs sent today:* {sent}",
        f"🏢 *Companies hired:* {len(companies)}",
    ]

    if companies:
        top = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]
        lines.append("\n🏆 *Top Companies:*")
        for co, cnt in top:
            lines.append(f"  • {_escape(co)} — {cnt} job{'s' if cnt > 1 else ''}")

    lines += [
        "",
        f"⏱ Bot checks every *{config.CHECK_INTERVAL_LABEL}*",
        f"🕐 {datetime.now().strftime('%d %b %Y %H:%M IST')}",
    ]

    _post("\n".join(lines))


def send_and_pin_welcome():
    """
    Send a welcome/intro message to the channel and pin it.
    Call once — after that it stays pinned permanently.
    Requires the bot to have 'Pin Messages' admin permission.
    """
    msg = (
        "👋 *Welcome to US Tax Software Testing India\\!*\n\n"
        "🎯 This channel posts *fresh Tax Software Testing & QA roles* hourly — "
        "automatically sourced from LinkedIn, Big 4 firms and top IT/BPO companies\\.\n\n"
        "💼 *Roles we cover:*\n"
        "• Tax Software QA / Testing\n"
        "• E\\-File / ATS / MeF Analyst\n"
        "• XML Schema / Tax Form QA\n"
        "• Regulatory & Compliance QA\n"
        "• Lacerte / ProSeries / GoSystem QA\n\n"
        "📍 *Locations:* Hyderabad, Bangalore, Chennai, Remote & more\n\n"
        "🔔 *Turn on notifications* so you never miss a job\\!\n\n"
        "✅ Good luck with your job search\\! 🚀"
    )

    api = f"https://api.telegram.org/bot{config.BOT_TOKEN}"

    # Step 1 — send the message
    try:
        r = requests.post(
            f"{api}/sendMessage",
            json={
                "chat_id":                  config.CHAT_ID,
                "text":                     msg,
                "parse_mode":               "MarkdownV2",
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
        if r.status_code != 200:
            print(f"[Pin] Failed to send welcome message: {r.text}")
            return False

        message_id = r.json()["result"]["message_id"]
        print(f"[Pin] Welcome message sent (id={message_id})")

    except Exception as e:
        print(f"[Pin] Send error: {e}")
        return False

    # Step 2 — pin it (disable_notification=True so no alert spam)
    try:
        r2 = requests.post(
            f"{api}/pinChatMessage",
            json={
                "chat_id":              config.CHAT_ID,
                "message_id":          message_id,
                "disable_notification": True,
            },
            timeout=15,
        )
        if r2.status_code == 200:
            print(f"[Pin] Welcome message pinned successfully.")
            return True
        else:
            print(f"[Pin] Pin failed: {r2.text}")
            return False

    except Exception as e:
        print(f"[Pin] Pin error: {e}")
        return False


def send_fail_alert(error_msg=""):
    """Send alert if bot encounters a critical error."""
    msg = (
        "❌ *US Tax Software Testing Bot — Error*\n\n"
        f"Something went wrong:\n`{_escape(str(error_msg)[:200])}`\n\n"
        "Please check GitHub Actions logs.\n"
        f"🕐 {datetime.now().strftime('%d %b %Y %H:%M')}"
    )
    _post(msg)
