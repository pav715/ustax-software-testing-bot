#!/usr/bin/env python3
"""Quick test: Check if scraper can find US Tax jobs"""
import sys
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add current dir to path
sys.path.insert(0, os.path.dirname(__file__))

import config
from scraper import fetch_all_jobs

print("=" * 60)
print("US TAX JOBS BOT - SCRAPER TEST")
print("=" * 60)
print(f"BOT_TOKEN: {'SET' if config.BOT_TOKEN else 'NOT SET'}")
print(f"CHAT_ID: {config.CHAT_ID}")
print(f"Keywords: {len(config.KEYWORDS)} - {config.KEYWORDS[:3]}...")
print(f"Locations: {len(config.LOCATIONS)} - {config.LOCATIONS}")
print("=" * 60)

try:
    print("\n🔍 Fetching jobs...")
    jobs = fetch_all_jobs(since_seconds=86400)  # Last 24 hours

    print(f"\n✅ Found {len(jobs)} total jobs")

    if jobs:
        print("\n📋 First 5 jobs:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Source: {job['source']}")
            print(f"   URL: {job['url'][:60]}...")
    else:
        print("\n❌ NO JOBS FOUND! Check:")
        print("   1. LinkedIn might be blocking requests")
        print("   2. Keywords might not match any jobs")
        print("   3. Network connectivity issue")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
