"""LinkedIn job scraper — guest API, no login needed."""
import hashlib
import re
import time
import random
from datetime import datetime
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
import config

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
})


def _job_id(url, title, company):
    raw = f"{url}{title}{company}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _delay():
    time.sleep(random.uniform(0.6, 1.2))


def _ist_hour():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Asia/Kolkata")).hour
    except Exception:
        return datetime.utcnow().hour


def _rotated_slice(items, limit, hour=None):
    if not items or limit <= 0 or len(items) <= limit:
        return list(items)
    if hour is None:
        hour = _ist_hour()
    start = (hour * limit) % len(items)
    chunk = items[start : start + limit]
    if len(chunk) < limit:
        chunk += items[: limit - len(chunk)]
    return chunk


def _linkedin_scan_set():
    kw_limit = getattr(config, "LINKEDIN_KEYWORD_LIMIT", 30)
    loc_limit = getattr(config, "LINKEDIN_LOCATION_LIMIT", 6)
    kws = _rotated_slice(config.KEYWORDS, kw_limit)
    locs = config.LOCATIONS[:loc_limit]
    return kws, locs


def _make_job(title, company, location, url, posted=""):
    return {
        "id": _job_id(url, title, company),
        "title": title,
        "company": company,
        "location": location,
        "url": url,
        "posted": posted,
        "experience": "",
        "skills": "",
        "description": "",
        "source": "LinkedIn",
        "fetched_at": datetime.now().isoformat(),
    }


def scrape_linkedin(keyword, location, since_seconds=86400):
    jobs = []
    try:
        url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
            f"keywords={quote(keyword)}&location={quote(location)}"
            f"&f_TPR=r{since_seconds}&sortBy=DD&start=0"
        )
        for attempt in range(3):
            r = SESSION.get(url, timeout=8)
            if r.status_code == 200:
                break
            if r.status_code in (429, 503) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            print(f"  [LinkedIn] HTTP {r.status_code} — '{keyword}' / {location}")
            return jobs

        soup = BeautifulSoup(r.content, "html.parser")
        for card in soup.find_all("li")[:15]:
            try:
                h3 = card.find("h3")
                h4 = card.find("h4")
                loc_tag = card.find("span", class_=re.compile("job-search-card__location"))
                a_tag = card.find("a", href=True)
                t_tag = card.find("time")
                title = h3.get_text(strip=True) if h3 else ""
                company = h4.get_text(strip=True) if h4 else ""
                loc_str = loc_tag.get_text(strip=True) if loc_tag else location
                link = a_tag["href"].split("?")[0] if a_tag else ""
                posted = t_tag.get("datetime", "") if t_tag else ""
                if title and link:
                    jobs.append(_make_job(title, company, loc_str, link, posted))
            except Exception:
                pass
    except Exception as e:
        print(f"  [LinkedIn] Error: {e}")
    print(f"  [LinkedIn] '{keyword}' / {location} — {len(jobs)} jobs")
    return jobs


def fetch_all_jobs(since_seconds=86400):
    all_jobs = []
    seen = set()

    print(f"\n[LinkedIn] Scanning (last {since_seconds // 3600}h)...")
    linkedin_kws, linkedin_locs = _linkedin_scan_set()
    print(f"  Batch: {len(linkedin_kws)} keywords × {len(linkedin_locs)} cities (IST hour {_ist_hour()})")
    for kw in linkedin_kws:
        for loc in linkedin_locs:
            for job in scrape_linkedin(kw, loc, since_seconds):
                key = job.get("url") or job.get("id")
                if key and key not in seen:
                    seen.add(key)
                    all_jobs.append(job)
            _delay()

    all_jobs.sort(key=lambda j: j.get("posted") or j.get("fetched_at") or "", reverse=True)
    print(f"\n  Total unique LinkedIn jobs: {len(all_jobs)}")
    return all_jobs
