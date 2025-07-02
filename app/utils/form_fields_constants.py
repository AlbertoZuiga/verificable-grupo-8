class CourseFields:
    ID = "id"
    TITLE = "title"
    CODE = "code"
    CREDITS = "credits"


class CourseInstanceFields:
    ID = "id"
    COURSE_ID = "course_id"
    YEAR = "year"
    SEMESTER = "semester"


class SectionFields:
    ID = "id"
    COURSE_INSTANCE_ID = "course_instance_id"
    CODE = "code"
    WEIGHING_TYPE = "weighing_type"
    TEACHER_ID = "teacher_id"


class UserFields:
    ID = "id"
    EMAIL = "email"
    PASSWORD_HASH = "password_hash"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"


class StudentFields:
    ID = "id"
    USER_ID = "user_id"
    UNIVERSITY_ENTRY_YEAR = "university_entry_year"


class TeacherFields:
    ID = "id"
    USER_ID = "user_id"


class RequisiteFields:
    ID = "id"
    COURSE_ID = "course_id"
    COURSE_REQUISITE_ID = "course_requisite_id"


class EvaluationFields:
    ID = "id"
    SECTION_ID = "section_id"
    TITLE = "title"
    WEIGHING = "weighing"
    WEIGHING_SYSTEM = "weighing_system"


class EvaluationInstanceFields:
    ID = "id"
    INDEX_IN_EVALUATION = "index_in_evaluation"
    EVALUATION_ID = "evaluation_id"
    TITLE = "title"
    INSTANCE_WEIGHING = "instance_weighing"
    OPTIONAL = "optional"


class StudentSectionFields:
    SECTION_ID = "section_id"
    STUDENT_ID = "student_id"


class StudentEvaluationInstanceFields:
    EVALUATION_INSTANCE_ID = "evaluation_instance_id"
    STUDENT_ID = "student_id"
    GRADE = "grade"


class ClassroomFields:
    ID = "id"
    NAME = "name"
    CAPACITY = "capacity"


class TimeBlockFields:
    ID = "id"
    START_TIME = "start_time"
    STOP_TIME = "stop_time"
    WEEKDAY = "weekday"


class AssignedTimeBlockFields:
    ID = "id"
    SECTION_ID = "section_id"
    CLASSROOM_ID = "classroom_id"
    TIME_BLOCK_ID = "time_block_id"
