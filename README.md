# SLMS — Student Learning Management System

SLMS is a command-line student management application. The active application stores student records in PostgreSQL and uses `psycopg` with parameterized SQL. Rich formats the reports in the terminal.

## Features

- **Add Student:** validates first and last names separately, optionally collects marks, and lets PostgreSQL generate the student ID. Skipped marks are stored as `0`.
- **Modify Student:** finds a student by ID and updates Midterm, Participation, Final, or both name fields. Invalid marks are rejected and prompted again.
- **Delete Student:** displays the selected record and requires confirmation before deleting it.
- **Show Reports:** displays all students with totals and class averages, or a report for one student. Missing marks display as `N/A`; totals require all three marks.

Names are currently validated as one non-empty alphabetic word each. IDs are positive integers. Mark limits are Midterm `0–30`, Participation `0–30`, and Final `0–40`.

## Project Structure

| File | Responsibility |
| --- | --- |
| `main.py` | Starts the application and routes the main menu. |
| `screens.py` | Console prompts, validation, student workflows, SQL operations, and Rich reports. |
| `students.py` | `Student` data object with ID, first name, last name, and marks. |
| `database.py` | `create_connection()` and `CREATE TABLE IF NOT EXISTS` initialization. |
| `pyproject.toml` | Python requirement and declared project dependencies for uv. |
| `uv.lock` | Locked dependency versions. |
| `main.ipynb`, `test.ipynb` | Notebooks; the supported application entry point is `main.py`. |
| `README.md`, `README_AR.md` | English and Arabic project documentation. |

## Database Schema

The database connection settings in `database.py` target PostgreSQL on `localhost:5432`, database `slms`, user `postgres`. On a successful import, `database.py` creates the table if it does not already exist:

```sql
CREATE TABLE IF NOT EXISTS students (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    midterm INTEGER NOT NULL DEFAULT 0 CHECK (midterm BETWEEN 0 AND 30),
    participation INTEGER NOT NULL DEFAULT 0 CHECK (participation BETWEEN 0 AND 30),
    final INTEGER NOT NULL DEFAULT 0 CHECK (final BETWEEN 0 AND 40)
);
```

The three mark columns are required, default to `0`, and must stay within their allowed ranges. On startup, `database.py` converts any existing `NULL` marks to `0` and then enforces `NOT NULL` on all three columns.

## Setup

Requirements: Python `>=3.13`, PostgreSQL, and [uv](https://docs.astral.sh/uv/).

1. Create the database once using a PostgreSQL administrator account:

   ```sql
   CREATE DATABASE slms;
   ```

   `database.py` initializes the `students` table when the application connects. The PostgreSQL role must have permission to connect to `slms` and create the table.

2. Create a `.env` file in the project directory with the password for the configured `postgres` role:

   ```dotenv
   SLMS_DB_PASSWORD=your_postgres_password
   ```

   Keep the password private. Host, port, database name, and username are currently set directly in `database.py`.

3. Install the locked dependencies:

   ```bash
   uv sync
   ```

4. Run the application:

   ```bash
   uv run python main.py
   ```

## Menu

| Choice | Action |
| --- | --- |
| A | Add a student |
| B | Modify a student |
| C | Show reports (`A` all students, `B` individual student, `C` return) |
| D | Delete a student |
| E | Exit |

Database operations use `create_connection()` and ordinary parameterized `psycopg` SQL. The application does not use an ORM for student records.

## Notes

- The main application is `main.py`; notebook files are not the application entry point.
- `pandas` and `sqlalchemy` are declared dependencies in `pyproject.toml`, but the current screen workflows use Rich and `psycopg`; they do not use Pandas or SQLAlchemy.
