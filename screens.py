from students import Student
import psycopg
from database import create_connection
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Store the developer details displayed at startup.
info = {
    "name": "Zaid Shatat",
    "email": "zaidshatat06@gmail.com",
    "github": "https://github.com/zaidshatat"
    }
dev_info = f"Developer Information:\n\
Name: {info['name']}\n\
Email: {info['email']}\n\
GitHub: {info['github']}"
def show_developer_info():
    print(dev_info)


def display_main_menu():
    # Present the available top-level actions.
    print(f"Please select an option from the menu below:\n")
    print("A. Add a new student (press A)")
    print("B. Modify a student (press B)")
    print("C. Show reports (press C)")
    print("D. Delete a student (press D)")
    print("E. Exit the program (press E)")


def get_bin_choice(message):
    while True:
        choice = input(f"\n{message}").strip().upper()
        if choice not in ['Y', 'YES', 'N', 'NO']:
            print("Invalid choice. Please try again.")
            continue
        return choice

def get_user_choice():
    # Keep asking until the user enters a valid menu letter.
    while True:
        choice = input("\nEnter your choice: ").strip().upper()
        if choice not in ['A', 'B', 'C', 'D', 'E']:
            # if the user enters an invaled choice
            print("\nInvalid choice. Please try again.")
            continue
        return choice

def _name_check(message):
    # Require a non-empty name containing only letters and spaces.
    while True: # check if the student name is valid
        name = input(f"{message}").strip()
        if (len(name.split()) != 1) or (not name) or not name.isalpha():
            print("Name cannot be empty or digits or more than one syllable. Please try again.")
            continue
        return name

