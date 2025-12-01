"""Check for mock jobs in database."""
import sqlite3

conn = sqlite3.connect('jobwise.db')
cursor = conn.cursor()

# Count mock jobs
cursor.execute("SELECT COUNT(*) FROM jobs WHERE source = 'mock'")
count = cursor.fetchone()[0]
print(f"\n{'='*60}")
print(f"Mock jobs in database: {count}")
print(f"{'='*60}\n")

if count > 0:
    # Show sample mock jobs
    cursor.execute("SELECT id, title, company, source FROM jobs WHERE source = 'mock' LIMIT 10")
    rows = cursor.fetchall()
    print("Sample mock jobs:")
    for row in rows:
        print(f"  - {row[1]} at {row[2]} (source: {row[3]})")
    print()

# Show source distribution
cursor.execute("SELECT source, COUNT(*) as count FROM jobs GROUP BY source ORDER BY count DESC")
rows = cursor.fetchall()
print("\nJob source distribution:")
for row in rows:
    print(f"  {row[0]}: {row[1]} jobs")

conn.close()
