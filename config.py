import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# 7 optimized search keywords (1 from each category of 100-keyword list)
# Fast + comprehensive: gets jobs from all categories
# Filtering: 1+ keyword from 100-list in description → POST
KEYWORDS = [
    "Form 1040",        # Tax Forms (1-20)
    "IRS",              # IRS/Regulatory (21-35)
    "Tax Preparation",  # Preparation (36-50)
    "E-File",           # Software/Testing (51-65)
    "XML",              # Schema/Tech (covers testing focus)
    "1099 Income",      # Income Types (76-85)
    "Test Cases",       # QA/Testing (testing-specific)
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
