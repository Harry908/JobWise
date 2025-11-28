"""Verify database schema matches documentation."""

import asyncio
from sqlalchemy import inspect, text
from app.infrastructure.database.connection import create_engine


async def verify_schema():
    """Verify database schema matches documentation."""
    engine = create_engine()

    async with engine.begin() as conn:
        # Get table names
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())

        print("=" * 80)
        print("DATABASE SCHEMA VERIFICATION")
        print("=" * 80)
        print(f"\nTables found: {len(tables)}")
        print(f"Tables: {', '.join(tables)}\n")

        # Verify users table specifically
        if 'users' in tables:
            print("\n" + "=" * 80)
            print("USERS TABLE SCHEMA")
            print("=" * 80)

            # Get column info
            columns = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_columns('users')
            )

            print(f"\nColumns ({len(columns)}):")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f", DEFAULT={col['default']}" if col['default'] else ""
                print(f"  - {col['name']}: {col['type']} ({nullable}{default})")

            # Get indexes
            indexes = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_indexes('users')
            )

            print(f"\nIndexes ({len(indexes)}):")
            for idx in indexes:
                unique = "UNIQUE" if idx['unique'] else "NON-UNIQUE"
                print(f"  - {idx['name']}: {unique} on {idx['column_names']}")

            # Get primary key
            pk = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_pk_constraint('users')
            )

            print(f"\nPrimary Key: {pk['constrained_columns']}")

            # Get row count
            result = await conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"\nRow count: {count}")

            # Verify against documentation
            print("\n" + "=" * 80)
            print("SCHEMA VERIFICATION AGAINST DOCUMENTATION")
            print("=" * 80)

            expected_columns = {
                'id': 'INTEGER',
                'email': 'VARCHAR',
                'password_hash': 'VARCHAR',
                'full_name': 'VARCHAR',
                'is_active': 'BOOLEAN',
                'is_verified': 'BOOLEAN',
                'created_at': 'DATETIME',
                'updated_at': 'DATETIME'
            }

            actual_columns = {col['name']: str(col['type']) for col in columns}

            print("\nExpected vs Actual columns:")
            all_match = True
            for col_name, col_type in expected_columns.items():
                actual = actual_columns.get(col_name, 'MISSING')
                match = "[OK]" if col_name in actual_columns else "[MISSING]"
                print(f"  {match} {col_name}: {col_type} (actual: {actual})")
                if match == "[MISSING]":
                    all_match = False

            # Check for extra columns
            extra_cols = set(actual_columns.keys()) - set(expected_columns.keys())
            if extra_cols:
                print(f"\nExtra columns not in documentation: {extra_cols}")
                all_match = False

            if all_match:
                print("\n[SUCCESS] All columns match documentation!")
            else:
                print("\n[ERROR] Schema mismatch detected!")

        else:
            print("[ERROR] 'users' table not found!")

        # Print all tables
        print("\n" + "=" * 80)
        print("ALL TABLES IN DATABASE")
        print("=" * 80)

        for table_name in sorted(tables):
            columns = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_columns(table_name)
            )
            print(f"\n{table_name} ({len(columns)} columns):")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(verify_schema())