def add_student():
    while True:
        # Collect and validate the student's names with the existing helper.
        first_name = _name_check("Enter first name: ")
        last_name = _name_check("Enter last name: ")

        # Ask whether marks should be entered; skipped marks default to zero.
        message = "Do you want to enter student marks? (Y/N): "
        enter_marks = get_bin_choice(message)
        if enter_marks in ('Y', 'YES'):
            marks = []
            # Validate each score separately so an error only repeats that mark.
            for label, maximum in (("Midterm", 30), ("Participation", 30), ("Final", 40)):
                while True:
                    raw_mark = input(f"Enter {label} (0-{maximum}) [Press enter to skip]: ").strip()
                    if not raw_mark:
                        marks.append(0)
                        break
                    try:
                        mark = int(raw_mark)
                        if mark < 0 or mark > maximum:
                            raise ValueError
                    except ValueError:
                        print(f"Invalid {label.lower()} score. Enter an integer between 0 and {maximum}.")
                        continue
                    marks.append(mark)
                    break
            midterm, participation, final = marks
        else:
            midterm = participation = final = 0

        # Open a fresh database connection for this student's insert.
        conn = create_connection()
        if conn is None:
            print("Student could not be added because the database connection failed.")
            return

        try:
            with conn.cursor() as cur:
                # PostgreSQL generates the ID; RETURNING gives it back after insertion.
                cur.execute(
                    """INSERT INTO students (first_name, last_name, midterm, participation, final)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                    (first_name, last_name, midterm, participation, final),
                )
                student_id = cur.fetchone()[0]
            # Save the successful insert permanently.
            conn.commit()
        except psycopg.Error as e:
            # Undo any partial transaction and report the database failure.
            conn.rollback()
            print(f"Student could not be added because of a database error: {e}")
            return
        finally:
            # Always release the connection, including when the insert fails.
            conn.close()

        # Confirm the saved student, then optionally repeat the process.
        print(f"Student has been added successfully. ID: {student_id}, Name: {first_name} {last_name}.")

        message = "Would you like to add another student? (Y/N): "
        another_add = get_bin_choice(message)
        if another_add in ('N', 'NO'):
            break



# Collect the attribute choice for the current student's edit loop.
def get_modify_choice():
    # Validate the attribute choice before returning it to the edit flow.
    while True:
        print("\nWhat would you like to modify?")
        print("A. Midterm")
        print("B. Participation")
        print("C. Final")
        print("D. Name")
        print("E. Exit to main menu")
        
        choice = input("Enter your choice: ").strip().upper()

        if choice not in ['A', 'B', 'C', 'D', 'E']:
            print("Invalid choice. Please try again.")
            continue
        return choice

def _get_student_by_id(student_id):
    """Retrieve one student's database record by ID."""
    conn = create_connection()
    if conn is None:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, first_name, last_name, midterm, participation, final
                   FROM students WHERE id = %s""",
                (student_id,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return Student(*row)
    except psycopg.Error as e:
        print(f"Could not retrieve student information: {e}")
        return False
    finally:
        conn.close()

def _student_id_from_input(raw_student_id):
    raw_student_id = raw_student_id.strip()
    if not raw_student_id or not raw_student_id.isascii() or not raw_student_id.isdecimal():
        return None
    try:
        student_id = int(raw_student_id)
    except ValueError:
        return None
    return student_id if student_id > 0 else None


def modify_student_info():
    # Find the student once and reuse the database record for each change.
    while True:
        raw_student_id = input("Enter student ID to modify: ").strip()
        student_id = _student_id_from_input(raw_student_id)
        if student_id is None:
            print("Invalid input. Please enter a valid student ID.")
            message = "Would you like to enter another Student ID? (Y/N): "
            retry = get_bin_choice(message)
            if retry == 'N' or retry == 'NO':
                print("Returning to main menu.")
                return
            continue

        student = _get_student_by_id(student_id)
        if student is False:
            print("Returning to main menu because the student could not be loaded.")
            return
        if student is None:
            print("Student ID not found.")
            message = "Would you like to enter another Student ID? (Y/N): "
            retry = get_bin_choice(message)
            if retry in ('Y', 'YES'):
                continue
            print("Returning to main menu.")
            return
        break

    while True:
        # Show all current values before each requested change.
        print(
            f"\nCurrent student: ID: {student.student_id}, "
            f"Name: {student.first_name} {student.last_name}, "
            f"Midterm: {student.midterm}, Participation: {student.participation}, Final: {student.final}"
        )
        choice = get_modify_choice()
        if choice == 'E':
            print("Returning to main menu.")
            return

        if choice == 'D':
            first_name = _name_check("Enter new first name: ")
            last_name = _name_check("Enter new last name: ")
            query = "UPDATE students SET first_name = %s, last_name = %s WHERE id = %s"
            values = (first_name, last_name, student.student_id)
            description = "Name"
        else:
            attributes = {
                'A': ('midterm', 'Midterm', 30, "UPDATE students SET midterm = %s WHERE id = %s"),
                'B': ('participation', 'Participation', 30, "UPDATE students SET participation = %s WHERE id = %s"),
                'C': ('final', 'Final', 40, "UPDATE students SET final = %s WHERE id = %s"),
            }
            attribute, label, maximum, query = attributes[choice]
            while True:
                raw_value = input(f"Enter new {label} score (0-{maximum}): ").strip()
                try:
                    value = int(raw_value)
                    if value < 0 or value > maximum:
                        raise ValueError
                    break
                except ValueError:
                    print(f"Invalid score. Enter an integer between 0 and {maximum}.")

            # Use the fixed query selected by the menu mapping; input remains parameterized.
            values = (value, student.student_id)
            description = label

        conn = create_connection()
        if conn is None:
            print("The update could not be completed because the database connection failed.")
            return
        try:
            with conn.cursor() as cur:
                cur.execute(query, values)
                if cur.rowcount != 1:
                    conn.rollback()
                    print("The student record was not updated because it could not be found.")
                    return
            conn.commit()
        except psycopg.Error as e:
            conn.rollback()
            print(f"Could not update the student: {e}")
            return
        finally:
            conn.close()

        # Keep the displayed Student object in sync with the committed database values.
        if choice == 'D':
            student.first_name = first_name
            student.last_name = last_name
        else:
            setattr(student, attribute, value)
        print(f"{description} updated successfully.")
        print(
            f"Updated student: ID: {student.student_id}, "
            f"Name: {student.first_name} {student.last_name}, "
            f"Midterm: {student.midterm}, Participation: {student.participation}, Final: {student.final}"
        )

        message = "Would you like to modify another attribute for this student? (Y/N): "
        another = get_bin_choice(message)
        if another in ('N', 'NO'):
            print("Returning to main menu.")
            return


def delete_student_info():
    # Retrieve and confirm the database record before deleting it.
    while True:
        raw_student_id = input("Enter student ID to delete: ").strip()
        student_id = _student_id_from_input(raw_student_id)
        if student_id is None:
            print("Invalid input. Please enter a valid student ID.")
            if get_bin_choice("Would you like to try another ID? (Y/N): ") in ('N', 'NO'):
                return
            continue

        student = _get_student_by_id(student_id)
        if student is False:
            print("Could not load the student because of a database error.")
            return
        if student is None:
            print("Student ID not found.")
            if get_bin_choice("Would you like to try another ID? (Y/N): ") in ('Y', 'YES'):
                continue
            return
        break

    print(
        f"Student: ID: {student.student_id}, Name: {student.first_name} {student.last_name}, "
        f"Midterm: {student.midterm}, Participation: {student.participation}, Final: {student.final}"
    )
    if get_bin_choice("Are you sure you want to delete this student? (Y/N): ") in ('N', 'NO'):
        print("Deletion cancelled.")
        return

    conn = create_connection()
    if conn is None:
        print("The student could not be deleted because the database connection failed.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE id = %s", (student.student_id,))
            if cur.rowcount != 1:
                conn.rollback()
                print("The student record was not deleted because it could not be found.")
                return
        conn.commit()
        print("Student deleted successfully.")
    except psycopg.Error as e:
        conn.rollback()
        print(f"Could not delete the student: {e}")
    finally:
        conn.close()


def _get_report_choice():
    """Return one of the complete report menu choices."""
    while True:
        console.print("\n[bold cyan]Student Reports[/bold cyan]")
        console.print("A. All Students       B. Individual Student       C. Total Scores")
        console.print("D. Names & IDs         E. Average Midterm           F. Average Participation")
        console.print("G. Average Final       H. Average Total             I. Return to Main Menu")
        console.print("J. Assessment Reports K. Score Sorting & Filters")
        choice = input("Enter your choice: ").strip().upper()
        if choice in tuple("ABCDEFGHIJK"):
            return choice
        console.print("[yellow]Invalid choice. Select A through K.[/yellow]")


def _get_students_for_report():
    """Load all report rows from PostgreSQL, or return False on failure."""
    conn = create_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, first_name, last_name, midterm, participation, final
                   FROM students ORDER BY id"""
            )
            return cur.fetchall()
    except psycopg.Error as e:
        console.print(f"[bold red]Could not load student reports:[/bold red] {e}")
        return False
    finally:
        conn.close()


