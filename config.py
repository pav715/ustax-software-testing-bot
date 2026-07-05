import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# US Tax Software Testing & Technology roles (50 titles + 2 catchall)
# Focus: ATS, E-File, Schema, QA, Tax Technology, Compliance
KEYWORDS = [
    # Catchall - matches any "US Tax XXX" or "US Taxation XXX" role
    "US Tax",
    "US Taxation",

    # US Tax Technology (1-10)
    "US Tax Technology Analyst",
    "Tax Technology Analyst",
    "US Tax Compliance Analyst",
    "Tax Compliance Technology Analyst",
    "US Tax Software Analyst",
    "Tax Filing Analyst",
    "US Tax E-File Analyst",
    "Tax Form Analyst",
    "US Tax Regulatory Analyst",
    "Tax Content Analyst",

    # E-File / Schema / ATS (11-20)
    "E-File Analyst",
    "E-File Compliance Analyst",
    "E-File Specialist",
    "XML Schema Analyst",
    "Tax Schema Analyst",
    "ATS Analyst",
    "Tax Schema Developer",
    "E-File QA Analyst",
    "Tax Filing Specialist",
    "Electronic Filing Analyst",

    # Tax QA / Testing (21-30)
    "Tax Software QA Analyst",
    "Tax Compliance QA Analyst",
    "Tax Form QA Analyst",
    "Tax Software Test Analyst",
    "Tax Regulatory QA Analyst",
    "Tax QA Engineer",
    "Tax Software Tester",
    "Tax QA Specialist",
    "Tax Form Tester",
    "Tax Compliance Tester",

    # Big 4 / Consulting (31-40)
    "Tax Technology Consultant",
    "US Tax Technology Consultant",
    "Tax Technology Senior",
    "Tax Technology Associate",
    "Tax Compliance Consultant",
    "Tax Digital Analyst",
    "Tax Transformation Analyst",
    "Tax Systems Analyst",
    "Tax Operations Analyst",
    "Tax Process Analyst",

    # AI + Tax + Product (41-50)
    "Tax Automation Analyst",
    "Tax Product Analyst",
    "Tax Innovation Analyst",
    "Tax AI Analyst",
    "Tax Software Product Analyst",
    "Tax Technology Specialist",
    "Tax Implementation Analyst",
    "Tax Data Analyst",
    "Tax Process Automation Analyst",
    "Tax Software Implementation Analyst",
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
