"""Check database tables."""
import sqlite3

conn = sqlite3.connect('jobwise.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("\nCurrent database tables:")
for table in tables:
    print(f"  ✓ {table[0]}")

# Check for preference tables
preference_tables = [
    'example_resumes',
    'writing_style_configs',
    'layout_configs',
    'user_generation_profiles',
    'consistency_scores',
    'job_type_overrides'
]

print("\nPreference-related tables status:")
for table_name in preference_tables:
    exists = any(t[0] == table_name for t in tables)
    status = "✅ EXISTS" if exists else "❌ MISSING"
    print(f"  {status}: {table_name}")

conn.close()
