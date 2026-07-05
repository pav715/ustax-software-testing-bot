"""Single-cycle runner for GitHub Actions — LinkedIn only. Updated: 2026-07-04"""
import json
import os
import re
import time
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import config

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from scraper import fetch_all_jobs, SESSION
from sender import send_job, send_daily_summary, send_fail_alert

SEEN_FILE  = "seen_jobs.json"
STATS_FILE = "stats.json"
STATE_FILE = "bot_state.json"

US_TAX_TERMS = re.compile(
    r"("
    r"1040|1041|1065|1120|"
    r"us\s*tax\s*preparer|us\s*tax\s*analyst|"
    r"enrolled\s*agent|"
    r"cpa\s*tax|"
    r"irs"
    r")",
    re.IGNORECASE,
)

BLOCKLIST = re.compile(
    r"\b("
    r"recruiter|recruitment|talent\s*acquisition|bench\s*sales|"
    r"us\s*it\s*recruiter|it\s*recruiter|"
    r"software\s*engineer(?!\s*tax)|software\s*developer(?!\s*tax)|"
    r"selenium|automation\s*tester|manual\s*tester|"
    r"payroll(?!\s*tax)|accounts\s*payable|accounts\s*receivable|"
    r"statutory\s*audit|business\s*development|sales\s*executive|"
    # Indian tax roles - GST (1-10)
    r"\bgst\b|goods\s*and\s*services\s*tax|gstn|gst\s*compliance|gst\s*specialist|gst\s*manager|gst\s*consultant|gst\s*filing|gst\s*returns|gst\s*audit|gst\s*advisory|"
    # Income Tax India (11-20)
    r"income\s*tax\s*(?!withholding)|income\s*tax\s*consultant|income\s*tax\s*executive|"
    r"direct\s*tax(?!\s*analyst\s*(?:us|federal|state))|india\s*tax|domestic\s*tax|indian\s*tax|"
    # TDS / TCS (21-25)
    r"\btds\b|\btcs\b|tax\s*deducted|tax\s*collected|tds\s*analyst|tds\s*filing|"
    # Indirect Tax India (26-35)
    r"indirect\s*tax(?!\s*analyst\s*(?:us|federal))|"
    r"\bvat\b(?!\s*us)|service\s*tax|excise\s*duty|customs\s*duty|"
    r"transfer\s*pricing|tax\s*litigation|"
    # CA / Finance Related (36-45)
    r"chartered\s*accountant|ca\s*article|ca\s*analyst|"
    r"(?<!us\s)(?<!federal\s)finance\s*analyst(?!\s*us)|accounts\s*analyst|^accountant$|"
    r"financial\s*analyst(?!\s*(?:us|tax))|finance\s*executive|accounts\s*executive|"
    # Other Indian Tax (46-50)
    r"tax\s*auditor|statutory\s*compliance|tax\s*compliance\s*executive(?!\s*us)"
    r")\b",
    re.IGNORECASE,
)


US_STATES = re.compile(
    r"\b(New York|California|Texas|Florida|Illinois|Washington DC|"
    r"Massachusetts|New Jersey|Georgia|Ohio|Virginia|Pennsylvania|"
    r"North Carolina|Michigan|Arizona|Colorado|"
    r"NY|CA|TX|FL|IL|NJ|GA|MA|OH|VA|PA|NC|MI|AZ|CO|DC|"
    r"Remote|WFH|Work from Home)\b",
    re.IGNORECASE,
)


def is_valid_us_tax_job(job):
    """Accept only if job mentions US state or Remote explicitly."""
    title = job.get("title", "")
    location = job.get("location", "")
    company = job.get("company", "")
    full = f"{title} {location} {company}"
    return bool(US_STATES.search(full))


def is_india_location(job):
    """Return True only if job is India/Remote — reject other countries."""
    loc = job.get("location", "").lower()

    india_keywords = [
        "india", "remote", "hyderabad", "bangalore", "bengaluru", "chennai",
        "mumbai", "pune", "delhi", "gurgaon", "noida", "kolkata", "ahmedabad",
        "jaipur", "indore", "chandigarh", "kochi", "coimbatore", "lucknow"
    ]

    reject_keywords = [
        "usa", "united states", "canada", "uk", "australia", "europe", "egypt",
        "middle east", "africa", "singapore", "malaysia"
    ]

    if any(kw in loc for kw in reject_keywords):
        return False

    if any(kw in loc for kw in india_keywords) or not loc or loc.strip() == "":
        return True

    return False


