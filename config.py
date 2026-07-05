import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# 7 search keywords - one from each category (positions 2,22,37,52,67,77,87)
# Filtering: if description has ANY 1 of these keywords → POST
KEYWORDS = [
    "ats",                   # Position 2 (E-File/ATS 1-20)
    "xmlspy",                # Position 22 (XML/Schema 21-35)
    "software qa",           # Position 37 (QA/Testing 36-50) - wait, need to check testing_keywords
    "lacerte",               # Position 52 (Tax Software 51-65)
    "individual tax",        # Position 67 (Tax Forms 66-75)
    "1099 income",           # Position 77 (Income Types 76-85)
    "tax compliance",        # Position 87 (Compliance 89-100)
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
