import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# ALL 100 exact keywords from user's list - any 1 keyword in description → POST
KEYWORDS = [
    # Tax Forms (1–20)
    "Form 1040", "Form 1040NR", "Form 1040SR", "Form 1041", "Form 1120",
    "Form 1120S", "Form 1065", "Form 990", "Form 1099", "W-2",
    "Schedule A", "Schedule B", "Schedule C", "Schedule D", "Schedule E",
    "Schedule F", "Schedule K-1", "Schedule SE", "Form 2441", "Form 8863",
    # IRS / Regulatory (21–35)
    "IRS", "IRS Guidelines", "IRS Regulations", "Department of Revenue", "DOR",
    "Federal Tax", "State Tax", "Tax Compliance", "Tax Law", "Tax Code",
    "Tax Reform", "Tax Withholding", "Tax Liability", "Tax Deductions", "Tax Credits",
    # Preparation Keywords (36–50)
    "Tax Preparation", "Tax Return Preparation", "Tax Filing", "Tax Review", "Tax Reviewer",
    "Tax Return Review", "Quality Review", "Tax Advisory", "Client Returns", "Tax Planning",
    "Tax Research", "Tax Compliance Review", "Return Review", "Tax Processing", "Tax Engagement",
    # Software (51–65)
    "Lacerte", "ProSeries", "GoSystem", "ONESOURCE", "UltraTax",
    "CCH Axcess", "ProSystem fx", "Drake", "ATX", "TaxWise",
    "TaxAct", "TaxSlayer", "ProConnect", "CrossLink", "H&R Block Software",
    # Entity Types (66–75)
    "Individual Tax", "Corporate Tax", "Partnership Tax", "S-Corporation", "Fiduciary Tax",
    "Non-Resident Tax", "Exempt Organization", "Trust Tax", "Estate Tax", "Self-Employed Tax",
    # Income Types (76–85)
    "W-2 Income", "1099 Income", "Rental Income", "Business Income", "Capital Gains",
    "Dividend Income", "Interest Income", "Self-Employment Income", "Foreign Income", "Passive Income",
    # Combination Keywords (86–100)
    "1040 Preparation", "1040 Review", "1041 Preparation", "1065 Review", "1120 Preparation",
    "W-2 Processing", "1099 Processing", "IRS Compliance Review", "Federal State Tax Preparation",
    "Individual Corporate Tax", "Tax Return QA", "Tax Software Review", "Multi-State Tax Filing",
    "Tax Deadline Compliance", "Client Tax Advisory",
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
