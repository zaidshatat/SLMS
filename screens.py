from students import Student
import psycopg
from database import create_connection
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def _show_menu(title, options):
    table = Table(title=title, box=box.ROUNDED, border_style="blue", header_style="bold")
    table.add_column("Option", style="bold cyan", justify="center", no_wrap=True)
    table.add_column("Description")
    for letter, description in options:
        table.add_row(letter, description)
    console.print(table)

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
    _show_menu("Main Menu", [
        ("A", "Add a new student (press A)"),
        ("B", "Modify a student (press B)"),
        ("C", "Show reports (press C)"),
        ("D", "Delete a student (press D)"),
        ("E", "Exit the program (press E)"),
    ])


def get_bin_choice(message):
    while True:
        _show_menu("Choose an option", [("Y", "Yes"), ("N", "No")])
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
        return name.capitalize()

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
        _show_menu("What would you like to modify?", [
            ("A", "Midterm"),
            ("B", "Participation"),
            ("C", "Final"),
            ("D", "Name"),
            ("E", "Exit to main menu"),
        ])
        
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
        """
cur.execute(query, values)
                if cur.rowcount != 1:
                    conn.rollback()
                    print("The student record was not updated because it could not be found.")
                    return

"""
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
    while True:
        _show_menu("Student Reports", [
            ("A", "All Students"),
            ("B", "Individual Student"),
            ("C", "Total Scores"),
            ("D", "Names & IDs"),
            ("E", "Average Midterm"),
            ("F", "Average Participation"),
            ("G", "Average Final"),
            ("H", "Average Total"),
            ("I", "Return to Main Menu"),
            ("J", "Assessment Reports"),
            ("K", "Score Sorting & Filters"),
        ])
        choice = input("Enter your choice: ").strip().upper()
        if choice in tuple("ABCDEFGHIJK"):
            return choice
        print("Invalid choice. Select A through K.")


def _show_all_students():
    conn = create_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, first_name, last_name, midterm, participation, final FROM students ORDER BY id")
            return cur.fetchall()
    except psycopg.Error as e:
        print(f"Could not retrieve student information: {e}")
        return None
    finally:
        conn.close()


def _show_all_students_report():
    students = _show_all_students()
    if students is None:
        return
    if not students:
        print("No students found.")
        return
    table = Table(title="All Students")
    table.add_column("ID")
    table.add_column("First Name")
    table.add_column("Last Name")
    table.add_column("Midterm")
    table.add_column("Participation")
    table.add_column("Final")
    for student in students:
        table.add_row(*[str(value) for value in student])
    console.print(table)


def _show_individual_student_report():
    while True:
        student_id = _student_id_from_input(input("Enter student ID: "))
        if student_id is None:
            print("Invalid student ID. Enter a positive whole number.")
            continue
        student = _get_student_by_id(student_id)
        if student is False:
            return
        if student is None:
            print("Student ID not found.")
            if get_bin_choice("Would you like to try another ID? (Y/N): ") in ('N', 'NO'):
                return
            continue

        table = Table(title="Individual Student")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Midterm")
        table.add_column("Participation")
        table.add_column("Final")

        table.add_row(str(student.student_id),
                      f"{student.first_name} {student.last_name}",
                      str(student.midterm),
                      str(student.participation),
                      str(student.final))
        console.print(table)
        return


def _show_total_scores_report():
    students = _show_all_students()
    if students is None:
        return
    table = Table(title="Total Scores")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Total")
    for row in students:
        table.add_row(str(row[0]), f"{row[1]} {row[2]}", str(sum(row[3:6])))
    console.print(table)


def _show_names_and_ids_report():
    students = _show_all_students()
    if students is None:
        return
    table = Table(title="Student Names and IDs")
    table.add_column("ID")
    table.add_column("Name")
    for row in students:
        table.add_row(str(row[0]), f"{row[1]} {row[2]}")
    console.print(table)


