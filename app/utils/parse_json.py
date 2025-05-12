import json
from app.models import Classroom, User, Student
from app.utils import json_constants as JC

def parse_classroom_json(json_data):
    classrooms = []
    data = json.loads(json_data)
    json_dictionary = data[JC.CLASSROOMS]

    for item in json_dictionary:
        classroom = Classroom(
            id=item[JC.ID],
            name=item[JC.NAME],
            capacity=item[JC.CAPACITY],
        )
        classrooms.append(classroom)

    return classrooms

def parse_students_json(json_data):
    result = []
    data = json.loads(json_data)
    student_list = data[JC.STUDENTS]

    for item in student_list:
        name_parts = item[JC.NAME].split(" ")
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=item[JC.EMAIL]
        )
        user.set_password(f"password_{item[JC.NAME]}")

        student = Student(
            id=item[JC.ID],
            user=user,
            university_entry_year=item[JC.ENTRY_YEAR]
        )

        result.append((user, student))

    return result