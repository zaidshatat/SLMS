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

        # Repair existing rows before enforcing the same rule on the table.
        cur.execute("""
            UPDATE students
            SET midterm = COALESCE(midterm, 0),
                participation = COALESCE(participation, 0),
                final = COALESCE(final, 0)
            WHERE midterm IS NULL OR participation IS NULL OR final IS NULL;
        """)
        cur.execute("""
            ALTER TABLE students
                ALTER COLUMN midterm SET DEFAULT 0,
                ALTER COLUMN midterm SET NOT NULL,
                ALTER COLUMN participation SET DEFAULT 0,
                ALTER COLUMN participation SET NOT NULL,
                ALTER COLUMN final SET DEFAULT 0,
                ALTER COLUMN final SET NOT NULL;
        """)
    conn.commit()
    conn.close()
