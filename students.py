class Student:
    # Hold one student's ID, name, and score attributes during screen operations.
    def __init__(self, student_id, name, midterm=None, participation=None, final=None):
        self.student_id = student_id
        self.name = name
        self.midterm = midterm
        self.participation = participation
        self.final = final   


def update_student_in_file(student: Student):
    students_data = []
    # Read all records and replace the one matching this Student object.
    with open("students.txt", "r") as f:
        for line in f:
            data = line.strip().split(",")

            if int(data[0]) == student.student_id:

                data = [
                    str(student.student_id).strip(),
                    student.name.strip(),
                    str(student.midterm).strip(),
                    str(student.participation).strip(),
                    str(student.final).strip()
                ]
            
            students_data.append(data)

    # Rewrite the file with the updated record and all other records intact.
    with open("students.txt", "w") as f:
        for data in students_data:
            f.write(",".join(data) + "\n")


def delete_student_from_file(student_id):
    # Keep every other record and rewrite the file only when the ID is found.
    students_data = []
    found = False # Flag to indicate if the student was found and deleted
    with open("students.txt", "r") as f:
        for line in f:
            data = line.strip().split(",")
            if int(data[0]) == student_id: # If the student ID matches, we skip adding
                found = True
            else: # Keep all other records
                students_data.append(line)

    if found:
        with open("students.txt", "w") as f:
            f.writelines(students_data)
    return found
