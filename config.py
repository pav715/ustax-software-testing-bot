import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID   = os.environ.get("CHAT_ID", "")

# LinkedIn search — resume-aligned tax software QA / e-file / ATS only
KEYWORDS = [
    "Tax Software Testing",
    "Tax Software QA",
    "E-File Analyst",
    "QA E-File Analyst",
    "E-File Testing",
    "Tax E-File Testing",
    "ATS Tax Testing",
    "Automated Test System Tax",
    "Tax ATS",
    "Schema Validation Tax",
    "XML Schema Tax",
    "Tax Form Testing",
    "Form 1040 Testing",
    "Form 1041 Testing",
    "Lacerte QA",
    "Lacerte Testing",
    "ProSeries QA",
    "ProSeries Testing",
    "UltraTax QA",
    "UltraTax Testing",
    "GoSystem QA",
    "GoSystem Testing",
    "ONESOURCE QA",
    "ONESOURCE Testing",
    "Drake Tax QA",
    "Drake Tax Testing",
    "Thomson Reuters Tax QA",
    "Intuit Tax QA",
    "H&R Block Tax QA",
    "Regulatory Analyst Tax Software",
    "Tax Product Testing",
    "Tax Validation",
    "MEF Testing",
    "Tax Diagnostics",
    "Print E-File Compliance",
    "ATX Tax QA",
    "TaxSlayer QA",
    "TaxAct QA",
    "ProConnect Tax QA",
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
