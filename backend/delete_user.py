"""Utility to delete a user and related data from the SQLite DB.

This script connects to the configured database and removes the user with the
specified id and related rows from tables that reference users. It runs in a
transaction and prints counts of deleted rows.

Usage:
    cd backend
    python delete_user.py --user-id 1 [--dry-run]
"""

import argparse
import asyncio
from sqlalchemy import text
from app.infrastructure.database.connection import create_engine


TABLES_ORDERED_FOR_DELETE = [
    "generations",
    "job_content_rankings",
    "writing_styles",
    "sample_documents",
    "jobs",
    # Delete sub-resources attached to master_profiles
    "experiences",
    "education",
    "projects",
    "master_profiles",
    "users",
]

# Tables that have a direct `user_id` column
TABLES_WITH_USER_ID = {
    "generations",
    "job_content_rankings",
    "writing_styles",
    "sample_documents",
    "jobs",
}


async def delete_user_and_related(user_id: int, dry_run: bool = False) -> None:
    engine = create_engine()

    async with engine.begin() as conn:
        # Ensure SQLite enforces FK constraints
        await conn.execute(text("PRAGMA foreign_keys = ON"))

        # Print counts first. Different tables use either `user_id` or `profile_id`.
        counts = {}
        # There can be 0..n master_profiles for a user.

        for table in TABLES_ORDERED_FOR_DELETE:
            if table in TABLES_WITH_USER_ID:
                result = await conn.execute(
                    text(f"SELECT COUNT(1) AS c FROM {table} WHERE user_id = :uid"), {"uid": user_id}
                )
                row = result.first()
                counts[table] = int(row[0]) if row else 0
            elif table in {"experiences", "education", "projects"}:
                result = await conn.execute(
                    text(f"SELECT COUNT(1) AS c FROM {table} WHERE profile_id IN (SELECT id FROM master_profiles WHERE user_id = :uid)"),
                    {"uid": user_id},
                )
                row = result.first()
                counts[table] = int(row[0]) if row else 0
            elif table == "master_profiles":
                result = await conn.execute(text("SELECT COUNT(1) AS c FROM master_profiles WHERE user_id = :uid"), {"uid": user_id})
                row = result.first()
                counts[table] = int(row[0]) if row else 0
            elif table == "users":
                result = await conn.execute(text("SELECT COUNT(1) AS c FROM users WHERE id = :uid"), {"uid": user_id})
                row = result.first()
                counts[table] = int(row[0]) if row else 0

        print("Counts before deletion:")
        for t, c in counts.items():
            print(f"  {t}: {c}")

        if dry_run:
            print("Dry run enabled; no deletions executed.")
            return

        # Perform deletes in order; this keeps referential integrity safe.
        for table in TABLES_ORDERED_FOR_DELETE:
            print(f"Deleting rows from {table}...")
            if table in TABLES_WITH_USER_ID:
                await conn.execute(text(f"DELETE FROM {table} WHERE user_id = :uid"), {"uid": user_id})
            elif table in {"experiences", "education", "projects"}:
                await conn.execute(
                    text(f"DELETE FROM {table} WHERE profile_id IN (SELECT id FROM master_profiles WHERE user_id = :uid)"),
                    {"uid": user_id},
                )
            elif table == "master_profiles":
                await conn.execute(text("DELETE FROM master_profiles WHERE user_id = :uid"), {"uid": user_id})
            elif table == "users":
                await conn.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user_id})

        print(f"Deleted user and related rows for user_id={user_id}")

    await engine.dispose()


def parse_args():
    p = argparse.ArgumentParser(description="Delete a user and their related DB rows")
    p.add_argument("--user-id", type=int, default=1, help="User id to remove")
    p.add_argument("--dry-run", action="store_true", help="Show what would be removed")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(delete_user_and_related(args.user_id, args.dry_run))