def _format_mark(value):
    return "N/A" if value is None else str(value)


def _student_total(marks):
    """Return a total only when all three marks are present."""
    if any(mark is None for mark in marks):
        return None
    return sum(marks)


def _average(values):
    """Average present values, matching PostgreSQL AVG's NULL handling."""
    present_values = [value for value in values if value is not None]
    return sum(present_values) / len(present_values) if present_values else None


def _show_student_table(rows):
    """Display the student list and summary statistics from database rows."""
    if not rows:
        console.print(Panel("No student records found.", title="Student Report", border_style="yellow"))
        return

    table = Table(
        title="Student Gradebook",
        box=box.SIMPLE_HEAVY,
        header_style="bold cyan",
        border_style="bright_blue",
        row_styles=["", "dim"],
        expand=True,
        pad_edge=False,
    )
    table.add_column("ID", justify="right", style="bold white", no_wrap=True)
    table.add_column("First Name", style="white", overflow="ellipsis", max_width=20)
    table.add_column("Last Name", style="white", overflow="ellipsis", max_width=20)
    table.add_column("Midterm\n(30)", justify="right")
    table.add_column("Participation\n(30)", justify="right")
    table.add_column("Final\n(40)", justify="right")
    table.add_column("Total\n(100)", justify="right", style="bold green")

    for student_id, first_name, last_name, midterm, participation, final in rows:
        total = _student_total((midterm, participation, final))
        total_style = "green" if total is not None and total >= 85 else "yellow" if total is not None and total >= 60 else "red"
        table.add_row(
            str(student_id), first_name, last_name,
            _format_mark(midterm), _format_mark(participation), _format_mark(final),
            f"[{total_style}]{_format_mark(total)}[/]",
        )

    count = len(rows)
    averages = [_average([row[index] for row in rows]) for index in (3, 4, 5)]
    average_total = _average([
        _student_total((row[3], row[4], row[5])) for row in rows
    ])
    stats = Table.grid(expand=True, padding=(0, 2))
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_row(
        f"[bold white]{count}[/]\n[dim]Students[/]",
        f"[bold cyan]{_format_mark(averages[0]) if averages[0] is None else f'{averages[0]:.2f}'}[/]\n[dim]Midterm / 30[/]",
        f"[bold cyan]{_format_mark(averages[1]) if averages[1] is None else f'{averages[1]:.2f}'}[/]\n[dim]Participation / 30[/]",
        f"[bold cyan]{_format_mark(averages[2]) if averages[2] is None else f'{averages[2]:.2f}'}[/]\n[dim]Final / 40[/]",
        f"[bold green]{_format_mark(average_total) if average_total is None else f'{average_total:.2f}'}[/]\n[dim]Average total / 100[/]",
    )
    console.print(Panel(stats, title="Class Summary", border_style="bold cyan", box=box.ROUNDED, padding=(1, 0)))
    console.print(table)


