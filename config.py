import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# Broad search terms - filter by description keywords (3+ matches required)
# These are just to get initial results - ACTUAL filtering happens by description
KEYWORDS = [
    "tax",
    "job",
]

# India US-Tax delivery hubs + remote. "India" already covers smaller hubs
# (Kochi, Coimbatore, Ahmedabad, Noida, etc.) via LinkedIn's country search,
# and INDIA_LOCATION in run_once.py keeps those cities in the results.
LOCATIONS = [
    "Remote",
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Mumbai",
    "Pune",
    "Gurgaon",
    "Noida",
    "Delhi",
    "Kolkata",
    "Ahmedabad",
    "Jaipur",
    "Indore",
    "Chandigarh",
    "Kochi",
    "Coimbatore",
    "Lucknow",
]

MAX_JOBS_PER_CYCLE = 15
