from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from .permissions import IsTeacherOrReadOnly
from wallets.models import Transaction


@api_view(['GET', 'POST'])
@permission_classes([IsTeacherOrReadOnly])
def course_list_create_view(request):
    """
    GET: List all available courses.
    POST: Create a new course (Teacher only).
    """
    if request.method == 'GET':
        courses = Course.objects.all().order_by('-created_at')
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = CourseSerializer(data=request.data)
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

    student_wallet = getattr(student, 'wallet', None)
    teacher_wallet = getattr(course.teacher, 'wallet', None)

    if not student_wallet or not teacher_wallet:
        return Response({"error": "Wallet missing for student or teacher."}, status=status.HTTP_400_BAD_REQUEST)

    if student_wallet.balance < course.price:
        return Response({"error": "Insufficient wallet balance to enroll in this course."}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        # Transfer funds from student to teacher
        student_wallet.balance -= course.price
        teacher_wallet.balance += course.price
        student_wallet.save()
        teacher_wallet.save()

        # Record purchase transaction
        Transaction.objects.create(
            sender=student_wallet,
            receiver=teacher_wallet,
            amount=course.price,
            transaction_type=Transaction.TransactionType.COURSE_PURCHASE,
            status=Transaction.Status.COMPLETED
        )

        # Enroll student
        enrollment = Enrollment.objects.create(student=student, course=course)

    serializer = EnrollmentSerializer(enrollment)
    return Response({
        "message": "Enrolled successfully!",
        "enrollment": serializer.data,
        "remaining_balance": str(student_wallet.balance)
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