def _show_score_report(rows, title, score_column, maximum, order=None):
    """Render a score-focused table from the shared PostgreSQL result set."""
    if not rows:
        console.print(Panel("No students match this report.", title=title, border_style="yellow"))
        return
    score_index = {"midterm": 3, "participation": 4, "final": 5, "total": None}[score_column]
    report_rows = []
    for row in rows:
        score = _student_total(row[3:6]) if score_column == "total" else row[score_index]
        report_rows.append((row[0], row[1], row[2], score))
    if order:
        scored_rows = [item for item in report_rows if item[3] is not None]
        missing_rows = [item for item in report_rows if item[3] is None]
        scored_rows.sort(key=lambda item: item[3], reverse=(order == "descending"))
        report_rows = scored_rows + missing_rows

    table = Table(title=title, box=box.SIMPLE_HEAVY, header_style="bold cyan", border_style="bright_blue", expand=True)
    table.add_column("Student ID", justify="right", no_wrap=True)
    table.add_column("First Name", overflow="ellipsis", max_width=22)
    table.add_column("Last Name", overflow="ellipsis", max_width=22)
    table.add_column(f"{score_column.title()} / {maximum}", justify="right", style="bold green")
    for student_id, first_name, last_name, score in report_rows:
        shown = _format_mark(score)
        style = "green" if score is not None and score >= maximum * .8 else "yellow" if score is not None and score >= maximum * .5 else "red"
        table.add_row(str(student_id), first_name, last_name, f"[{style}]{shown}[/]")
    console.print(table)


def _choose_mark():
    """Ask which individual mark should be analyzed."""
    choices = {"A": ("midterm", 3, 30), "B": ("participation", 4, 30), "C": ("final", 5, 40)}
    while True:
        console.print("Select mark: A. Midterm  B. Participation  C. Final")
        choice = input("Enter choice: ").strip().upper()
        if choice in choices:
            return choices[choice]
        console.print("[yellow]Choose A, B, or C.[/yellow]")


def _show_assessment_reports(rows):
    while True:
        console.print("\n[bold cyan]Assessment Reports[/bold cyan]")
        console.print("A. Midterm  B. Participation  C. Final  D. Back")
        choice = input("Enter choice: ").strip().upper()
        if choice == "D":
            return
        spec = {"A": ("midterm", 30), "B": ("participation", 30), "C": ("final", 40)}
        if choice not in spec:
            console.print("[yellow]Choose A, B, C, or D.[/yellow]")
            continue
        mark, maximum = spec[choice]
        _show_score_report(rows, f"{mark.title()} Report", mark, maximum)


def _show_score_analysis(rows):
    while True:
        console.print("\n[bold cyan]Score Analysis[/bold cyan]")
        console.print("A. Total: descending  B. Total: ascending")
        console.print("C. Mark: descending   D. Mark: ascending")
        console.print("E. Highest and lowest mark  F. Filter mark range  G. Back")
        choice = input("Enter choice: ").strip().upper()
        if choice == "G":
            return
        if choice in ("A", "B"):
            _show_score_report(rows, "Students Sorted by Total", "total", 100, "descending" if choice == "A" else "ascending")
            continue
        if choice not in ("C", "D", "E", "F"):
            console.print("[yellow]Choose A through G.[/yellow]")
            continue
        mark, index, maximum = _choose_mark()
        if choice in ("C", "D"):
            _show_score_report(rows, f"{mark.title()} Scores ({choice.lower()} order)", mark, maximum, "descending" if choice == "C" else "ascending")
        elif choice == "E":
            valid_rows = [row for row in rows if row[index] is not None]
            if not valid_rows:
                console.print(Panel("No recorded scores for this mark.", title=mark.title(), border_style="yellow"))
            else:
                low, high = min(row[index] for row in valid_rows), max(row[index] for row in valid_rows)
                _show_score_report([row for row in valid_rows if row[index] in (low, high)], f"Lowest and Highest {mark.title()} Scores", mark, maximum)
        else:
            while True:
                try:
                    low = int(input(f"Minimum {mark} score (0-{maximum}): ").strip())
                    high = int(input(f"Maximum {mark} score (0-{maximum}): ").strip())
                    if 0 <= low <= high <= maximum:
                        break
                except ValueError:
                    pass
                console.print(f"[yellow]Enter integer bounds from 0 to {maximum}, with minimum no greater than maximum.[/yellow]")
            filtered = [row for row in rows if row[index] is not None and low <= row[index] <= high]
            _show_score_report(filtered, f"{mark.title()} Scores: {low}–{high}", mark, maximum)


