import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Read env variables
DATABASE_URL = os.getenv("DATABASE_URL")

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
DB_NAME = os.getenv("DB_NAME", "ims")

# Fallback if DATABASE_URL not provided
if not DATABASE_URL:
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

# Retry DB connection
while True:
    try:
        print(f"🔌 Connecting to DB: {DATABASE_URL}")
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        conn = engine.connect()
        conn.close()
        print("✅ API connected to DB")
        break
    except Exception as e:
        print(f"⏳ API waiting for DB... ({e})")
        time.sleep(2)

# Session
SessionLocal = sessionmaker(bind=engine)