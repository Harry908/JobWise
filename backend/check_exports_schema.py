"""
Check the actual database schema for exports table.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import sqlite3


def check_exports_schema():
    """Check the exports table schema."""
    
    db_path = Path(__file__).parent / "jobwise.db"
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get table schema
        cursor.execute("PRAGMA table_info(exports)")
        columns = cursor.fetchall()
        
        print("Exports table columns:")
        print("-" * 60)
        for col in columns:
            print(f"{col[0]:3d} | {col[1]:20s} | {col[2]:10s} | NotNull:{col[3]} | Default:{col[4]}")
        
        print("\n" + "=" * 60)
        
        # Get count
        cursor.execute("SELECT COUNT(*) FROM exports")
        count = cursor.fetchone()[0]
        print(f"Total exports: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM exports LIMIT 1")
            row = cursor.fetchone()
            cursor.execute("PRAGMA table_info(exports)")
            columns = cursor.fetchall()
            print("\nSample row:")
            for i, col in enumerate(columns):
                print(f"  {col[1]}: {row[i]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()


if __name__ == "__main__":
    check_exports_schema()