def is_us_tax_job(job):
    title = job.get("title", "").lower()
    company = job.get("company", "").lower()
    desc = job.get("description", "").lower()
    full = f"{title} {company} {desc}"

    if BLOCKLIST.search(title):
        return False

    form_numbers = ["1040", "1041", "1120", "1065", "1099", "w-2"]
    us_specific_keywords = [
        "enrolled agent", "ea", "cpa", "irs", "internal revenue",
        "us tax", "us taxation", "united states tax"
    ]

    common_tax_roles = [
        "tax preparer", "tax analyst", "tax accountant", "tax associate",
        "tax manager", "tax director", "tax consultant", "tax specialist",
        "tax compliance", "tax auditor"
    ]

    indian_tax_keywords = [
        "gst", "goods and services tax", "income tax", "it return",
        "indian tax", "india tax", "ato", "inr", "rupee"
    ]

    has_form_number = any(fn in full for fn in form_numbers)
    has_form_in_desc = any(fn in desc for fn in form_numbers)
    has_us_keyword = any(kw in full for kw in us_specific_keywords)
    has_common_role = any(role in title for role in common_tax_roles)
    has_indian_tax = any(kw in full for kw in indian_tax_keywords)

    if has_indian_tax:
        return False

    # Accept if has form numbers OR US-specific keywords in full text
    if has_form_number or has_us_keyword:
        return True

    # Accept if common tax role title AND form numbers MUST be in description
    if has_common_role and has_form_in_desc:
        return True

    return False


def is_tax_software_testing_job(job):
    """Accept US Tax Software Testing jobs: form numbers OR software testing keywords."""
    title = job.get("title", "").lower()
    company = job.get("company", "").lower()
    desc = job.get("description", "").lower()
    full = f"{title} {company} {desc}"

    if BLOCKLIST.search(title):
        return False

    # Tax form numbers
    form_numbers = ["1040", "1041", "1120", "1065", "1099", "w-2"]

    # Software testing keywords (QA, testing, schema, ATS, E-File, etc.)
    testing_keywords = [
        "qa", "qe", "quality assurance", "quality engineer",
        "test", "tester", "testing",
        "schema", "xml", "xsd",
        "ats", "automated test", "e-file", "electronic filing",
        "compliance", "validation", "regression",
        "bug tracking", "defect", "jira", "visual studio"
    ]

    # US tax keywords
    us_tax_keywords = [
        "us tax", "us taxation", "tax software",
        "lacerte", "proseries", "onesource", "atx",
        "taxslayer", "drake", "proconnect"
    ]

    indian_tax_keywords = [
        "gst", "goods and services tax", "income tax", "it return",
        "indian tax", "india tax", "ato", "inr", "rupee"
    ]

    has_form_number = any(fn in full for fn in form_numbers)
    has_testing_keyword = any(kw in full for kw in testing_keywords)
    has_us_tax_keyword = any(kw in full for kw in us_tax_keywords)
    has_indian_tax = any(kw in full for kw in indian_tax_keywords)

    if has_indian_tax:
        return False

    # Accept if: form numbers OR (testing keywords AND US tax context)
    if has_form_number:
        return True

    if has_testing_keyword and has_us_tax_keyword:
        return True

    return False


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"paused": False, "last_update_id": 0, "last_run_at": ""}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def load_stats():
    today = date.today().isoformat()
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE) as f:
                s = json.load(f)
            if s.get("date") == today:
                return s
        except Exception:
            pass
    return {"date": today, "sent": 0, "companies": {}, "summary_sent": False}


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


def load_seen():
    """Load seen job IDs. Handles [], {}, and corrupt files gracefully."""
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                return set(data)
            if isinstance(data, dict):
                return set(data.keys()) if data else set()
        except Exception:
            pass
    return set()


def save_seen(seen_set):
    data = list(seen_set)[-5000:]
    with open(SEEN_FILE, "w") as f:
        json.dump(data, f)


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def _dedup_key(job):
    """Title+company fingerprint — blocks the same job even if LinkedIn
    gives it a new URL each scrape (prevents channel spam)."""
    title   = (job.get("title") or "").lower().strip()
    company = (job.get("company") or "").lower().strip()
    return f"{title}|{company}"


