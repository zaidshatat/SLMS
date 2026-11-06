# SLMS — Student Learning Management System

SLMS is a command-line Python application for maintaining student names and scores. It stores records in a local comma-separated text file and uses Pandas to produce reports.

## Features

- Display developer information at startup.
- Add students after validating that the ID is an integer and unique and the name contains letters and spaces.
- Modify a student's Midterm, Participation, or Final score. Scores are validated against their limits: 0–30, 0–20, and 0–50, respectively. Multiple attributes can be changed for the same student without entering the ID again.
- Delete a student after displaying the record and receiving confirmation.
- View student and score reports, including averages.
- Keep student records in a text file between program runs.

## Project Structure

```text
SLMS/
├── main.py        # Startup, local data-file initialization, and main menu routing
├── screens.py     # Console interaction, validation, student actions, and Pandas reports
├── students.py    # Student class and text-file update/delete functions
├── students.txt   # Local student records; created at startup if missing and ignored by Git
├── main.ipynb     # Older Google Colab notebook; its menu flow is not current
├── README.md      # Project documentation
└── .gitignore     # Excludes local data and other generated/local files
```

## Requirements

- Python 3.10 or later (the code uses `match`/`case`).
- Pandas. The project was inspected with Pandas 2.2.3 and Python 3.13.0; these are the versions in the current environment, not declared minimum versions.

## Installation and Setup

Run commands from the project directory. Create and activate a virtual environment if desired, then install Pandas:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install pandas
```

On macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install pandas
```

Start the current application with:

```bash
python main.py
```

At startup, `main.py` opens `students.txt` in append mode. This creates an empty file if it does not exist and does not truncate an existing file. Run from the project directory so the application's relative `students.txt` path resolves to the project data file.

## Usage

The program displays developer information, waits for a keypress, and then repeats the main menu until Exit is selected:

| Choice | Action |
| --- | --- |
| A | Add a new student |
| B | Modify a student's scores |
| C | Show reports |
| D | Delete a student |
| E | Exit the program |

### Add a Student

Enter a unique integer student ID and a non-empty name containing letters and spaces. The new record is appended with all three scores set to `None`. The Add flow can be repeated for more students.

### Modify a Student

Enter the student's ID once. If it is invalid or not found, the program offers another ID attempt or a return to the main menu. For a found student, choose Midterm, Participation, or Final and enter a score within its allowed range. Invalid or out-of-range scores are rejected and prompted again. After a successful update, choose whether to edit another attribute for the same student; the same `Student` object is reused. Choosing `D` in the attribute menu returns to the main menu.

### Delete a Student

Enter an integer student ID. If a matching record is found, the program displays the student details and asks for confirmation. Answer `Y` to remove that record while keeping the other records; any other response cancels the deletion. A missing ID is reported without changing the file.

## Data Storage

`students.txt` is a headerless comma-separated text file with one student per line and fields in this order:

```text
Student_ID,Name,Midterm,Participation,Final
```

The line above describes the field order; it is not a literal header row. For example, a record has the form `1234,Student Name,25.0,None,None`.

`None` represents a score that has not been entered. Student creation, lookup, modification, and deletion use text-file handling in `screens.py` and `students.py`. Reports load the file with Pandas, interpret `None` as a missing value, and display missing values as `N/A`. The file is created automatically when the program starts if it is missing.

## Reports

From the Reports menu, the program provides:

- All student records.
- One student's record by ID.
- Student IDs, names, and total scores (the total is available only when all three scores are present).
- IDs and names for all students.
- Average Midterm, Participation, and Final scores.
- Average total score, using students who have all three scores.

Pandas reads and converts report data. Per-score averages use the available numeric values; missing scores are skipped. Averages are shown to two decimal places, or as `N/A` when no value is available.

## Git and Local Data

`students.txt` is intended to remain local to each user's working copy. The `.gitignore` file contains a `students.txt` rule, and the file is currently ignored and untracked in this repository. The ignore rule prevents Git from adding the local data file; it does not remove a copy that was already tracked in another repository history.

## Notebook Status

`main.ipynb` contains an older Colab workflow with a hard-coded Drive path and an outdated menu dispatch. It does not currently include the `main.py` startup initialization or Delete Student flow. Use `python main.py` for the current application behavior.
