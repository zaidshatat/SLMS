import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    try:
        return psycopg.connect(
            host="localhost",
            port=5432,
            dbname="slms",
            user="postgres",
            password=os.getenv("SLMS_DB_PASSWORD")
        )
    except psycopg.Error as e:
        print(f"Database connection failed: {e}")
        return None

conn = create_connection()

if conn:
    with conn.cursor() as cur:

        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                midterm INTEGER NOT NULL DEFAULT 0 CHECK (midterm BETWEEN 0 AND 30),
                participation INTEGER NOT NULL DEFAULT 0 CHECK (participation BETWEEN 0 AND 30),
                final INTEGER NOT NULL DEFAULT 0 CHECK (final BETWEEN 0 AND 40)
            );
        """)

    conn.commit()
    conn.close()
