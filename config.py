import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# 3 BROAD KEYWORDS - Gets maximum jobs
KEYWORDS = [
    "US Tax",
    "Tax Preparation",
    "Tax Compliance",
]

# 17 LOCATIONS - India focus
LOCATIONS = [
    "Hyderabad",
    "Bangalore",
    "Mumbai",
    "Chennai",
    "Pune",
    "Delhi",
    "Noida",
    "Gurgaon",
    "Kolkata",
    "Ahmedabad",
    "Kochi",
    "Coimbatore",
    "Vizag",
    "Chandigarh",
    "Jaipur",
    "Remote India",
    "India",
]

MAX_JOBS_PER_CYCLE = 15
