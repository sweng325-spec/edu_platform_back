from rest_framework import serializers

from .models import Course, CourseFolder, CourseMaterial, Enrollment


class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = (
            'id',
            'course',
            'folder',
            'title',
            'material_type',
            'file',
            'video_url',
            'created_at',
        )
        read_only_fields = ('id', 'course', 'created_at')


class CourseFolderSerializer(serializers.ModelSerializer):
    materials = CourseMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = CourseFolder
        fields = ('id', 'course', 'name', 'order', 'materials', 'created_at')
        read_only_fields = ('id', 'course', 'created_at')


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(
        source='teacher.username', read_only=True
    )
    folders = CourseFolderSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            'id',
            'teacher',
            'teacher_name',
            'title',
            'description',
            'image',
            'folders',
            'created_at',
        )
        read_only_fields = ('id', 'teacher', 'created_at')


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'course_title', 'enrolled_at')
        read_only_fields = ('id', 'student', 'enrolled_at')