def _show_average_report(column, title):
    conn = create_connection()
    if conn is None:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT AVG({column}) FROM students")
            average = cur.fetchone()[0]
        if average is None:
            print(f"No scores available for {title}.")
        else:
            table = Table(title=f"{title} AVG")
            table.add_column(f"{column}_avg")
            table.add_row(str(round(average, 2)))
            console.print(table)
    except psycopg.Error as e:
        print(f"Could not retrieve average score: {e}")
    finally:
        conn.close()


def _show_average_total_report():
    students = _show_all_students()
    if students is None:
        return
    totals = [sum(row[3:6]) for row in students]
    if totals:
        print(f"Average Total: {sum(totals) / len(totals):.2f}")
    else:
        print("No total scores available.")


def _show_assessment_reports():
    _show_menu("Choose assessment", [
        ("A", "Midterm"),
        ("B", "Participation"),
        ("C", "Final"),
    ])
    choice = input("Choose assessment: ").strip().upper()
    assessments = {'A': ('midterm', 'Midterm'), 'B': ('participation', 'Participation'), 'C': ('final', 'Final')}
    if choice not in assessments:
        print("Invalid assessment choice.")
        return
    column, title = assessments[choice]
    students = _show_all_students()
    if students is None:
        return
    table = Table(title=f"{title} Scores")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column(f"{column}_score")
    index = {'midterm': 3, 'participation': 4, 'final': 5}[column]
    for row in students:
        table.add_row(str(row[0]), f"{row[1]} {row[2]}", str(row[index]))
    console.print(table)


def _show_score_sorting_and_filters():
    _show_menu("Score Sorting & Filters", [
        ("A", "Sort total scores"),
        ("B", "Filter an assessment score"),
    ])
    choice = input("Enter your choice: ").strip().upper()
    students = _show_all_students()
    if students is None:
        return
    if choice == 'A':
        students.sort(key=lambda row: sum(row[3:6]), reverse=True)
        table = Table(title="Students Sorted by Total")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Total")
        for row in students:
            table.add_row(str(row[0]), f"{row[1]} {row[2]}", str(sum(row[3:6])))
        console.print(table)
    elif choice == 'B':
        _show_menu("Choose assessment", [
            ("A", "Midterm"),
            ("B", "Participation"),
            ("C", "Final"),
        ])
        assessment = input("Choose assessment: ").strip().upper()
        assessments = {'A': ('Midterm', 3, 30), 'B': ('Participation', 4, 30), 'C': ('Final', 5, 40)}
        if assessment not in assessments:
            print("Invalid assessment choice.")
            return
        name, index, maximum = assessments[assessment]
        try:
            low = int(input(f"Minimum {name} score (0-{maximum}): "))
            high = int(input(f"Maximum {name} score (0-{maximum}): "))
        except ValueError:
            print("Enter whole numbers for the score range.")
            return
        if low < 0 or high > maximum or low > high:
            print("Invalid score range.")
            return
        table = Table(title=f"{name} Scores from {low} to {high}")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Score")
        for row in students:
            if low <= row[index] <= high:
                table.add_row(str(row[0]), f"{row[1]} {row[2]}", str(row[index]))
        console.print(table)
    else:
        print("Invalid choice.")


def show_reports_screen():
    while True:
        choice = _get_report_choice()
        match choice:
            case 'A':
                _show_all_students_report()
            case 'B':
                _show_individual_student_report()
            case 'C':
                _show_total_scores_report()
            case 'D':
                _show_names_and_ids_report()
            case 'E':
                _show_average_report("midterm", "Midterm")
            case 'F':
                _show_average_report("participation", "Participation")
            case 'G':
                _show_average_report("final", "Final")
            case 'H':
                _show_average_total_report()
            case 'I':
                print("Returning to main menu.")
                return
            case 'J':
                _show_assessment_reports()
            case 'K':
                _show_score_sorting_and_filters()
