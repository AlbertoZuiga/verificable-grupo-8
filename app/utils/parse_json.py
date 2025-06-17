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
    
    if JC.CLASSROOMS not in data:
        raise ValueError(f"Falta la clave '{JC.CLASSROOMS}' en el JSON.")
    json_dictionary = data[JC.CLASSROOMS]

    for item in json_dictionary:
        if JC.ID not in item:
            raise ValueError(f"Falta la clave '{JC.ID}' en un elemento de '{JC.CLASSROOMS}'.")
        if JC.NAME not in item:
            raise ValueError(f"Falta la clave '{JC.NAME}' en un elemento de '{JC.CLASSROOMS}'.")
        if JC.CAPACITY not in item:
            raise ValueError(f"Falta la clave '{JC.CAPACITY}' en un elemento de '{JC.CLASSROOMS}'.")

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
    
    if JC.STUDENTS not in data:
        raise ValueError(f"Falta la clave '{JC.STUDENTS}' en el JSON.")
    student_list = data[JC.STUDENTS]

    for item in student_list:
        if JC.NAME not in item:
            raise ValueError(f"Falta la clave '{JC.NAME}' en un elemento de '{JC.STUDENTS}'.")
        if JC.EMAIL not in item:
            raise ValueError(f"Falta la clave '{JC.EMAIL}' en un elemento de '{JC.STUDENTS}'.")
        if JC.ID not in item:
            raise ValueError(f"Falta la clave '{JC.ID}' en un elemento de '{JC.STUDENTS}'.")
        if JC.ENTRY_YEAR not in item:
            raise ValueError(f"Falta la clave '{JC.ENTRY_YEAR}' en un elemento de '{JC.STUDENTS}'.")

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
    
    if JC.TEACHERS not in data:
        raise ValueError(f"Falta la clave '{JC.TEACHERS}' en el JSON.")
    teacher_list = data[JC.TEACHERS]

    for item in teacher_list:
        if JC.NAME not in item:
            raise ValueError(f"Falta la clave '{JC.NAME}' en un elemento de '{JC.TEACHERS}'.")
        if JC.EMAIL not in item:
            raise ValueError(f"Falta la clave '{JC.EMAIL}' en un elemento de '{JC.TEACHERS}'.")
        if JC.ID not in item:
            raise ValueError(f"Falta la clave '{JC.ID}' en un elemento de '{JC.TEACHERS}'.")

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
    
    if JC.COURSES not in data:
        raise ValueError(f"Falta la clave '{JC.COURSES}' en el JSON.")
    course_list = data[JC.COURSES]

    courses = []
    requisite_code_pairs = [] 

    for item in course_list:
        if JC.ID not in item:
            raise ValueError(f"Falta la clave '{JC.ID}' en un elemento de '{JC.COURSES}'.")
        if JC.CODE not in item:
            raise ValueError(f"Falta la clave '{JC.CODE}' en un elemento de '{JC.COURSES}'.")
        if JC.DESCRIPTION not in item:
            raise ValueError(f"Falta la clave '{JC.DESCRIPTION}' en un elemento de '{JC.COURSES}'.")
        if JC.CREDITS not in item:
            raise ValueError(f"Falta la clave '{JC.CREDITS}' en un elemento de '{JC.COURSES}'.")

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
    
    if JC.YEAR not in data:
        raise ValueError(f"Falta la clave '{JC.YEAR}' en el JSON.")
    year = data[JC.YEAR]

    if JC.SEMESTER not in data:
        raise ValueError(f"Falta la clave '{JC.SEMESTER}' en el JSON.")
    semester_value = data[JC.SEMESTER]

    if JC.COURSE_INSTANCES not in data:
        raise ValueError(f"Falta la clave '{JC.COURSE_INSTANCES}' en el JSON.")
    course_instances_list = data[JC.COURSE_INSTANCES]
    
    try:
        semester_enum = Semester(semester_value)
    except ValueError:
        flash(f"Invalid semester value '{semester_value}'. No course instances parsed.", "danger")
        return []

    instances = []
    for item in course_instances_list:
        if JC.ID not in item:
            raise ValueError(f"Falta la clave '{JC.ID}' en un elemento de '{JC.COURSE_INSTANCES}'.")
        if JC.COURSE_ID not in item:
            raise ValueError(f"Falta la clave '{JC.COURSE_ID}' en un elemento de '{JC.COURSE_INSTANCES}'.")

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

    if JC.SECTIONS not in data:
        raise ValueError(f"Falta la clave '{JC.SECTIONS}' en el JSON.")
    
    for section_data in data[JC.SECTIONS]:
        if JC.EVALUATION not in section_data:
            raise ValueError(f"Falta la clave '{JC.EVALUATION}' en un elemento de '{JC.SECTIONS}'.")
        evaluation_data = section_data[JC.EVALUATION]

        if JC.EVALUATION_TYPE not in evaluation_data:
            raise ValueError(f"Falta la clave '{JC.EVALUATION_TYPE}' en la evaluación de un elemento de '{JC.SECTIONS}'.")
        if JC.TOPIC_COMBINATIONS not in evaluation_data:
            raise ValueError(f"Falta la clave '{JC.TOPIC_COMBINATIONS}' en la evaluación de un elemento de '{JC.SECTIONS}'.")
        if JC.TOPICS not in evaluation_data:
            raise ValueError(f"Falta la clave '{JC.TOPICS}' en la evaluación de un elemento de '{JC.SECTIONS}'.")

        section_weighing_type = WeighingType(evaluation_data[JC.EVALUATION_TYPE].capitalize())
        topic_combinations = evaluation_data[JC.TOPIC_COMBINATIONS]
        topic_details = evaluation_data[JC.TOPICS]

        if JC.ID not in section_data:
            raise ValueError(f"Falta la clave '{JC.ID}' en un elemento de '{JC.SECTIONS}'.")
        if JC.COURSE_INSTANCE not in section_data:
            raise ValueError(f"Falta la clave '{JC.COURSE_INSTANCE}' en un elemento de '{JC.SECTIONS}'.")
        if JC.TEACHER_ID not in section_data:
            raise ValueError(f"Falta la clave '{JC.TEACHER_ID}' en un elemento de '{JC.SECTIONS}'.")

        section = Section(
            id=section_data[JC.ID],
            code=section_data[JC.ID], 
            course_instance_id=section_data[JC.COURSE_INSTANCE],
            teacher_id=section_data[JC.TEACHER_ID],
            weighing_type=section_weighing_type
        )
        parsed_sections.append(section)


        if section_weighing_type == WeighingType.PERCENTAGE:
            total = sum(topic[JC.TOPIC_WEIGHT] for topic in topic_combinations)
            if total != 0 and total != 100:
                for topic in topic_combinations:
                    original = topic[JC.TOPIC_WEIGHT]
                    topic[JC.TOPIC_WEIGHT] = round((original / total) * 100, 2)
        
        for topic in topic_combinations:
            if JC.ID not in topic:
                raise ValueError(f"Falta la clave '{JC.ID}' en un topic de '{JC.TOPIC_COMBINATIONS}'.")
            topic_id = topic[JC.ID]

            if str(topic_id) not in topic_details:
                raise ValueError(f"Falta la definición para el topic id '{topic_id}' en '{JC.TOPICS}'.")

            topic_def = topic_details[str(topic_id)]

            if JC.EVALUATION_TYPE not in topic_def:
                raise ValueError(f"Falta la clave '{JC.EVALUATION_TYPE}' en la definición de topic '{topic_id}'.")
            if JC.TOPIC_VALUES not in topic_def:
                raise ValueError(f"Falta la clave '{JC.TOPIC_VALUES}' en la definición de topic '{topic_id}'.")
            if JC.TOPIC_COUNT not in topic_def:
                raise ValueError(f"Falta la clave '{JC.TOPIC_COUNT}' en la definición de topic '{topic_id}'.")
            if JC.TOPIC_MANDATORY not in topic_def:
                raise ValueError(f"Falta la clave '{JC.TOPIC_MANDATORY}' en la definición de topic '{topic_id}'.")

            evaluation_weighing_type = WeighingType(topic_def[JC.EVALUATION_TYPE].capitalize())
            
            if evaluation_weighing_type == WeighingType.PERCENTAGE:
                total_instance_weight = sum(topic_def[JC.TOPIC_VALUES])
                if total_instance_weight != 0 and total_instance_weight != 100:
                    topic_def[JC.TOPIC_VALUES] = [round((v / total_instance_weight) * 100, 2) for v in topic_def[JC.TOPIC_VALUES]]
            
            evaluation = Evaluation(
                id=topic_id,
                section=section,
                title=topic[JC.NAME],
                weighing=topic[JC.TOPIC_WEIGHT],
                weighing_system=evaluation_weighing_type,
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
    
    if JC.STUDENT_SECTIONS not in data:
        raise ValueError(f"Falta la clave '{JC.STUDENT_SECTIONS}' en el JSON.")
    student_section_data = data[JC.STUDENT_SECTIONS]

    parsed_links = []
    for item in student_section_data:
        if JC.SECTION_ID not in item:
            raise ValueError(f"Falta la clave '{JC.SECTION_ID}' en un elemento de '{JC.STUDENT_SECTIONS}'.")
        if JC.STUDENT_ID not in item:
            raise ValueError(f"Falta la clave '{JC.STUDENT_ID}' en un elemento de '{JC.STUDENT_SECTIONS}'.")

        parsed_links.append(StudentSection(
            section_id=item[JC.SECTION_ID],
            student_id=item[JC.STUDENT_ID]
        ))
    return parsed_links

def parse_grades_json(json_data):
    data = json.loads(json_data)
    
    if JC.GRADES not in data:
        raise ValueError(f"Falta la clave '{JC.GRADES}' en el JSON.")
    grades_raw = data[JC.GRADES]

    parsed_grades = []
    for entry in grades_raw:
        if JC.STUDENT_ID not in entry:
            raise ValueError(f"Falta la clave '{JC.STUDENT_ID}' en un elemento de '{JC.GRADES}'.")
        if JC.TOPIC_ID not in entry:
            raise ValueError(f"Falta la clave '{JC.TOPIC_ID}' en un elemento de '{JC.GRADES}'.")
        if JC.INSTANCE not in entry:
            raise ValueError(f"Falta la clave '{JC.INSTANCE}' en un elemento de '{JC.GRADES}'.")
        if JC.GRADE not in entry:
            raise ValueError(f"Falta la clave '{JC.GRADE}' en un elemento de '{JC.GRADES}'.")

        parsed_grades.append({
            "student_id": entry[JC.STUDENT_ID],
            "topic_id": entry[JC.TOPIC_ID],
            "instance_index": entry[JC.INSTANCE],
            "grade": entry[JC.GRADE]
        })

    return parsed_grades