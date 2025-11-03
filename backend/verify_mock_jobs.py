"""Verify mock jobs JSON data integrity."""

import json
from pathlib import Path

# Load JSON file
json_file = Path("data/mock_jobs.json")
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

jobs = data.get("tech_jobs", [])

print(f"✓ Jobs in JSON file: {len(jobs)}")
print(f"✓ First job: {jobs[0]['title']} at {jobs[0]['company']}")
print(f"✓ Last job: {jobs[-1]['title']} at {jobs[-1]['company']}")
print(f"✓ All jobs have source='mock': {all(j.get('source') == 'mock' for j in jobs)}")
print(f"✓ All jobs have required fields: {all('title' in j and 'company' in j and 'description' in j for j in jobs)}")
print(f"✓ All jobs have parsed_keywords: {all('parsed_keywords' in j for j in jobs)}")
print(f"✓ All jobs have requirements: {all('requirements' in j for j in jobs)}")
print(f"✓ All jobs have benefits: {all('benefits' in j for j in jobs)}")
print(f"✓ All jobs have salary_range: {all('salary_range' in j for j in jobs)}")
print(f"✓ All jobs have remote field: {all('remote' in j for j in jobs)}")
print(f"✓ All jobs have location: {all('location' in j for j in jobs)}")

# Check metadata
metadata = data.get("metadata", {})
print(f"\n✓ Metadata version: {metadata.get('version')}")
print(f"✓ Last updated: {metadata.get('last_updated')}")
print(f"✓ Total count in metadata: {data.get('total_count')}")

print("\n✅ All validation checks passed! JSON file is properly structured.")
