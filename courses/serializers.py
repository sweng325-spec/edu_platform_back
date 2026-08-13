from rest_framework import serializers
from .models import Course, Enrollment

class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'teacher', 'teacher_name', 'title', 'description', 'price', 'created_at')
        read_only_fields = ('id', 'teacher', 'created_at')


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'course_title', 'enrolled_at')
        read_only_fields = ('id', 'student', 'enrolled_at')