def handle_commands(state, stats):
    if not config.BOT_TOKEN:
        return state
    try:
        offset = state.get("last_update_id", 0) + 1
        r = requests.get(
            f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates",
            params={"offset": offset, "timeout": 5, "limit": 10},
            timeout=10,
        )
        if r.status_code != 200:
            return state

        updates = r.json().get("result", [])
        for update in updates:
            state["last_update_id"] = update["update_id"]
            msg = (update.get("message") or update.get("channel_post") or {})
            text = msg.get("text", "").strip().lower()
            chat_id = str(msg.get("chat", {}).get("id", ""))
            if not chat_id:
                continue

            api = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"

            if text.startswith("/status"):
                reply = (
                    f"🤖 *US Tax Jobs Bot — Status*\n\n"
                    f"{'⏸ PAUSED' if state.get('paused') else '✅ RUNNING'}\n\n"
                    f"📊 *Today ({stats['date']}):*\n"
                    f"• Jobs sent: *{stats['sent']}*\n"
                    f"• Companies: *{len(stats['companies'])}*\n"
                    f"⏱ Checks every *1 hour*\n"
                    f"🕐 {datetime.now().strftime('%d %b %Y %H:%M IST')}"
                )
                requests.post(api, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"}, timeout=10)
            elif text == "/pause":
                state["paused"] = True
                requests.post(api, json={"chat_id": chat_id, "text": "⏸ *Bot paused.* Send /resume to restart.", "parse_mode": "Markdown"}, timeout=10)
            elif text == "/resume":
                state["paused"] = False
                requests.post(api, json={"chat_id": chat_id, "text": "▶️ *Bot resumed.* Notifications are back on.", "parse_mode": "Markdown"}, timeout=10)
            elif text == "/help":
                reply = "🤖 *Commands:*\n/status — Bot status\n/pause — Pause\n/resume — Resume\n/help — Help"
                requests.post(api, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        log(f"[Commands] Error: {e}")
    return state


def enrich_job(job):
    """Fetch full job description from LinkedIn detail page."""
    if job.get("description") and len(job["description"]) > 300:
        return job
    url = job.get("url", "")
    try:
        if "linkedin.com" in url:
            match = re.search(r'/(\d{8,})', url)
            if match:
                jid = match.group(1)
                detail_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{jid}"
                r = SESSION.get(detail_url, timeout=12)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.content, "html.parser")
                    desc_div = (
                        soup.find("div", class_=re.compile(r"show-more-less-html|description__text")) or
                        soup.find("section", class_=re.compile(r"description"))
                    )
                    if desc_div:
                        job["description"] = desc_div.get_text(" ", strip=True)[:2000]
                    criteria = soup.find_all("span", class_=re.compile(r"description__job-criteria-text"))
                    for c in criteria:
                        text = c.get_text(strip=True)
                        if re.search(r"year|experience|mid|senior|entry", text, re.IGNORECASE):
                            if not job.get("experience") or len(job["experience"]) < 3:
                                job["experience"] = text
    except Exception as e:
        log(f"  [Enrich] error: {e}")
    time.sleep(1.5)
    return job


def extract_experience(desc, title):
    patterns = [
        r"(\d+\+?\s*(?:to|-)\s*\d*\+?\s*years?\s*(?:of\s*)?(?:experience|exp)?[^\n.]*)",
        r"((?:minimum|min\.?|atleast|at\s*least)\s*\d+\+?\s*years?[^\n.]*)",
        r"(\d+\+?\s*years?\s*(?:of\s*)?(?:relevant\s*)?experience[^\n.]*)",
    ]
    for p in patterns:
        m = re.search(p, desc, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:100]
    t = title.lower()
    if any(x in t for x in ["senior", "manager", "lead"]):
        return "5+ Years (US Tax)"
    elif any(x in t for x in ["associate", "junior", "jr"]):
        return "1-2 Years (US Tax)"
    return "2-5 Years (US Tax)"


def extract_qualification(desc, title):
    qual_match = re.search(
        r"(B\.?Com|B\.?Tech|MBA|CA|CPA|EA|Bachelor|Master|Graduate|Post.?Graduate)[^\n.]{0,80}",
        desc, re.IGNORECASE,
    )
    if qual_match:
        return qual_match.group(0).strip()[:120]
    return "Graduate / Post-Graduate (Accounting / Finance preferred)"


def main():
    log("=" * 50)
    log("US Tax Jobs Bot — LinkedIn Only")
    log("=" * 50)

    if not config.BOT_TOKEN:
        log("ERROR: BOT_TOKEN not set.")
        print("ERROR: BOT_TOKEN not set in config!")
        return
    if not config.CHAT_ID:
        log("ERROR: CHAT_ID not set.")
        print("ERROR: CHAT_ID not set in config!")
        return

    log(f"BOT_TOKEN present: {len(config.BOT_TOKEN)} chars")
    log(f"CHAT_ID: {config.CHAT_ID}")

    state = load_state()
    stats = load_stats()

    state = handle_commands(state, stats)
    save_state(state)

    if state.get("paused"):
        log("Bot is PAUSED. Send /resume to restart.")
        return

    # Calculate time window: only fetch jobs since last run (+ 5 min buffer)
    last_run = state.get("last_run_at", "")
    if last_run:
        try:
            last_dt = datetime.fromisoformat(last_run)
            elapsed = (datetime.utcnow() - last_dt).total_seconds()
            since_seconds = int(elapsed) + 300  # add 5 min buffer
        except Exception:
            since_seconds = 2400  # fallback: 40 minutes
    else:
        since_seconds = 2400  # first run: 40 minutes

    # Cap: minimum 30 min, maximum 2 hours
    since_seconds = max(1800, min(since_seconds, 7200))

    state["last_run_at"] = datetime.utcnow().isoformat()
    save_state(state)

    log(f"Fetch window: {since_seconds // 60} minutes")

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen jobs.")

    try:
        jobs = fetch_all_jobs(since_seconds=since_seconds)
    except Exception as e:
        log(f"Scrape error (will continue with empty list): {e}")
        jobs = []

    print(f"DEBUG: Total jobs scraped: {len(jobs)}")
    log(f"Total jobs scraped: {len(jobs)}")

    india_jobs = [j for j in jobs if is_india_location(j)]
    log(f"India/Remote: {len(india_jobs)} out of {len(jobs)} total.")
    print(f"DEBUG: India jobs: {len(india_jobs)}")

    us_tax_jobs = [j for j in india_jobs if is_us_tax_job(j)]
    log(f"US Tax relevant: {len(us_tax_jobs)} out of {len(india_jobs)} India/Remote jobs.")
    print(f"DEBUG: US Tax jobs: {len(us_tax_jobs)}")

    new_jobs = [j for j in us_tax_jobs if _dedup_key(j) not in seen]
    new_jobs.sort(key=lambda j: str(j.get("posted") or j.get("fetched_at") or ""))
    log(f"New jobs to send: {len(new_jobs)}")

    if not new_jobs:
        log("No new US Tax jobs this cycle.")
        save_seen(seen)
        save_stats(stats)
        return

    if len(new_jobs) > config.MAX_JOBS_PER_CYCLE:
        log(f"Capping to {config.MAX_JOBS_PER_CYCLE} jobs this cycle.")
        new_jobs = new_jobs[:config.MAX_JOBS_PER_CYCLE]

    sent = 0
    for job in new_jobs:
        job = enrich_job(job)
        desc  = job.get("description", "")
        title = job.get("title", "")
        if not job.get("_experience"):
            job["_experience"] = extract_experience(desc, title)
        if not job.get("_qualification"):
            job["_qualification"] = extract_qualification(desc, title)

        try:
            ok = send_job(job)
            if ok:
                seen.add(_dedup_key(job))
                sent += 1
                stats["sent"] += 1
                company = job.get("company", "Other")
                stats["companies"][company] = stats["companies"].get(company, 0) + 1
                log(f"  Sent: {job['title']} @ {job['company']}")
            else:
                log(f"  Failed: {job['title']}")
        except Exception as e:
            log(f"  Error: {e}")

    save_seen(seen)
    save_stats(stats)
    log(f"Done. Sent {sent} new jobs. Today total: {stats['sent']}. Tracked: {len(seen)}")


if __name__ == "__main__":
    main()
