import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# Search terms - BROAD keywords to get maximum jobs (50+)
# Actual filtering happens in run_once.py by description (3+ keywords required)
KEYWORDS = [
    "US tax", "US taxation", "tax", "taxation",
    "tax preparation", "tax return", "tax filing", "tax compliance",
    "tax preparation software", "tax software testing", "e-file",
    "form 1040", "form 1120", "form 1065", "irs",
    "tax analyst", "tax specialist", "tax manager", "tax consultant",
    "tax accountant", "tax auditor", "tax advisor",
    "individual tax", "corporate tax", "partnership tax",
    "payroll tax", "federal tax", "state tax",
    "tax planning", "tax strategy", "tax review",
    "cpa", "enrolled agent", "tax preparer",
    "proseries", "lacerte", "taxwise", "taxact",
    "xml", "schema", "ats", "e-file testing",
    "tax forms", "tax documents", "tax return preparation",
    "quality assurance", "qa testing", "regression testing",
    "tax software", "tax technology", "tax tools",
    "tax regulations", "tax law", "irs regulations",
    "tax deductions", "tax credits", "tax withholding",
    "1099", "w-2", "schedule", "tax reporting",
    "tax associate", "tax executive", "tax officer",
    "form 990", "form 1041", "form 1065",
    "tax compliance officer", "tax operations", "tax processing",
    "tax delivery", "tax services", "tax solutions",
    "tax audit", "tax examination", "tax verification",
    "indirect tax", "estate tax", "trust tax",
    "tax documentation", "tax records", "tax filing software",
]

# India cities ONLY - metro + tier-2 cities
LOCATIONS = [
    # Metro cities (Tier-1)
    "Bangalore",
    "Hyderabad",
    "Mumbai",
    "Delhi",
    "Pune",
    "Chennai",
    "Kolkata",
    # State capitals & major cities (Tier-2)
    "Gurgaon",
    "Noida",
    "Ahmedabad",
    "Chandigarh",
    "Jaipur",
    "Kochi",
    "Coimbatore",
    "Indore",
    "Lucknow",
]

MAX_JOBS_PER_CYCLE = 15
