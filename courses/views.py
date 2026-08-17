from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
# courses/views.py

# Update this import line to include parser_classes
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from .permissions import IsTeacherOrReadOnly
# from wallets.models import Transaction


@api_view(['GET', 'POST'])
@permission_classes([IsTeacherOrReadOnly])
@parser_classes([MultiPartParser, FormParser])
def course_list_create_view(request):
    """
    GET: List all available courses.
    POST: Create a new course (Teacher only).
    """
    if request.method == 'GET':
        courses = Course.objects.all().order_by('-created_at')
        serializer = CourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = CourseSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(teacher=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def course_detail_view(request, course_id):
    """GET: Retrieve details of a specific course."""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CourseSerializer(course)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course_view(request, course_id):
    """
    POST: Purchase a course using the student's wallet balance and create an enrollment.
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

    student = request.user

    # Prevent duplicate enrollment
    if Enrollment.objects.filter(student=student, course=course).exists():
        return Response({"error": "You are already enrolled in this course."}, status=status.HTTP_400_BAD_REQUEST)

    # # student_wallet = getattr(student, 'wallet', None)
    # # teacher_wallet = getattr(course.teacher, 'wallet', None)

    # if not student_wallet or not teacher_wallet:
    #     return Response({"error": "Wallet missing for student or teacher."}, status=status.HTTP_400_BAD_REQUEST)

    # if student_wallet.balance < course.price:
    #     return Response({"error": "Insufficient wallet balance to enroll in this course."}, status=status.HTTP_400_BAD_REQUEST)

    # with transaction.atomic():
    #     # Transfer funds from student to teacher
    #     student_wallet.balance -= course.price
    #     teacher_wallet.balance += course.price
    #     student_wallet.save()
    #     teacher_wallet.save()

    #     # Record purchase transaction
    #     Transaction.objects.create(
    #         sender=student_wallet,
    #         receiver=teacher_wallet,
    #         amount=course.price,
    #         transaction_type=Transaction.TransactionType.COURSE_PURCHASE,
    #         status=Transaction.Status.COMPLETED
    #     )

        # Enroll student
    enrollment = Enrollment.objects.create(student=student, course=course)

    serializer = EnrollmentSerializer(enrollment)
    return Response({
        "message": "Enrolled successfully!",
        "enrollment": serializer.data,
        # "remaining_balance": str(student_wallet.balance)
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_courses_view(request):
    """
    GET: Retrieve courses enrolled by the logged-in student 
    or created by the logged-in teacher.
    """
    if request.user.role == 'TEACHER':
        courses = Course.objects.filter(teacher=request.user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        enrollments = Enrollment.objects.filter(student=request.user)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_enrolled_courses_view(request, student_id):
    """
    GET: Retrieve all courses in which a specific student is enrolled.
    """
    # Fetch all enrollments for the given student
    enrollments = Enrollment.objects.filter(student_id=student_id).select_related('course')
    
    # Extract the associated Course instances
    courses = [enrollment.course for enrollment in enrollments]
    
    # Serialize course details using CourseSerializer
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_created_courses_view(request):
    """
    GET: Retrieve all courses created by the authenticated teacher/instructor.
    """
    courses = Course.objects.filter(teacher=request.user).order_by('-created_at')
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


from users.models import User
from users.serializers import UserProfileSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import UserProfileSerializer
from .models import Course, Enrollment




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_enrolled_students_view(request, course_id):
    """
    GET: Retrieve all students enrolled in a specific course using apps/users custom User model.
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check permission using your custom User.Role enum
    is_admin = (
        getattr(request.user, 'role', '') == User.Role.ADMIN
        or request.user.is_staff
        or request.user.is_superuser
    )

    if course.teacher != request.user and not is_admin:
        return Response(
            {"error": "You do not have permission to view this roster."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # Fetch enrollments and extract student instances
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    students = [enrollment.student for enrollment in enrollments]

    # Serialize using your UserProfileSerializer
    serializer = UserProfileSerializer(students, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Course, CourseMaterial, Enrollment
from .serializers import CourseMaterialSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def course_materials_view(request, course_id):
    """
    GET: List all materials for a course (If enrolled, teacher, or admin).
    POST: Add a PDF or Video material to a course (Instructor only).
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Check if user is teacher or enrolled student
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        if course.teacher != request.user and not is_enrolled and not request.user.is_staff:
            return Response({"error": "You must be enrolled to access course materials."}, status=status.HTTP_403_FORBIDDEN)

        materials = course.materials.all().order_by('-created_at')
        serializer = CourseMaterialSerializer(materials, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if course.teacher != request.user:
            return Response({"error": "Only the course teacher can upload materials."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CourseMaterialSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def course_material_detail_view(request, material_id):
    """
    DELETE: Remove a specific material item.
    """
    try:
        material = CourseMaterial.objects.get(id=material_id, course__teacher=request.user)
    except CourseMaterial.DoesNotExist:
        return Response({"error": "Material not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

    material.delete()
    return Response({"message": "Material deleted successfully."}, status=status.HTTP_204_NO_CONTENT)