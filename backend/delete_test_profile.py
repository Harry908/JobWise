"""Delete all profiles from the database."""
import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Delete all related records
cursor.execute("DELETE FROM projects")
cursor.execute("DELETE FROM education")
cursor.execute("DELETE FROM experiences")
cursor.execute("DELETE FROM master_profiles")

conn.commit()

# Verify deletion
cursor.execute("SELECT COUNT(*) FROM master_profiles")
count = cursor.fetchone()[0]
print(f"Profiles remaining: {count}")

conn.close()
print("All profiles deleted successfully!")
