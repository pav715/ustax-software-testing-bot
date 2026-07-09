"""
Telegram sender — formats and sends job posts to the channel.
Updated: 2026-07-04
"""
import requests
import re
import time
from datetime import datetime, date, timedelta
import config

API = f"https://api.telegram.org/bot{config.BOT_TOKEN}"


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
    """
    Return a human-readable posted time string in IST.
    - ISO date  "2026-03-08"           → "08 Mar 2026"
    - ISO datetime "2026-03-08T10:30"  → "08 Mar 2026, 04:00 PM IST"  (converted to IST)
    - Relative  "1 day ago"            → "1 day ago"
    - Empty                            → use fetched_at converted to IST
    """
    IST_OFFSET = timedelta(hours=5, minutes=30)

    p = str(posted or "").strip()

    # Try ISO date/datetime format
    if p and re.match(r"\d{4}-\d{2}-\d{2}", p):
        try:
            dt = datetime.fromisoformat(p[:19])  # handles "2026-03-08" and "2026-03-08T10:30:00"
            if len(p) >= 16:
                # Has time component — convert UTC → IST
                dt_ist = dt + IST_OFFSET
                return dt_ist.strftime("%d %b %Y, %I:%M %p IST")
            else:
                # Date only
                return dt.strftime("%d %b %Y")
        except Exception:
            pass

    # Relative string from Indeed / Naukri / Workday — return as-is
    if p:
        return p

    # Fallback: use fetched_at (when bot scraped it), convert UTC → IST
    if fetched_at:
        try:
            dt = datetime.fromisoformat(str(fetched_at)[:19])
            dt_ist = dt + IST_OFFSET
            return f"Found at {dt_ist.strftime('%d %b %Y, %I:%M %p IST')}"
        except Exception:
            pass

    return ""


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


def _format_location(loc):
    loc = (loc or "India").strip()
    ll = loc.lower()
    if "remote" in ll and "(remote)" not in ll and "· remote" not in ll:
        return loc
    if "hyderabad" in ll and "hybrid" not in ll and "· hybrid" not in ll:
        return f"{loc} · Hybrid"
    return loc


def _experience_display(job, title):
    exp = (job.get("_experience") or job.get("experience") or "").strip()
    if exp and exp.lower() not in ("not mentioned", "n/a", ""):
        return exp
    return "See job description ↓"


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

    safe_company = _escape(company)
    safe_title   = _escape(title)
    safe_loc     = _escape(loc_str)
    safe_qual    = _escape(qual)
    safe_exp     = _escape(exp)

    lines = []

    # Urgency tag
    urgency = _urgency_tag(posted)
    if urgency:
        lines.append(urgency.strip())
        lines.append("")

    # Header
    lines += [
        f"🧪 *{safe_company}*",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"💼 *Role:* {safe_title}",
        f"📍 *Location:* {safe_loc}",
    ]

    if safe_exp:
        lines.append(f"👨‍💻 *Experience:* {safe_exp}")

    if safe_qual and safe_qual.lower() not in ("not mentioned", ""):
        lines.append(f"🎓 *Qualification:* {safe_qual}")

    # Posted time — exact date/time in IST where available
    posted_str = _format_posted(posted, job.get("fetched_at", ""))
    if posted_str:
        lines.append(f"⏰ *Posted:* {_escape(posted_str)}")

    # Salary (if mentioned)
    if salary and salary.lower() not in ("not mentioned", ""):
        lines.append(f"💰 *Salary:* {_escape(salary)}")

    lines += [
        "",
        f"🔗 *Apply Here:*",
        url,
    ]
    if source:
        lines.append(f"\n📋 _{_escape(source)}_")

    return "\n".join(lines)


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
