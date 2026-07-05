"""
US Tax Jobs — Telegram Bot
Runs 24/7, checks every 1 minute, sends new jobs instantly.
No duplicates. Newest first.

Run: python bot.py
"""
import json
import os
import time
import re
import requests
from datetime import datetime
import config
from scraper import fetch_all_jobs
from sender import send_job
try:
    from sender import send_startup_message
except ImportError:
    def send_startup_message(*args, **kwargs):
        pass

SEEN_FILE = "seen_jobs.json"
LOG_FILE  = "bot.log"

# Defaults for optional config values (config.py may not define these)
CHECK_INTERVAL_MINUTES = getattr(config, "CHECK_INTERVAL_MINUTES", 30)
SHOW_STARTUP_MESSAGE   = getattr(config, "SHOW_STARTUP_MESSAGE", False)


# ── Seen jobs tracker ─────────────────────────────────────────────────
def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()


def save_seen(seen_set):
    # Keep only last 5000 to avoid file bloat
    data = list(seen_set)[-5000:]
    with open(SEEN_FILE, "w") as f:
        json.dump(data, f)


# ── Logging ───────────────────────────────────────────────────────────
def log(msg):
    ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── Telegram setup ────────────────────────────────────────────────────
def setup_telegram():
    """Detect Chat ID on first run."""
    if config.CHAT_ID:
        return True

    log("CHAT_ID not set. Detecting from Telegram updates...")
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates",
            timeout=15
        )
        data = r.json()
        for item in data.get("result", []):
            chat = (
                item.get("channel_post", {}).get("chat")
                or item.get("message", {}).get("chat")
                or {}
            )
            if chat.get("id"):
                chat_id = str(chat["id"])
                config.CHAT_ID = chat_id
                _save_chat_id(chat_id)
                log(f"Chat ID detected and saved: {chat_id}  ({chat.get('title','')})")
                return True

        log("No channel found. Add @USTaxjobs_bot as Admin to your channel, send a message, then restart.")
        return False
    except Exception as e:
        log(f"Telegram setup error: {e}")
        return False


def _save_chat_id(chat_id):
    """Write Chat ID into config.py automatically."""
    try:
        path = os.path.join(os.path.dirname(__file__), "config.py")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(
            r'os\.environ\.get\("CHAT_ID",\s*"[^"]*"\)',
            f'os.environ.get("CHAT_ID", "{chat_id}")',
            content, count=1
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        pass


# ── One scrape cycle ──────────────────────────────────────────────────
def run_cycle(seen):
    log(f"Checking for new jobs... ({len(config.KEYWORDS)} keywords x {len(config.LOCATIONS)} locations)")
    try:
        jobs = fetch_all_jobs()
    except Exception as e:
        log(f"Scrape error: {e}")
        return seen, 0

    # Filter out already-seen jobs
    new_jobs = [j for j in jobs if j["id"] not in seen]

    if not new_jobs:
        log(f"No new jobs found. Total tracked: {len(seen)}")
        return seen, 0

    log(f"Found {len(new_jobs)} new jobs! Sending to Telegram...")

    sent = 0
    for job in new_jobs:   # already sorted newest first by scraper
        try:
            ok = send_job(job)
            if ok:
                seen.add(job["id"])
                sent += 1
                log(f"  Sent: [{job['source']}] {job['title']} @ {job['company']} | {job['location']}")
            else:
                log(f"  Failed to send: {job['title']}")
        except Exception as e:
            log(f"  Error sending job: {e}")

    save_seen(seen)
    log(f"Done. Sent {sent} new jobs. Total tracked: {len(seen)}")
    return seen, sent


# ── Main loop ─────────────────────────────────────────────────────────
def main():
    log("=" * 60)
    log("  US Tax Jobs Telegram Bot")
    log("  Bot: @USTaxjobs_bot")
    log(f"  Check interval: every {CHECK_INTERVAL_MINUTES} minutes")
    log("=" * 60)

    # Setup Telegram
    if not setup_telegram():
        log("Cannot start without CHAT_ID. Exiting.")
        return

    # Load seen jobs
    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen jobs (no duplicates).")

    # Startup message to channel (only if enabled in config)
    if SHOW_STARTUP_MESSAGE:
        send_startup_message(len(config.KEYWORDS), len(config.LOCATIONS))

    # First run immediately
    seen, sent = run_cycle(seen)

    interval = config.CHECK_INTERVAL_MINUTES * 60

    while True:
        next_check = datetime.now().strftime("%H:%M:%S")
        log(f"Sleeping {config.CHECK_INTERVAL_MINUTES} min... (next check after {next_check})")
        time.sleep(interval)
        seen, sent = run_cycle(seen)


if __name__ == "__main__":
    main()
