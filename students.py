class Student:
    def __init__(
        self,
        student_id,
        first_name,
        last_name,
        midterm=0,
        participation=0,
        final=0
    ):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.midterm = midterm
        self.participation = participation
        self.final = final
