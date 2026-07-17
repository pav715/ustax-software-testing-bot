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
from experience_utils import extract_experience_from_job, pick_linkedin_criteria_experience

SEEN_FILE  = "seen_jobs.json"
STATS_FILE = "stats.json"
STATE_FILE = "bot_state.json"


def _write_cycle_report(scraped=0, india=0, matched=0, new=0, sent=0, seen_total=0, **extra):
    data = {
        "scraped": scraped, "india": india, "matched": matched,
        "new": new, "sent": sent, "seen_total": seen_total, **extra,
        "at": datetime.utcnow().isoformat(),
    }
    try:
        with open("last_cycle.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def _check_telegram():
    try:
        base = f"https://api.telegram.org/bot{config.BOT_TOKEN}"
        me = requests.get(f"{base}/getMe", timeout=10)
        chat = requests.get(f"{base}/getChat", params={"chat_id": config.CHAT_ID}, timeout=10)
        ok = me.status_code == 200 and chat.status_code == 200
        return ok, f"getMe={me.status_code} getChat={chat.status_code} {chat.text[:80]}"
    except Exception as e:
        return False, str(e)

BLOCKLIST = re.compile(
    r"\b("
    r"recruiter|recruitment|talent\s*acquisition|bench\s*sales|"
    r"us\s*it\s*recruiter|it\s*recruiter|"
    r"software\s*engineer(?!\s*tax)|software\s*developer(?!\s*tax)|"
    r"payroll(?!\s*tax)|accounts\s*payable|accounts\s*receivable|"
    r"statutory\s*audit|business\s*development|sales\s*executive|"
    r"\bgst\b|goods\s*and\s*services\s*tax|gstn|gst\s*compliance|gst\s*specialist|gst\s*manager|gst\s*consultant|gst\s*filing|gst\s*returns|gst\s*audit|gst\s*advisory|"
    r"income\s*tax\s*(?!withholding)|income\s*tax\s*consultant|income\s*tax\s*executive|"
    r"direct\s*tax(?!\s*analyst\s*(?:us|federal|state))|india\s*tax|domestic\s*tax|indian\s*tax|"
    r"\btds\b|\btcs\b|tax\s*deducted|tax\s*collected|tds\s*analyst|tds\s*filing|"
    r"indirect\s*tax(?!\s*analyst\s*(?:us|federal))|"
    r"\bvat\b(?!\s*us)|service\s*tax|excise\s*duty|customs\s*duty|"
    r"transfer\s*pricing|tax\s*litigation|"
    r"chartered\s*accountant|ca\s*article|ca\s*analyst|"
    r"(?<!us\s)(?<!federal\s)finance\s*analyst(?!\s*us)|accounts\s*analyst|^accountant$|"
    r"financial\s*analyst(?!\s*(?:us|tax))|finance\s*executive|accounts\s*executive|"
    r"tax\s*auditor|statutory\s*compliance|tax\s*compliance\s*executive(?!\s*us)"
    r")\b",
    re.IGNORECASE,
)

INDIAN_TAX_BLOCKLIST = re.compile(
    r"\b("
    r"gst\s*analyst|gst\s*compliance|gst\s*executive|gst\s*specialist|gst\s*manager|"
    r"gst\s*consultant|gst\s*filing|gst\s*returns|gst\s*audit|gst\s*advisory|"
    r"income\s*tax\s*analyst|income\s*tax\s*consultant|income\s*tax\s*executive|"
    r"direct\s*tax\s*analyst|direct\s*tax\s*consultant|direct\s*tax\s*manager|"
    r"india\s*tax\s*analyst|india\s*tax\s*consultant|domestic\s*tax|"
    r"tds\s*analyst|tds\s*compliance|tcs\s*analyst|tds\s*executive|tds\s*filing|"
    r"indirect\s*tax\s*analyst|indirect\s*tax\s*consultant|indirect\s*tax\s*manager|"
    r"vat\s*analyst|service\s*tax|excise\s*duty|customs\s*duty|"
    r"tax\s*litigation|indirect\s*tax\s*specialist|"
    r"tax\s*auditor|tax\s*litigation\s*specialist|transfer\s*pricing|"
    r"tax\s*compliance\s*executive|statutory\s*compliance|"
    r"itr|itr-1|itr-2|itr-3|itr-4|itr-5|itr-6|itr-7|"
    r"form\s*16|form\s*16a|form\s*24q|"
    r"pan\s*number|aadhar|aadhaar|cin|gstin|"
    r"goods\s*and\s*services\s*tax|section\s*80|fy20[0-9]{2}|ay20[0-9]{2}|"
    r"tds|tcs|advance\s*tax|challan|saral|"
    r"indian\s*tax|india\s*tax|ato"
    r")\b",
    re.IGNORECASE,
)

# Top 50 titles + 100 keywords — tax software testing only
TESTING_KEYWORDS = [
    # E-File / ATS / Schema (1–25)
    "ats", "e-file", "efile", "ats submission", "e-file approval", "print approval",
    "e-file compliance", "print compliance", "state e-file", "federal e-file",
    "ats test client", "e-file authorization", "dor approval", "mef", "modernized e-file",
    "e-file diagnostics", "e-file schema", "e-file module", "electronic filing",
    "state authority approval", "xml schema", "xsd schema", "schema validation",
    "schema mapping", "xml tagging",
    # Tax Software (26–50)
    "lacerte", "proseries", "gosystem", "onesource", "ultratax", "cch axcess",
    "prosystem fx", "drake", "atx", "taxwise", "taxact", "taxslayer", "proconnect",
    "crosslink", "gosystem tax rs", "tax software", "tax software qa", "tax form software",
    "tax platform", "tax system", "tax application", "tax tool", "tax engine",
    "tax solution", "filing software",
    # QA / Testing — tax context required via filter (51–70)
    "tax qa", "tax testing", "tax tester", "tax software testing", "tax software qa",
    "manual testing", "regression testing", "functional testing", "uat",
    "user acceptance testing", "test cases", "test scenarios", "bug tracking",
    "defect management", "pre-production testing", "post-production testing",
    "compliance testing", "software validation", "end-to-end testing",
    "integration testing", "smoke testing", "sanity testing", "quality assurance",
    # Tax Forms (71–80)
    "form 1040", "form 1041", "form 1120", "form 1120s", "form 1065", "form 990",
    "schedule k-1", "individual tax", "corporate tax", "partnership tax",
    # Tools / Tech (81–90)
    "lasermap", "2d barcode", "xmlspy", "altova xmlspy",
    # Regulatory / Compliance (91–100)
    "tax compliance", "regulatory compliance", "tax form development", "filing product",
    "government liaison", "state authority", "irs compliance", "dor", "tax law changes",
    "compliance qa",
    # Title keywords (Top 50 roles)
    "tax software qa analyst", "us tax software qa analyst", "tax software tester",
    "tax qa engineer", "senior tax qa analyst", "tax qa specialist",
    "tax software quality engineer", "us tax qa engineer", "tax quality assurance analyst",
    "senior tax software qa analyst", "e-file analyst", "e-file qa analyst",
    "e-file compliance analyst", "e-file specialist", "xml schema analyst",
    "tax schema analyst", "ats analyst", "schema validation analyst", "tax schema developer",
    "regulatory qa analyst", "regulatory qa engineer", "tax regulatory analyst",
    "compliance qa analyst", "tax compliance qa analyst", "form qa analyst",
    "tax form qa analyst", "tax form tester", "tax compliance tester",
    "regulatory compliance qa", "tax manual test engineer", "tax functional qa analyst",
    "tax functional test analyst", "tax regression test analyst", "tax uat analyst",
    "tax test analyst", "tax software test analyst", "tax test engineer", "tax qa tester",
    "tax qa lead", "tax qa manager", "tax test lead", "tax qa engineer lead",
    "lead qa e-file analyst", "senior tax qa engineer", "tax qa consultant", "tax test manager",
    # Expanded titles / products
    "tax product qa", "tax application qa", "tax platform qa", "tax validation analyst",
    "tax diagnostics analyst", "print and efile", "state e-file", "federal e-file",
    "electronic filing", "dor approval", "ats test client", "xsd schema", "xml validation",
    "mef qa", "mef analyst", "irs compliance qa", "filing product qa", "compliance testing tax",
    "cch axcess", "ultratax", "drake tax", "prosystem fx", "proconnect", "vertex", "avalara",
    "wolters kluwer", "thomson reuters", "tax integration test", "tax end to end",
    "tax smoke test", "tax sanity test", "principal tax qa", "tax software validation",
]

# Required signal — at least ONE must be present (not product names alone)
REQUIRED_TAX_SIGNAL = re.compile(
    r"\b("
    r"tax\s*software|tax\s*(?:qa|testing|tester)|"
    r"\bats\b|automated\s*test\s*system|"
    r"e[\s-]*file|efile|"
    r"\bxml\b|xml\s*schema|xsd|"
    r"1040|form\s*1040|"
    r"\bdor\b|department\s*of\s*revenue|"
    r"\bmef\b|modernized\s*e[\s-]*file|"
    r"lacerte|proseries|gosystem|ultratax|onesource|cch\s*axcess|drake|proconnect|prosystem"
    r")\b",
    re.IGNORECASE,
)

TESTING_SIGNAL = re.compile(
    r"\b("
    r"testing|tester|qa|quality|validation|diagnostics|"
    r"e[\s-]*file|efile|ats|schema|xml|xsd|mef|regulatory|compliance|"
    r"automated\s*test|test\s*case|test\s*client|test\s*scenario|bug|defect|"
    r"manual\s*test|functional\s*test|regression|uat|smoke|sanity|integration"
    r")\b",
    re.IGNORECASE,
)

# Pure IT testing — block only when no tax software context
GENERIC_IT_BLOCKLIST = re.compile(
    r"\b("
    r"\bsdet\b|selenium|cypress|playwright|appium|"
    r"mobile\s*testing|web\s*testing|api\s*testing|performance\s*testing|"
    r"devops|full\s*stack|\.net\s*testing|java\s*developer"
    r")\b",
    re.IGNORECASE,
)

# Generic QA titles (31–50) — need tax/e-file/schema signal (no variable-width lookbehind)
GENERIC_QA_TITLE = re.compile(
    r"\b("
    r"manual\s*test\s*engineer|functional\s*(?:qa|test)\s*analyst|"
    r"regression\s*test\s*analyst|\buat\s*analyst|"
    r"test\s*analyst|software\s*test\s*analyst|software\s*tester|"
    r"test\s*engineer|qa\s*tester|qa\s*lead|senior\s*qa\s*analyst|"
    r"qa\s*manager|test\s*lead|qa\s*engineer\s*lead|"
    r"senior\s*qa\s*engineer|qa\s*consultant|test\s*manager"
    r")\b",
    re.IGNORECASE,
)


def _is_generic_qa_title(title):
    """Generic IT QA title without tax/e-file in the title itself."""
    if not title or not GENERIC_QA_TITLE.search(title):
        return False
    t = title.lower()
    if re.search(r"\btax\b", t):
        return False
    if re.search(r"e[\s-]*file|efile", t):
        return False
    return True

TESTING_ROLE_TITLE = re.compile(
    r"\b("
    # Tax Software QA (1–10)
    r"(?:us|u\.s\.|senior)?\s*tax\s*software\s*(?:qa|quality|testing|tester)\s*(?:analyst|engineer|specialist)?|"
    r"tax\s*software\s*(?:tester|quality\s*engineer)|"
    r"(?:senior|us|u\.s\.)?\s*tax\s*qa\s*(?:analyst|engineer|specialist)|"
    r"tax\s*quality\s*assurance\s*analyst|senior\s*tax\s*software\s*qa\s*analyst|"
    # E-File / Schema (11–20)
    r"e[\s-]*file\s*(?:analyst|qa\s*analyst|compliance\s*analyst|specialist)|"
    r"xml\s*schema\s*analyst|tax\s*schema\s*(?:analyst|developer)|"
    r"ats\s*analyst|schema\s*validation\s*analyst|"
    # Regulatory QA (21–30)
    r"(?:tax\s*)?regulatory\s*(?:qa|compliance)\s*(?:analyst|engineer)|"
    r"tax\s*regulatory\s*analyst|(?:tax\s*)?compliance\s*qa\s*analyst|"
    r"tax\s*compliance\s*qa\s*analyst|form\s*qa\s*analyst|tax\s*form\s*qa\s*analyst|"
    r"tax\s*form\s*tester|tax\s*compliance\s*tester|regulatory\s*compliance\s*qa|"
    # Manual / Leadership with Tax prefix (31–50)
    r"tax\s*(?:manual\s*test|functional\s*(?:qa|test)|regression\s*test|uat|test|qa)\s*(?:engineer|analyst|tester|lead|manager)?|"
    r"tax\s*software\s*test\s*analyst|tax\s*test\s*(?:engineer|analyst|lead|manager)|"
    r"tax\s*qa\s*(?:lead|manager|consultant|tester)|"
    r"lead\s*qa\s*e[\s-]*file\s*analyst|senior\s*tax\s*qa\s*(?:analyst|engineer)|"
    r"tax\s*qa\s*engineer\s*lead|"
    # Core tax software testing
    r"tax\s*(?:software|application|product)\s*(?:testing|tester|qa|validation)|"
    r"qa\s*(?:&|and)?\s*e[\s-]*file|e[\s-]*file\s*(?:&|and)?\s*qa|"
    r"schema\s*(?:validation|testing|analyst)|xml\s*(?:schema|testing|validation)|"
    r"tax\s*(?:schema|xml|e[\s-]*file|ats|validation|diagnostics)|filing\s*product|"
    r"tax\s*(?:product|application|platform)\s*qa|"
    r"(?:lacerte|proseries|gosystem|ultratax|onesource|cch\s*axcess|drake)\s*qa|"
    r"print\s*(?:and|&)\s*e[\s-]*file|state\s*e[\s-]*file|federal\s*e[\s-]*file|"
    r"mef\s*(?:qa|analyst)?|tax\s*validation\s*analyst|tax\s*diagnostics\s*analyst"
    r")\b",
    re.IGNORECASE,
)

INDIA_LOCATION_KEYWORDS = [
    "india", "hyderabad", "bangalore", "bengaluru", "chennai", "mumbai", "pune", "delhi",
    "gurgaon", "gurugram", "noida", "kolkata", "ahmedabad", "jaipur", "indore", "chandigarh",
    "kochi", "coimbatore", "lucknow", "visakhapatnam", "vizag",
]

FOREIGN_LOCATION_KEYWORDS = [
    "usa", "united states", "u.s.", "canada", "uk", "united kingdom", "australia", "europe",
    "egypt", "middle east", "africa", "singapore", "malaysia", "sweden", "sverige", "japan",
    "dubai", "germany", "france",
]


def _keyword_hits(text, keywords):
    hits = []
    for kw in keywords:
        if len(kw) <= 4:
            if re.search(rf"\b{re.escape(kw)}\b", text):
                hits.append(kw)
        elif kw in text:
            hits.append(kw)
    return hits


def is_india_location(job):
    """Return True for India on-site, India-tied remote, or India-targeted search results."""
    loc = (job.get("location") or "").lower()
    search_loc = (job.get("search_location") or "").lower()
    title = (job.get("title") or "").lower()

    # GitHub Actions (US IP): LinkedIn often returns foreign loc for India city searches — trust search_loc
    if search_loc and any(kw in search_loc for kw in INDIA_LOCATION_KEYWORDS):
        return True

    if not loc.strip():
        return True

    if any(kw in loc for kw in FOREIGN_LOCATION_KEYWORDS):
        return False

    if any(kw in loc for kw in INDIA_LOCATION_KEYWORDS):
        return True

    if "remote" in loc:
        context = f"{loc} {title}"
        return "india" in context or any(kw in context for kw in INDIA_LOCATION_KEYWORDS)

    return False


_SEARCH_TESTING_INTENT = re.compile(
    r"\b(tax|qa|test|quality|software|e[\s-]?file|efile|schema|ats|validation|mef|regulatory|compliance)\b",
    re.IGNORECASE,
)


def _passes_search_trust(job):
    """Trust LinkedIn niche keyword search — title may not repeat full query."""
    sk_l = (job.get("search_keyword") or "").lower()
    title = (job.get("title") or "").lower()
    if not sk_l or not _SEARCH_TESTING_INTENT.search(sk_l):
        return False
    if INDIAN_TAX_BLOCKLIST.search(title) or BLOCKLIST.search(title):
        return False
    if re.search(r"\btax\b", title):
        return True
    if re.search(r"\b(qa|test|quality|software|validation|analyst|engineer|tester|associate|specialist)\b", title):
        if re.search(r"\b(tax|qa|test|quality|software|e[\s-]?file|schema|ats|validation|mef)\b", sk_l):
            return True
    if TESTING_ROLE_TITLE.search(title):
        return True
    return False


def _passes_early_filter(job, role_title_pattern):
    title = job.get("title") or ""
    company = job.get("company") or ""
    sk = job.get("search_keyword") or ""
    title_l = title.lower()
    company_l = company.lower()
    if INDIAN_TAX_BLOCKLIST.search(title_l) or INDIAN_TAX_BLOCKLIST.search(company_l):
        return False
    if BLOCKLIST.search(title_l) or BLOCKLIST.search(company_l):
        return False
    if _passes_search_trust(job):
        return True
    if re.search(r"\btax\b", title_l) and re.search(r"\b(test|qa|quality|software|automation|analyst|associate)\b", title_l):
        return True
    if sk and "tax" in sk.lower() and _title_matches_search(title, sk):
        return True
    if sk and _title_matches_search(title, sk):
        return True
    if role_title_pattern.search(title_l) and re.search(r"\btax\b", title_l):
        return True
    return False


def _has_required_tax_signal(text):
    """Must have tax software, ATS, e-file, XML, 1040, or DOR."""
    return bool(REQUIRED_TAX_SIGNAL.search(text))


def _title_matches_search(title, keyword):
    if not title or not keyword:
        return False
    tl = title.lower()
    kw_l = keyword.lower()
    domain_words = (
        "mortgage", "loan", "credit", "tax", "servicing", "underwrit",
        "financial", "compliance", "testing", "software", "banking", "escrow",
    )
    for d in domain_words:
        if d in kw_l:
            return d in tl
    words = [w for w in re.findall(r"[a-z]+", kw_l) if len(w) > 3]
    return bool(words) and all(w in tl for w in words)


def is_tax_software_testing_job(job):
    """Accept only when tax software / ATS / e-file / XML / 1040 / DOR signal present."""
    desc = (job.get("description") or "").lower()
    title = (job.get("title") or "").lower()
    company = (job.get("company") or "").lower()
    blob = f"{title} {company} {desc}"

    if INDIAN_TAX_BLOCKLIST.search(title) or INDIAN_TAX_BLOCKLIST.search(company):
        return False

    if _passes_search_trust(job):
        print(f"DEBUG: '{job.get('title')}' @ {job.get('company')} matched: search keyword trust")
        return True

    sk_l = (job.get("search_keyword") or "").lower()
    # Title + search intent — pass without description (LinkedIn enrich often rate-limited)
    if re.search(r"\btax\b", title) and (
        TESTING_ROLE_TITLE.search(title)
        or re.search(r"\b(qa|test|testing|software|e[\s-]?file|ats|xml|schema|validation|analyst|associate)\b", title)
        or (sk_l and ("tax" in sk_l or "qa" in sk_l or "test" in sk_l) and _title_matches_search(title, job.get("search_keyword") or ""))
    ):
        if not BLOCKLIST.search(title) and not BLOCKLIST.search(company):
            print(f"DEBUG: '{job.get('title')}' @ {job.get('company')} matched: tax testing title")
            return True

    sk = (job.get("search_keyword") or "")
    if sk and "tax" in sk.lower() and re.search(r"\btax\b", title):
        if re.search(r"\b(test|qa|quality|software|automation|analyst|associate)\b", blob):
            if not BLOCKLIST.search(title) and not INDIAN_TAX_BLOCKLIST.search(blob):
                if _title_matches_search(title, sk) or TESTING_ROLE_TITLE.search(title):
                    print(f"DEBUG: '{job.get('title')}' @ {job.get('company')} matched: search keyword + tax testing")
                    return True

    if GENERIC_IT_BLOCKLIST.search(blob) and not _has_required_tax_signal(blob):
        return False

    if TESTING_ROLE_TITLE.search(title):
        if BLOCKLIST.search(title) or BLOCKLIST.search(company):
            return False
        if _is_generic_qa_title(title) and not _has_required_tax_signal(blob):
            return False
        if re.search(r"\btax\b", title) or _has_required_tax_signal(blob):
            print(f"DEBUG: '{job.get('title')}' @ {job.get('company')} matched: tax software testing title")
            return True
        return False

    if BLOCKLIST.search(blob):
        return False
    if INDIAN_TAX_BLOCKLIST.search(blob):
        return False
    if _is_generic_qa_title(title) and not _has_required_tax_signal(blob):
        return False
    if GENERIC_IT_BLOCKLIST.search(blob) and not _has_required_tax_signal(blob):
        return False

    if not _has_required_tax_signal(blob):
        return False

    matched = _keyword_hits(blob, TESTING_KEYWORDS)
    if matched and TESTING_SIGNAL.search(blob):
        print(f"DEBUG: '{job.get('title')}' @ {job.get('company')} matched: {matched}")
        return True
    return False


def _mark_run_complete(state):
    state["last_run_at"] = datetime.utcnow().isoformat()
    save_state(state)


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


def _norm_dedup_text(s):
    s = (s or "").lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s&]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _dedup_keys(job):
    title = _norm_dedup_text(job.get("title"))
    company = _norm_dedup_text(job.get("company"))
    keys = {f"{title}|{company}"}
    url = job.get("url") or ""
    m = re.search(r"/(\d{8,})", url)
    if m:
        keys.add(f"lid:{m.group(1)}")
    return keys


