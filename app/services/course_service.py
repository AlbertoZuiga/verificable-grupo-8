from app.models.course import Course

def get_course_and_other_courses(course_id):
    course = Course.query.get_or_404(course_id)

    # Obtener los IDs de los cursos requisitos
    requisite_ids = {requisite.course_requisite_id for requisite in course.prerequisites}
    
    # Obtener los cursos que no son el actual ni sus requisitos
    courses = Course.query.filter(
        Course.id != course_id,
        Course.id.notin_(requisite_ids)
    ).all()

    return course, courses
