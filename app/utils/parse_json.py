import json
from flask import flash
from app.models import Classroom, User, Student, Teacher, Course, Semester, CourseInstance
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

def parse_teachers_json(json_data):
    result = []
    data = json.loads(json_data)
    teacher_list = data[JC.TEACHERS]

    for item in teacher_list:
        name_parts = item[JC.NAME].split(" ")
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=item[JC.EMAIL]
        )
        user.set_password(f"password_{item[JC.NAME]}")

        teacher = Teacher(
            id=item[JC.ID],
            user=user
        )

        result.append((user, teacher))

    return result

def parse_courses_json(json_data):
    data = json.loads(json_data)
    course_list = data[JC.COURSES]

    courses = []
    requisite_relations = []

    for item in course_list:
        course = Course(
            id=item[JC.ID],
            code=item[JC.CODE],
            title=item[JC.DESCRIPTION],
            credits=item[JC.CREDITS],
        )
        courses.append(course)

        # Store requisite links (by course code)
        for req_code in item.get(JC.REQUISITES, []):
            requisite_relations.append({
                JC.MAIN_COURSE_CODE: item[JC.CODE],
                JC.REQUISITE_CODE: req_code
            })

    return {
        JC.COURSES: courses,
        JC.REQUISITES: requisite_relations
    }

def parse_course_instances_json(json_data):
    data = json.loads(json_data)
    year = data[JC.YEAR]
    semester_value = data[JC.SEMESTER]
    
    try:
        semester_enum = Semester(semester_value)
    except ValueError:
        flash(f"Invalid semester value '{semester_value}'. No course instances parsed.", "danger")
        return []

    instances = []
    for item in data[JC.COURSE_INSTANCES]:
        instance = CourseInstance(
            id=item[JC.ID],
            course_id=item[JC.COURSE_ID],
            year=year,
            semester=semester_enum
        )
        instances.append(instance)

    return instances