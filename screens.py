from students import Student, update_student_in_file, delete_student_from_file
import pandas as pd

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


def get_user_choice():
    # Keep asking until the user enters a valid menu letter.
    while True:
        choice = input("\nEnter your choice: ").strip().upper()
        if choice not in ['A', 'B', 'C', 'D', 'E']:
            # if the user enters an invaled choice
            print("\nInvalid choice. Please try again.")
            continue
        return choice

def _new_id_check():
    # Accept only an integer ID that is not already in the student file.
    while True: # check if the student ID is unique and valid
        error_message = "Invalid input. Please enter a valid student ID."
        try:
            raw_student_id = input("\nEnter student ID: ").strip()
            if len(raw_student_id) != 5 or not raw_student_id.isascii() or not raw_student_id.isdecimal():
                raise ValueError
            student_id = int(raw_student_id)
            if student_id < 10000 or student_id > 99999:
                raise ValueError
            with open("students.txt", "r") as file:
                for line in file:
                    existing_id = int(line.split(",")[0])
                    if student_id == existing_id:
                        error_message = "Student ID already exists. Please enter a unique ID."
                        raise ValueError
            break
        except ValueError:
            print(error_message)
    return student_id

def _name_check():
    # Require a non-empty name containing only letters and spaces.
    while True: # check if the student name is valid
        name = input("Enter student name: ").strip()
        if not name or not all(char.isalpha() or char.isspace() for char in name):
            print("Name cannot be empty or digits. Please try again.")
            continue
        break
    return name

def add_student():
    # Collect validated details, append a new record, and optionally repeat.
    while True:    
        with open("students.txt", "a") as f: # open the file that contains the students information

            student_id = _new_id_check() # check if the student ID is unique and valid
            name = _name_check() # check if the student name is valid

            # create a new student object and write the information to the file
            student = Student(student_id, name)
            f.write(f"{student.student_id},{student.name},{student.midterm},{student.participation},{student.final}\n")
            
            print("Student added successfully!")
            print(f"Student ID: {student.student_id}, Name: {student.name}")
            while True:
                another_add = input("\nWould you like to add another student? (Y/N): ").strip().upper()
                if another_add not in ['Y', 'N']:
                    print("Invalid choice. Please try again.")
                    continue
                break
        if another_add == 'N':
            break

# Collect the attribute choice for the current student's edit loop.
def get_modify_choice():
    # Validate the attribute choice before returning it to the edit flow.
    while True:
        print("\nWhat would you like to modify?")
        print("A. Midterm")
        print("B. Participation")
        print("C. Final")
        print("D. Exit to main menu")
        
        choice = input("Enter your choice: ").strip().upper()

        if choice not in ['A', 'B', 'C', 'D']:
            print("Invalid choice. Please try again.")
            continue
        return choice

def _get_student_by_id(student_id):
    # Find a record and convert its stored values into a Student object.
    with open("students.txt", "r") as f:
        for line in f:
            student_data = line.strip().split(",")
            if int(student_data[0]) == student_id:
                return Student(
                    int(student_data[0]),
                        student_data[1],
                        None if student_data[2] == "None" else float(student_data[2]),
                        None if student_data[3] == "None" else float(student_data[3]),
                        None if student_data[4] == "None" else float(student_data[4])
                    )
        else:
            return None

def _student_id_from_input(raw_student_id):
    if not raw_student_id.isascii() or not raw_student_id.isdecimal():
        return None
    if len(raw_student_id) > 5:
        return None
    student_id = int(raw_student_id)
    if len(raw_student_id) == 5:
        return student_id if 10000 <= student_id <= 99999 else None
    if str(student_id) == raw_student_id:
        student = _get_student_by_id(student_id)
        if student is not None:
            return student_id
    return None


def modify_student_info():
    # Find the student once; reuse this object for each requested attribute change.
    while True:
        try:
            raw_student_id = input("Enter student ID to modify: ").strip()
            student_id = _student_id_from_input(raw_student_id)
            if student_id is None:
                raise ValueError
            student = _get_student_by_id(student_id)

            if student is None:
                print("Student ID not found.")
                while True:
                    retry = input("Would you like to enter another Student ID? (Y/N): ").strip().upper()
                    if retry in ['Y', 'N']:
                        break
                if retry == 'Y':
                    continue
                print("Returning to main menu.")
                return

        except ValueError:
            print("Invalid input. Please enter a valid student ID.")
            while True:
                retry = input("Would you like to enter another Student ID? (Y/N): ").strip().upper()
                if retry in ['Y', 'N']:
                    break
            if retry == 'N':
                print("Returning to main menu.")
                return
            continue
        break

    while True:
        # Show current values before each mark selection.
        print(f"\nCurrent student: ID: {student.student_id}, Name: {student.name}, Midterm: {student.midterm}, Participation: {student.participation}, Final: {student.final}")
        choice = get_modify_choice()
        if choice == 'D':
            print("Returning to main menu.")
            return

        attributes = {
            'A': ('midterm', 'midterm score', 30),
            'B': ('participation', 'participation score', 20),
            'C': ('final', 'final score', 50),
        }
        attribute, label, maximum = attributes[choice]

        # Validate the new score against the selected attribute's allowed range.
        while True:
            try:
                value = float(input(f"Enter {label}: "))
                if value < 0 or value > maximum:
                    print(f"Score must be between 0 and {maximum}. Please try again.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid score.")
        # Update the Student object and persist the change to the file.
        setattr(student, attribute, value)

        # Persist each accepted change before asking whether to continue.
        update_student_in_file(student)
        print(f"{label.capitalize()} updated to {value} for student {student.name} (ID: {student.student_id})")

        # Ask whether to modify another mark for the same student or return to the main menu.
        while True:
            another = input("Would you like to modify another attribute for this student? (Y/N): ").strip().upper()
            if another in ['Y', 'N']:
                break
            print("Invalid choice. Please try again.")
        if another != 'Y':
            print("Returning to main menu.")
            return


