# US Tax Jobs Bot

A Telegram bot that automatically monitors and sends US Tax job postings every 10 minutes — runs free on GitHub Actions, no server or laptop needed.

## What It Does

- Scrapes LinkedIn every 10 minutes for US Tax jobs in India
- Filters only genuine US Tax roles (1040, 1041, 1120, 1065, 990, 5500, IRS, Federal Tax etc.)
- Uses Google Gemini AI to extract real Roles & Responsibilities, Skills, and Experience from each job description
- Sends formatted job posts to a Telegram channel
- No duplicate jobs — tracks previously seen jobs automatically
- Covers locations: Hyderabad, Bangalore, Chennai, Tamil Nadu, Kerala, Remote

## Job Post Format

Each job is sent to Telegram in this format:

```
🔥 Job Opportunity at Deloitte

💼 Role: US Tax Analyst
📍 Location: Hyderabad (Hybrid)
🎓 Qualification: B.Com / CA / CPA
👨‍💻 Experience: 3-5 Years (US Tax)

📌 Roles & Responsibilities:
• Prepare US individual tax returns (Form 1040, 1041)
• Coordinate with IRS on audit matters
• Review federal and state tax filings
• Ensure compliance with US tax regulations
• Support e-file processes and ATS testing

🧠 Skills: US Tax, 1040/1041, IRS, CCH, MS Excel
🔗 Apply Here:
https://linkedin.com/jobs/...

📋 LinkedIn
```

## Tech Stack

| Component | Tool |
|-----------|------|
| Scheduling | GitHub Actions (free) |
| Job Scraping | LinkedIn Guest API |
| AI Extraction | Google Gemini Flash (free) |
| Notifications | Telegram Bot API |
| Language | Python 3.11 |

## Setup

### 1. Clone this repo

### 2. Create a Telegram Bot
- Message [@BotFather](https://t.me/BotFather) on Telegram
- Create a new bot → copy the **Bot Token**
- Add the bot to your channel as admin
- Copy your **Channel Chat ID**

### 3. Get a Free Gemini API Key
- Go to [aistudio.google.com](https://aistudio.google.com)
- Click **Get API Key** → Create API key
- Free tier: 1,500 requests/day — more than enough

### 4. Add GitHub Secrets
Go to your repo → **Settings** → **Secrets and variables** → **Actions** → add:

| Secret Name | Value |
|-------------|-------|
| `BOT_TOKEN` | Your Telegram bot token |
| `CHAT_ID` | Your Telegram channel chat ID |
| `GEMINI_API_KEY` | Your Google Gemini API key |

### 5. Run the Workflow
- Go to **Actions** tab → **US Tax Jobs Bot** → **Run workflow**
- First run: seeds baseline (no messages sent, marks existing jobs as seen)
- Second run onwards: sends only NEW jobs

## Files

```
Telegram Bot/
├── run_once.py       # Main runner — fetches, filters, enriches, sends
├── scraper.py        # LinkedIn scraper
├── sender.py         # Telegram message formatter and sender
├── config.py         # Keywords, locations, company sites
├── seen_jobs.json    # Tracks sent jobs (auto-updated by GitHub Actions)
├── requirements.txt  # Python dependencies
└── .github/
    └── workflows/
        └── bot.yml   # GitHub Actions schedule (every 10 minutes)
```

## Keywords Monitored

US Tax, US Taxation, Tax Analyst, Tax Compliance, Tax Preparation, Tax Consultant, IRS, 1040, 1041, 1120, 1065, 990, 5500, Federal Tax, State Tax, Tax E-Filing, Tax Software, Tax SME, Direct Tax, and more.

## Filters

**Included:** Jobs containing US federal/state tax terms (IRS, 1040, 1041, 1120, 1065 etc.)

**Excluded:** IT Recruiters, GST/VAT jobs, Selenium testers, Accounts Payable/Receivable, non-tax software engineers

## Notes

- GitHub Actions free tier allows up to 2,000 minutes/month — this bot uses ~2 min per run × 144 runs/day = well within limits
- `seen_jobs.json` is automatically committed back to the repo after each run to persist state
- If Gemini AI is unavailable, the bot falls back to regex-based extraction automatically
