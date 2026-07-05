import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# PHASE 1: Positions 1-10 from each section (100% of 8 sections)
# Posts job if ANY keyword found in description
KEYWORDS = [
    # Position 1 from each section
    "ATS", "XML", "Lacerte", "Form 1040", "Software QA", "Java", "AI Tool Development", "Tax Compliance",
    # Position 2
    "E-File", "XSD", "ProSeries", "Form 1041", "Manual Testing", "Delphi XE5", "MCP", "Regulatory Compliance",
    # Position 3
    "EFile", "XML Schema", "GoSystem", "Form 1120", "Regression Testing", "GitHub", "Claude AI", "State Tax Regulations",
    # Position 4
    "ATS Submission", "XSD Schema", "ONESOURCE", "Form 1120S", "Functional Testing", "Jira", "LaserMap MCP", "Federal Tax Regulations",
    # Position 5
    "E-File Approval", "Schema Validation", "UltraTax", "Form 1065", "UAT", "Visual Studio", "TAP AI Assistant", "IRS Compliance",
    # Position 6
    "Print Approval", "XML Tagging", "CCH Axcess", "Form 990", "Test Cases", "LaserMap", "BRMS", "DOR",
    # Position 7
    "E-File Compliance", "Schema Mapping", "ProSystem fx", "Schedule K-1", "Test Scenarios", "2D Barcode", "AI Automation", "Department of Revenue",
    # Position 8
    "Print Compliance", "Schema Development", "Drake", "Individual Tax", "Bug Tracking", "GFS", "Workflow Automation", "Tax Form Development",
    # Position 9
    "State E-File", "Schema Testing", "ATX", "Corporate Tax", "Defect Management", "OSI", "", "Filing Product",
    # Position 10
    "Federal E-File", "Schema Updates", "TaxWise", "Partnership Tax", "Pre-Production Testing", "ODT", "", "Data Conversion",
]

# India cities ONLY - metro + tier-2 cities
LOCATIONS = [
    "Bangalore", "Hyderabad", "Mumbai", "Delhi", "Pune", "Chennai", "Kolkata",
    "Gurgaon", "Noida", "Ahmedabad", "Chandigarh", "Jaipur", "Kochi", "Coimbatore", "Indore", "Lucknow",
]

MAX_JOBS_PER_CYCLE = 15
