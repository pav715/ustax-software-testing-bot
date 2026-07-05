import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# TAX SOFTWARE TESTING: Positions 1-20 from each section - any 1 keyword = POST
KEYWORDS = [
    # E-File / ATS (1–20) - ALL 20
    "ATS", "E-File", "EFile", "ATS Submission", "E-File Approval",
    "Print Approval", "E-File Compliance", "Print Compliance", "State E-File", "Federal E-File",
    "ATS Test Client", "E-File Authorization", "State Authority Approval", "DOR Approval", "MeF",
    "Modernized e-File", "E-File Diagnostics", "E-File Schema", "E-File Module", "Electronic Filing",
    # XML / Schema (21–35) - Top 15 only
    "XML", "XSD", "XML Schema", "XSD Schema", "Schema Validation",
    "XML Tagging", "Schema Mapping", "Schema Development", "Schema Testing", "Schema Updates",
    "XMLSpy", "Altova XMLSpy", "XML Output Validation", "Master Schema", "Schema Versions",
    # Tax Software (36–50) - Top 15 only
    "Lacerte", "ProSeries", "GoSystem", "ONESOURCE", "UltraTax",
    "CCH Axcess", "ProSystem fx", "Drake", "ATX", "TaxWise",
    "TaxAct", "TaxSlayer", "ProConnect", "CrossLink", "GoSystem Tax RS",
    # Tax Forms (51–60) - All 10
    "Form 1040", "Form 1041", "Form 1120", "Form 1120S", "Form 1065",
    "Form 990", "Schedule K-1", "Individual Tax", "Corporate Tax", "Partnership Tax",
    # QA / Testing (61–70) - All 10
    "Software QA", "Manual Testing", "Regression Testing", "Functional Testing", "UAT",
    "Test Cases", "Test Scenarios", "Bug Tracking", "Defect Management", "Pre-Production Testing",
    # Tools / Tech (71–80) - All 10
    "Java", "Delphi XE5", "GitHub", "Jira", "Visual Studio",
    "LaserMap", "2D Barcode", "GFS", "OSI", "ODT",
    # AI / Automation (81–88) - All 8
    "AI Tool Development", "MCP", "Claude AI", "LaserMap MCP", "TAP AI Assistant",
    "BRMS", "AI Automation", "Workflow Automation",
    # Compliance / Regulatory (89–100) - All 12
    "Tax Compliance", "Regulatory Compliance", "State Tax Regulations", "Federal Tax Regulations", "IRS Compliance",
    "DOR", "Department of Revenue", "Tax Form Development", "Filing Product", "Data Conversion",
    "Tax Law Changes", "Government Liaison",
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
