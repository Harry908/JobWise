"""Check what profile data exists in the database."""
import sqlite3
import json

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Check users
print("=" * 60)
print("USERS:")
print("=" * 60)
cursor.execute("SELECT id, email, full_name FROM users")
users = cursor.fetchall()
for user in users:
    print(f"ID: {user[0]}, Email: {user[1]}, Name: {user[2]}")

print("\n" + "=" * 60)
print("PROFILES:")
print("=" * 60)
cursor.execute("""
    SELECT id, user_id, personal_info, professional_summary 
    FROM master_profiles
""")
profiles = cursor.fetchall()
for profile in profiles:
    print(f"\nProfile ID: {profile[0]}")
    print(f"User ID: {profile[1]}")
    print(f"Personal Info: {profile[2]}")
    print(f"Summary: {profile[3]}")

print("\n" + "=" * 60)
print("EXPERIENCES:")
print("=" * 60)
cursor.execute("SELECT * FROM experiences")
experiences = cursor.fetchall()
for exp in experiences:
    print(f"ID: {exp[0]}, Profile: {exp[1]}, Company: {exp[2]}, Title: {exp[3]}")

print("\n" + "=" * 60)
print("PROJECTS:")
print("=" * 60)
cursor.execute("SELECT * FROM projects")
projects = cursor.fetchall()
for proj in projects:
    print(f"ID: {proj[0]}, Profile: {proj[1]}, Name: {proj[2]}, Description: {proj[3]}")

conn.close()
