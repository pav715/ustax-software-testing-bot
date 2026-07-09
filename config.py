import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID   = os.environ.get("CHAT_ID", "")

# LinkedIn search — Tax Software Testing ONLY (no generic SDET/UAT/QA)
KEYWORDS = [
    "Tax Software Testing",
    "Tax Software QA",
    "Tax Application Testing",
    "Tax Technology Testing",
    "Tax QA Engineer",
    "Tax Test Engineer",
    "Tax Automation Testing",
    "E-File Testing",
    "Tax E-File Testing",
    "Tax ATS",
    "Tax Validation",
    "Lacerte Testing",
    "ProSeries Testing",
    "UltraTax Testing",
    "GoSystem Testing",
    "OneSource Testing",
    "Drake Tax Testing",
    "MEF Testing",
    "Tax Product Testing",
    "Tax Software",
    "Tax Technology",
]

LOCATIONS = [
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Kochi",
    "Visakhapatnam",
    "Mumbai",
    "Pune",
    "Delhi",
    "Noida",
    "Gurgaon",
    "Ahmedabad",
    "Kolkata",
]

MAX_JOBS_PER_CYCLE = 15
CHECK_INTERVAL_LABEL = "1 hour"
