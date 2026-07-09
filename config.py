import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID   = os.environ.get("CHAT_ID", "")

# LinkedIn search — Top 50 Tax Software Testing titles + combo searches
KEYWORDS = [
    # Tax Software QA (1–10)
    "Tax Software QA Analyst",
    "US Tax Software QA Analyst",
    "Tax Software Tester",
    "Tax QA Engineer",
    "Senior Tax QA Analyst",
    "Tax QA Specialist",
    "Tax Software Quality Engineer",
    "US Tax QA Engineer",
    "Tax Quality Assurance Analyst",
    "Senior Tax Software QA Analyst",
    # E-File / Schema (11–20)
    "E-File Analyst",
    "E-File QA Analyst",
    "E-File Compliance Analyst",
    "E-File Specialist",
    "XML Schema Analyst",
    "Tax Schema Analyst",
    "ATS Analyst",
    "Schema Validation Analyst",
    "Tax Schema Developer",
    # Regulatory QA (21–30)
    "Regulatory QA Analyst Tax",
    "Regulatory QA Engineer Tax",
    "Tax Regulatory Analyst",
    "Compliance QA Analyst Tax",
    "Tax Compliance QA Analyst",
    "Form QA Analyst",
    "Tax Form QA Analyst",
    "Tax Form Tester",
    "Tax Compliance Tester",
    "Regulatory Compliance QA Tax",
    # Manual / Functional — Tax-prefixed (31–40)
    "Tax Manual Test Engineer",
    "Tax Functional QA Analyst",
    "Tax Functional Test Analyst",
    "Tax Regression Test Analyst",
    "Tax UAT Analyst",
    "Tax Test Analyst",
    "Tax Software Test Analyst",
    "Tax Software Tester",
    "Tax Test Engineer",
    "Tax QA Tester",
    # Leadership — Tax-prefixed (41–50)
    "Tax QA Lead",
    "Senior Tax QA Analyst",
    "Tax QA Manager",
    "Senior Tax Test Analyst",
    "Tax Test Lead",
    "Tax QA Engineer Lead",
    "Lead QA E-File Analyst",
    "Senior Tax QA Engineer",
    "Tax QA Consultant",
    "Tax Test Manager",
    # LinkedIn combo searches
    "Tax Software QA",
    "E-File Analyst Tax",
    "XML Schema Tax",
    "GoSystem QA",
    "ONESOURCE Testing",
    "ATS E-File",
    "Tax QA Hyderabad",
    "Lacerte Testing",
    "ProSeries QA",
    "Schema Validation Tax",
    "MeF ATS",
    "Tax Form QA",
    "Regulatory QA Tax",
    "Tax Compliance Testing",
    "Tax Software Testing",
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