def _is_seen(job, seen):
    return any(k in seen for k in _dedup_keys(job))


def _mark_seen(job, seen):
    for k in _dedup_keys(job):
        seen.add(k)


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
            if not chat_id or chat_id != str(config.CHAT_ID):
                continue

            api = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"

            if text.startswith("/status"):
                reply = (
                    f"🤖 *US Tax Software Testing Bot — Status*\n\n"
                    f"{'⏸ PAUSED' if state.get('paused') else '✅ RUNNING'}\n\n"
                    f"📊 *Today ({stats['date']}):*\n"
                    f"• Jobs sent: *{stats['sent']}*\n"
                    f"• Companies: *{len(stats['companies'])}*\n"
                    f"⏱ Checks every *{config.CHECK_INTERVAL_LABEL}*\n"
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
    fetched = False
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
                        job["description"] = desc_div.get_text(" ", strip=True)[:4000]
                        fetched = True
                    criteria = soup.find_all("span", class_=re.compile(r"description__job-criteria-text"))
                    exp_line = pick_linkedin_criteria_experience(criteria)
                    if exp_line:
                        job["experience"] = exp_line
    except Exception as e:
        log(f"  [Enrich] error: {e}")
    if fetched:
        time.sleep(1.0)
    return job


def extract_experience(desc, title="", raw_exp=""):
    return extract_experience_from_job(desc, raw_exp)


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
    log("US Tax Software Testing Bot — LinkedIn Only")
    log("=" * 50)

    if not config.BOT_TOKEN or not config.CHAT_ID:
        log("ERROR: BOT_TOKEN or CHAT_ID not set in environment.")
        sys.exit(1)

    log(f"BOT_TOKEN present: {len(config.BOT_TOKEN)} chars")
    log(f"CHAT_ID: {config.CHAT_ID}")
    tg_ok, tg_msg = _check_telegram()
    log(f"Telegram check: {tg_msg}")
    if not tg_ok:
        log("WARNING: Telegram getChat failed — posts may not deliver.")

    state = load_state()
    stats = load_stats()

    state = handle_commands(state, stats)
    save_state(state)

    if state.get("paused"):
        log("Bot is PAUSED. Send /resume to restart.")
        return

    # Calculate time window: only fetch jobs since last run (+ 5 min buffer)
    since_seconds = getattr(config, "SCRAPE_WINDOW_SECONDS", 86400)
    log(f"Fetch window: {since_seconds // 3600} hours")

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen jobs.")

    try:
        jobs = fetch_all_jobs(since_seconds=since_seconds)
    except Exception as e:
        log(f"Scrape error: {e}")
        send_fail_alert(str(e))
        sys.exit(1)

    if os.environ.get("SEED_MODE", "").lower() == "true":
        for job in jobs:
            _mark_seen(job, seen)
        save_seen(seen)
        _mark_run_complete(state)
        log(f"Seed mode: marked {len(jobs)} jobs as seen, sent 0.")
        return

    log(f"Total jobs scraped: {len(jobs)}")

    india_jobs = [j for j in jobs if is_india_location(j)]
    log(f"India jobs: {len(india_jobs)} out of {len(jobs)} total.")

    tax_software_testing_jobs = []
    enrich_budget = getattr(config, "MAX_ENRICH_PER_CYCLE", 30)
    enriched = 0
    for job in india_jobs:
        if not _passes_early_filter(job, TESTING_ROLE_TITLE):
            continue
        if is_tax_software_testing_job(job):
            tax_software_testing_jobs.append(job)
            continue
        if enriched >= enrich_budget:
            continue
        job = enrich_job(job)
        enriched += 1
        if is_tax_software_testing_job(job):
            tax_software_testing_jobs.append(job)

    log(f"Enriched {enriched} jobs (budget {enrich_budget})")

    log(f"Tax Software Testing relevant: {len(tax_software_testing_jobs)} out of {len(india_jobs)} India jobs.")

    new_jobs = [j for j in tax_software_testing_jobs if not _is_seen(j, seen)]
    new_jobs.sort(key=lambda j: str(j.get("posted") or j.get("fetched_at") or ""))
    log(f"New jobs to send: {len(new_jobs)}")

    if not new_jobs:
        log("No new Tax Software Testing jobs this cycle.")
        save_seen(seen)
        save_stats(stats)
        _mark_run_complete(state)
        _write_cycle_report(len(jobs), len(india_jobs), len(tax_software_testing_jobs), 0, 0, len(seen), telegram_ok=tg_ok, telegram_detail=tg_msg)
        return

    if len(new_jobs) > config.MAX_JOBS_PER_CYCLE:
        log(f"Capping to {config.MAX_JOBS_PER_CYCLE} jobs this cycle.")
        new_jobs = new_jobs[:config.MAX_JOBS_PER_CYCLE]

    sent = 0
    for job in new_jobs:
        desc  = job.get("description", "")
        title = job.get("title", "")
        if not job.get("_experience"):
            job["_experience"] = extract_experience(desc, title, job.get("experience", ""))
        if not job.get("_qualification"):
            job["_qualification"] = extract_qualification(desc, title)

        try:
            ok = send_job(job)
            if ok:
                _mark_seen(job, seen)
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
    _mark_run_complete(state)
    _write_cycle_report(len(jobs), len(india_jobs), len(tax_software_testing_jobs), len(new_jobs), sent, len(seen), telegram_ok=tg_ok, telegram_detail=tg_msg)
    log(f"Done. Sent {sent} new jobs. Today total: {stats['sent']}. Tracked: {len(seen)}")


if __name__ == "__main__":
    main()
