from django.urls import path

from .views import (
    course_detail_view,
    course_enrolled_students_view,
    course_folders_view,
    course_list_create_view,
    course_material_detail_view,
    course_materials_view,
    enroll_course_view,
    my_courses_view,
    student_enrolled_courses_view,
    teacher_created_courses_view,
)

app_name = 'courses'

urlpatterns = [
    path('', course_list_create_view, name='course-list-create'),
    path('my-courses/', my_courses_view, name='my-courses'),
    path('<int:course_id>/', course_detail_view, name='course-detail'),
    path('<int:course_id>/enroll/', enroll_course_view, name='course-enroll'),
    path(
        'students/<int:student_id>/courses/',
        student_enrolled_courses_view,
        name='student-enrolled-courses',
    ),
    path(
        'teachers/my-courses/',
        teacher_created_courses_view,
        name='teacher-my-courses',
    ),
    path(
        'students/my-courses/',
        student_enrolled_courses_view,
        name='student-enrolled-courses',
    ),
    path(
        '<int:course_id>/students/',
        course_enrolled_students_view,
        name='course-enrolled-students',
    ),
    # Folder endpoints
    path(
        '<int:course_id>/folders/', course_folders_view, name='course-folders'
    ),
    # Materials
    path(
        '<int:course_id>/materials/',
        course_materials_view,
        name='course-materials',
    ),
    path(
        'materials/<int:material_id>/',
        course_material_detail_view,
        name='course-material-detail',
    ),
]