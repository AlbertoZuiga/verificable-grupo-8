import json

from flask import flash

from app.models import (
    Classroom,
    Course,
    CourseInstance,
    Evaluation,
    EvaluationInstance,
    Section,
    Semester,
    Student,
    StudentSection,
    Teacher,
    User,
    WeighingType,
)

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
    requisite_code_pairs = [] 

    for item in course_list:
        courses.append(Course(
            id=item[JC.ID],
            code=item[JC.CODE],
            title=item[JC.DESCRIPTION],
            credits=item[JC.CREDITS],
        ))

        for req_code in item.get(JC.REQUISITES, []):
            requisite_code_pairs.append((item[JC.CODE], req_code))

    return courses, requisite_code_pairs

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

def parse_sections_json(json_data):
    data = json.loads(json_data)
    parsed_sections = []
    parsed_evaluations = []
    parsed_instances = []

    for section_data in data[JC.SECTIONS]:
        section = Section(
            id=section_data[JC.ID],
            code=section_data[JC.ID], 
            course_instance_id=section_data[JC.COURSE_INSTANCE],
            teacher_id=section_data[JC.TEACHER_ID],
            weighing_type=WeighingType(section_data[JC.EVALUATION][JC.EVALUATION_TYPE].capitalize())
        )
        parsed_sections.append(section)

        evaluation_type = WeighingType(section_data[JC.EVALUATION][JC.EVALUATION_TYPE].capitalize())
        topic_combinations = section_data[JC.EVALUATION][JC.TOPIC_COMBINATIONS]
        topic_details = section_data[JC.EVALUATION][JC.TOPICS]

        for topic in topic_combinations:
            topic_id = topic[JC.ID]
            topic_def = topic_details[str(topic_id)]

            evaluation = Evaluation(
                id=topic_id,
                section=section,
                title=topic[JC.NAME],
                weighing=topic[JC.TOPIC_WEIGHT],
                weighing_system=evaluation_type
            )
            parsed_evaluations.append(evaluation)

            for i in range(topic_def[JC.TOPIC_COUNT]):
                instance = EvaluationInstance(
                    evaluation=evaluation,
                    index_in_evaluation=i + 1,
                    title=f"{topic[JC.NAME]} {i + 1}",
                    instance_weighing=topic_def[JC.TOPIC_VALUES][i],
                    optional=topic_def[JC.TOPIC_MANDATORY][i]
                )
                parsed_instances.append(instance)

    print(f"[DEBUG] Parsed {len(parsed_sections)} sections, {len(parsed_evaluations)} evaluations, and {len(parsed_instances)} evaluation instances.")

    return parsed_sections, parsed_evaluations, parsed_instances

def parse_student_sections_json(json_data):
    data = json.loads(json_data)
    student_section_data = data[JC.STUDENT_SECTIONS]

    parsed_links = []
    for item in student_section_data:
        parsed_links.append(StudentSection(
            section_id=item[JC.SECTION_ID],
            student_id=item[JC.STUDENT_ID]
        ))
    return parsed_links

def parse_grades_json(json_data):
    data = json.loads(json_data)
    grades_raw = data[JC.GRADES]

    parsed_grades = []
    for entry in grades_raw:
        parsed_grades.append({
            "student_id": entry[JC.STUDENT_ID],
            "topic_id": entry[JC.TOPIC_ID],
            "instance_index": entry[JC.INSTANCE],
            "grade": entry[JC.GRADE]
        })

    return parsed_grades