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