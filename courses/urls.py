from django.urls import path
from .views import (
    course_list_create_view,
    course_detail_view,
    enroll_course_view,
    my_courses_view,
)

app_name = 'courses'

urlpatterns = [
    # List all courses or create a new course
    path('', course_list_create_view, name='course-list-create'),

    # View enrolled courses (students) or created courses (teachers)
    path('my-courses/', my_courses_view, name='my-courses'),

    # Single course detail
    path('<int:course_id>/', course_detail_view, name='course-detail'),

    # Enroll / Purchase course
    path('<int:course_id>/enroll/', enroll_course_view, name='course-enroll'),
]