def _show_individual_student_report():
    """Ask for an ID and display the student's PostgreSQL record."""
    while True:
        student_id = _student_id_from_input(input("Enter student ID: "))
        if student_id is not None:
            break
        console.print("[yellow]Enter a valid positive integer ID.[/yellow]")

    while True:
        student = _get_student_by_id(student_id)
        if student is False:
            console.print("[bold red]Database error prevented loading the student report.[/bold red]")
            return
        if student is None:
            console.print(f"[yellow]Student ID {student_id} was not found.[/yellow]")
            if get_bin_choice("Would you like to try another ID? (Y/N): ") in ('Y', 'YES'):
                while True:
                    student_id = _student_id_from_input(input("Enter student ID: "))
                    if student_id is not None:
                        break
                    console.print("[yellow]Enter a valid positive integer ID.[/yellow]")
                continue
            return
        break

    marks = (student.midterm, student.participation, student.final)
    total = _student_total(marks)
    details = Table(box=box.SIMPLE, show_header=False, padding=(0, 1), expand=True)
    details.add_column(style="bold cyan", width=20)
    details.add_column(style="white")
    details.add_row("Student ID", str(student.student_id))
    details.add_row("First name", student.first_name)
    details.add_row("Last name", student.last_name)
    details.add_row("Midterm", f"{_format_mark(student.midterm)} / 30")
    details.add_row("Participation", f"{_format_mark(student.participation)} / 30")
    details.add_row("Final", f"{_format_mark(student.final)} / 40")
    total_value = _format_mark(total) if total is None else f"{total} / 100"
    details.add_row("Total", f"[bold green]{total_value}[/bold green]")
    console.print(Panel(details, title="Individual Student Report", border_style="bright_blue", box=box.ROUNDED, padding=(1, 2)))


def show_reports_screen():
    """Route report menu choices to PostgreSQL-backed reports."""
    while True:
        choice = _get_report_choice()
        if choice == 'I':
            console.print("Returning to main menu.")
            return
        if choice == 'A':
            rows = _get_students_for_report()
            if rows is not False:
                _show_student_table(rows)
        elif choice == 'B':
            _show_individual_student_report()
        elif choice in ('C', 'D', 'E', 'F', 'G', 'H', 'J', 'K'):
            rows = _get_students_for_report()
            if rows is False:
                continue
            if choice == 'C':
                _show_score_report(rows, "Students' Total Scores", "total", 100)
            elif choice == 'D':
                table = Table(title="Student Names & IDs", box=box.SIMPLE_HEAVY, header_style="bold cyan", expand=True)
                table.add_column("Student ID", justify="right")
                table.add_column("First Name")
                table.add_column("Last Name")
                if rows:
                    for row in rows:
                        table.add_row(str(row[0]), row[1], row[2])
                    console.print(table)
                else:
                    console.print(Panel("No student records found.", title="Names & IDs", border_style="yellow"))
            elif choice in ('E', 'F', 'G', 'H'):
                mark = {'E': ('midterm', 3, 30), 'F': ('participation', 4, 30), 'G': ('final', 5, 40), 'H': ('total', None, 100)}[choice]
                name, index, maximum = mark
                values = [_student_total(row[3:6]) if name == 'total' else row[index] for row in rows]
                average = _average(values)
                label = f"Average {name.title()}"
                result = _format_mark(average) if average is None else f"{average:.2f} / {maximum}"
                console.print(Panel(f"[bold cyan]{result}[/bold cyan]", title=label, border_style="cyan", box=box.ROUNDED))
            elif choice == 'J':
                _show_assessment_reports(rows)
            else:
                _show_score_analysis(rows)
        else:
            console.print("Returning to main menu.")
            return
