import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1004378631673")  # US Tax Software Testing Jobs channel

# ONE mega search query with all 100 keywords (LinkedIn searches for ANY match)
# Much faster: 1 search per location instead of 100 searches
KEYWORDS = [
    "ATS E-File EFile ATS Submission E-File Approval Print Approval E-File Compliance Print Compliance State E-File Federal E-File ATS Test Client E-File Authorization State Authority Approval DOR Approval MeF Modernized e-File E-File Diagnostics E-File Schema E-File Module Electronic Filing XML XSD XML Schema XSD Schema Schema Validation XML Tagging Schema Mapping Schema Development Schema Testing Schema Updates XMLSpy Altova XMLSpy XML Output Validation Master Schema Schema Versions Lacerte ProSeries GoSystem ONESOURCE UltraTax CCH Axcess ProSystem fx Drake ATX TaxWise TaxAct TaxSlayer ProConnect CrossLink GoSystem Tax RS Form 1040 Form 1041 Form 1120 Form 1120S Form 1065 Form 990 Schedule K-1 Individual Tax Corporate Tax Partnership Tax Software QA Manual Testing Regression Testing Functional Testing UAT Test Cases Test Scenarios Bug Tracking Defect Management Pre-Production Testing Java Delphi XE5 GitHub Jira Visual Studio LaserMap 2D Barcode GFS OSI ODT AI Tool Development MCP Claude AI LaserMap MCP TAP AI Assistant BRMS AI Automation Workflow Automation Tax Compliance Regulatory Compliance State Tax Regulations Federal Tax Regulations IRS Compliance DOR Department of Revenue Tax Form Development Filing Product Data Conversion Tax Law Changes Government Liaison"
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
