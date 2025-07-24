"""
Drop All Tables Except Users Script

This script connects to the Awade database and drops all tables except the 'users' table. Useful for resetting the database while preserving user data.

Usage:
    python scripts/drop_all_except_users.py

Author: Tolulope Babajide
"""
from sqlalchemy import create_engine, MetaData, text
from apps.backend.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
meta = MetaData()
meta.reflect(bind=engine)

with engine.connect() as conn:
    for table in list(meta.tables):
        if table != 'users':
            print(f"Dropping table: {table}")
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
    print("All tables except 'users' have been dropped.") 