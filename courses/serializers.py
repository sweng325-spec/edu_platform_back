from rest_framework import serializers
from .models import Course, Enrollment, CourseMaterial


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    # Define as a generic SerializerMethodField or initialize in __init__
    materials = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'teacher', 'teacher_name', 'title', 'description', 'image', 'materials', 'created_at')
        read_only_fields = ('id', 'teacher', 'created_at')

    def get_materials(self, obj):
        # Access CourseMaterialSerializer after it has been defined later in the file
        serializer = CourseMaterialSerializer(obj.materials.all(), many=True, context=self.context)
        return serializer.data


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'course_title', 'enrolled_at')
        read_only_fields = ('id', 'student', 'enrolled_at')


class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = ('id', 'course', 'title', 'material_type', 'file', 'video_url', 'created_at')
        read_only_fields = ('id', 'course', 'created_at')