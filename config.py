import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# Search term to fetch jobs - ACTUAL filtering happens in run_once.py
# by checking if description has 3+ keywords from the 100-keyword list
KEYWORDS = [
    "US tax",
    "US taxation",
]

# India locations ONLY + Remote (work from home)
# Remote = work from home, NOT USA states
LOCATIONS = [
    "Remote",
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