def delete_student_info():
    # Validate the ID, show the matching record, and require confirmation before deletion.
    while True:
        try:
            raw_student_id = input("Enter student ID to delete: ").strip()
            student_id = _student_id_from_input(raw_student_id)
            if student_id is None:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter a valid student ID.")

    student = _get_student_by_id(student_id)
    if student is None:
        print("Student ID not found.")
        return
    print(f"Student: ID: {student.student_id}, Name: {student.name}, Midterm: {student.midterm}, Participation: {student.participation}, Final: {student.final}")
    confirmation = input("Are you sure you want to delete this student? (Y/N): ").strip().upper()
    if confirmation != 'Y':
        print("Deletion cancelled.")
        return
    if delete_student_from_file(student_id):
        print("Student deleted successfully.")


def _get_report_choice():
    # Return a valid report option or keep prompting.
    while True:
        print("\nWhich report would you like to view?")
        print("A. Show all students")
        print("B. Show individual student")
        print("C. Show students' final grades")
        print("D. Show IDs and names of all students")
        print("E. Show average midterm scores")
        print("F. Show average participation scores")
        print("G. Show average final scores")
        print("H. Show average total scores")
        print("I. Exit to main menu")

        choice = input("Enter your choice: ").strip().upper()

        if choice not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
            print("Invalid choice. Please try again.")
            continue
        return choice

# Route report choices and return to the main menu when requested.
def show_reports_screen():

    while True:
        choice = _get_report_choice()

        if choice == 'I':
            print("Returning to main menu.")
            return

        match choice:
            case 'A':
                show_all_students()
            case 'B':
                show_individual_student()
            case 'C':
                show_final_grades()
            case 'D':
                show_ids_and_names()
            case 'E':
                show_average_midterm_scores()
            case 'F':
                show_average_participation_scores()
            case 'G':
                show_average_final_scores()
            case 'H':
                show_average_total_scores()

        # ask the user if they want to view another report
        while True:
            another_report = input("\nWould you like to view another report? (Y/N): ").strip().upper()
            if another_report not in ['Y', 'N']:
                print("Invalid choice. Please try again.")
                continue
            break
        if another_report == 'N':
            break


REPORT_COLUMNS = ['Student_ID', 'Name', 'Midterm', 'Participation', 'Final']


def load_students_data():
    """Load student records from the existing comma-separated text file."""
    try:
        # Pandas reads the comma-separated file and treats unentered grades as missing values.
        data = pd.read_csv(
            'students.txt',
            header=None,
            names=REPORT_COLUMNS,
            na_values=['None'],
            keep_default_na=True,
        )
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=REPORT_COLUMNS)

    # Keep identifiers readable while parsing grade fields as numbers.
    for column in ['Student_ID', 'Midterm', 'Participation', 'Final']:
        data[column] = pd.to_numeric(data[column], errors='coerce')
        
    return data


def _show_report(data):
    # Display a report table or explain that there are no records.
    if data.empty:
        print('No student records found.')
        return
    print(data.to_string(index=False, na_rep='N/A'))


def _with_total(data):
    # Calculate totals only for students who have all three scores.
    result = data.copy()
    grade_columns = ['Midterm', 'Participation', 'Final']
    complete = result[grade_columns].notna().all(axis=1)
    result['Total'] = result[grade_columns].sum(axis=1, min_count=3).where(complete)
    return result


def show_all_students():
    # Load and display every student record.
    _show_report(load_students_data())


def show_individual_student():
    # Validate the requested ID and display its matching record.
    data = load_students_data()
    if data.empty:
        print('No student records found.')
        return
    while True:
        raw_id = input('Enter Student ID: ').strip()
        student_id = _student_id_from_input(raw_id)
        if student_id is None:
            print('Invalid input. Please enter a valid Student ID.')
            continue
        break
    student = data[data['Student_ID'] == student_id]
    if student.empty:
        print(f'Student ID {student_id} not found.')
        return
    _show_report(student)


def show_final_grades():
    # Display each student's total when all scores are available.
    data = load_students_data()
    if data.empty:
        print('No student records found.')
        return
    _show_report(_with_total(data)[['Student_ID', 'Name', 'Total']])


def show_ids_and_names():
    # Display the identifying columns for all students.
    _show_report(load_students_data()[['Student_ID', 'Name']])


def _show_average(column, label):
    # Calculate and display the average for one score column.
    data = load_students_data()
    if data.empty:
        print('No student records found.')
        return
    average = data[column].mean()
    if pd.isna(average):
        print(f'Average {label}: N/A')
    else:
        print(f'Average {label}: {average:.2f}')


def show_average_midterm_scores():
    _show_average('Midterm', 'midterm score')


def show_average_participation_scores():
    _show_average('Participation', 'participation score')


def show_average_final_scores():
    _show_average('Final', 'final score')


def show_average_total_scores():
    # Average only the complete totals produced by _with_total().
    data = load_students_data()
    if data.empty:
        print('No student records found.')
        return
    average = _with_total(data)['Total'].mean()
    if pd.isna(average):
        print('Average total grade: N/A')
    else:
        print(f'Average total grade: {average:.2f}')
