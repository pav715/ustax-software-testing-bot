import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# Search keywords organized by POSITION (1-20) across all 8 sections
# Bot checks position-wise: if description has keywords from same position → POST
KEYWORDS = [
    # POSITION 1 from each section
    "ATS", "XML", "Lacerte", "Form 1040", "Software QA", "Java", "AI Tool Development", "Tax Compliance",
    # POSITION 2
    "E-File", "XSD", "ProSeries", "Form 1041", "Manual Testing", "Delphi XE5", "MCP", "Regulatory Compliance",
    # POSITION 3
    "EFile", "XML Schema", "GoSystem", "Form 1120", "Regression Testing", "GitHub", "Claude AI", "State Tax Regulations",
    # POSITION 4
    "ATS Submission", "XSD Schema", "ONESOURCE", "Form 1120S", "Functional Testing", "Jira", "LaserMap MCP", "Federal Tax Regulations",
    # POSITION 5
    "E-File Approval", "Schema Validation", "UltraTax", "Form 1065", "UAT", "Visual Studio", "TAP AI Assistant", "IRS Compliance",
    # POSITION 6
    "Print Approval", "XML Tagging", "CCH Axcess", "Form 990", "Test Cases", "LaserMap", "BRMS", "DOR",
    # POSITION 7
    "E-File Compliance", "Schema Mapping", "ProSystem fx", "Schedule K-1", "Test Scenarios", "2D Barcode", "AI Automation", "Department of Revenue",
    # POSITION 8
    "Print Compliance", "Schema Development", "Drake", "Individual Tax", "Bug Tracking", "GFS", "Workflow Automation", "Tax Form Development",
    # POSITION 9
    "State E-File", "Schema Testing", "ATX", "Corporate Tax", "Defect Management", "OSI", "", "Filing Product",
    # POSITION 10
    "Federal E-File", "Schema Updates", "TaxWise", "Partnership Tax", "Pre-Production Testing", "ODT", "", "Data Conversion",
    # POSITION 11
    "ATS Test Client", "XMLSpy", "", "", "", "", "", "Tax Law Changes",
    # POSITION 12
    "E-File Authorization", "Altova XMLSpy", "", "", "", "", "", "Government Liaison",
    # POSITION 13
    "State Authority Approval", "XML Output Validation", "", "", "", "", "", "",
    # POSITION 14
    "DOR Approval", "Master Schema", "", "", "", "", "", "",
    # POSITION 15
    "MeF", "Schema Versions", "", "", "", "", "", "",
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
