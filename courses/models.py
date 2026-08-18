from django.conf import settings
from django.db import models


class Course(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_created',
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to='course_images/', null=True, blank=True
    )

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrolled_students'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')


class CourseFolder(models.Model):
    """Represents folders or sections inside a course (e.g., 'Lec 1', 'Lec 2')."""

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='folders'
    )
    name = models.CharField(max_length=255)  # e.g., "Lecture 1: Introduction"
    order = models.PositiveIntegerField(
        default=0
    )  # Allows sorting folders sequentially
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.course.title} - {self.name}'


class CourseMaterial(models.Model):
    class MaterialType(models.TextChoices):
        PDF = 'PDF', 'PDF Document'
        VIDEO = 'VIDEO', 'Video'

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='materials'
    )
    folder = models.ForeignKey(
        CourseFolder,
        on_delete=models.CASCADE,
        related_name='materials',
        null=True,
        blank=True,  # Keeps materials optional if not grouped into a folder
    )
    title = models.CharField(max_length=255)
    material_type = models.CharField(
        max_length=10, choices=MaterialType.choices
    )
    file = models.FileField(
        upload_to='course_materials/', null=True, blank=True
    )
    video_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.course.title} - {self.title} ({self.material_type})'