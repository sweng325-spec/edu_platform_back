from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from users.models import SubTodo
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UserStatusSerializer,
)

# Import models from other apps for analytics
from courses.models import Course, Enrollment
# from wallets.models import Transaction, Wallet
from .models import Todo
User = get_user_model()


# Helper function to check admin privileges
def is_admin_user(user):
    return user.is_authenticated and (getattr(user, 'role', '') == getattr(User.Role, 'ADMIN', 'ADMIN') or user.is_staff or user.is_superuser)


# --- AUTHENTICATION & PROFILE VIEWS ---

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user (Student or Teacher) and generate JWT tokens."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate tokens upon registration
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['role'] = user.role

        return Response({
            "message": "User registered successfully.",
            "user": UserProfileSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Authenticate user and return JWT access/refresh tokens with user details."""
    serializer = CustomTokenObtainPairSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Retrieve profile data for the logged-in user."""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change current logged-in user's password."""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- ADMIN CONTROL & ANALYTICS VIEWS ---

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def admin_manage_users(request, user_id=None):
    """
    ADMIN ONLY:
    GET: List all registered users and their activation status.
    PATCH: Activate or deactivate a user account (requires user_id in URL).
    """
    if not is_admin_user(request.user):
        return Response({"error": "Admin access required."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        users = User.objects.all().order_by('-id')
        serializer = UserStatusSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PATCH':
        if not user_id:
            return Response({"error": "User ID is required to update status."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if target_user == request.user:
            return Response({"error": "You cannot deactivate your own admin account."}, status=status.HTTP_400_BAD_REQUEST)

        is_active = request.data.get('is_active')
        if is_active is None or not isinstance(is_active, bool):
            return Response({"error": "Please provide boolean 'is_active' field."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.is_active = is_active
        target_user.save()

        status_str = "activated" if is_active else "deactivated"
        return Response({
            "message": f"User {target_user.email} has been {status_str}.",
            "user": UserStatusSerializer(target_user).data
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_analytics(request):
    """
    ADMIN ONLY: Returns platform-wide analytics data for the admin dashboard.
    """
    if not is_admin_user(request.user):
        return Response({"error": "Admin access required."}, status=status.HTTP_403_FORBIDDEN)

    total_students = User.objects.filter(role=getattr(User.Role, 'STUDENT', 'STUDENT')).count()
    total_teachers = User.objects.filter(role=getattr(User.Role, 'TEACHER', 'TEACHER')).count()
    total_active_users = User.objects.filter(is_active=True).count()
    total_inactive_users = User.objects.filter(is_active=False).count()

    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()

    total_transactions_volume = Transaction.objects.filter(
        status=getattr(Transaction.Status, 'COMPLETED', 'COMPLETED')
    ).aggregate(total=Sum('amount'))['total'] or 0.00

    total_wallet_funds = Wallet.objects.aggregate(total=Sum('balance'))['total'] or 0.00

    analytics_data = {
        "users": {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_active_users": total_active_users,
            "total_inactive_users": total_inactive_users,
        },
        "academics": {
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
        },
        "financials": {
            "total_platform_volume": str(total_transactions_volume),
            "total_system_wallet_funds": str(total_wallet_funds),
        }
    }

    return Response(analytics_data, status=status.HTTP_200_OK)

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Todo
from .serializers import TodoSerializer


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SubTodo, Todo
from .serializers import SubTodoSerializer, TodoSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def todo_list_create_view(request):
    if request.method == 'GET':
        # prefetch_related avoids N+1 queries when serializing nested subtasks
        todos = (
            Todo.objects.filter(user=request.user)
            .prefetch_related('subtasks')
            .order_by('-created_at')
        )
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def todo_detail_view(request, todo_id):
    """
    GET: Retrieve a specific To-Do item with subtasks.
    PUT/PATCH: Update a specific To-Do item.
    DELETE: Remove a specific To-Do item.
    """
    try:
        todo = Todo.objects.prefetch_related('subtasks').get(
            id=todo_id, user=request.user
        )
    except Todo.DoesNotExist:
        return Response(
            {"error": "To-Do item not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = TodoSerializer(todo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = TodoSerializer(todo, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subtodo_create_view(request, todo_id):
    """POST: Create a subtask under a specific parent To-Do."""
    try:
        todo = Todo.objects.get(id=todo_id, user=request.user)
    except Todo.DoesNotExist:
        return Response(
            {"error": "Parent To-Do item not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = SubTodoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(todo=todo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def subtodo_detail_view(request, subtodo_id):
    """
    PATCH: Toggle or update a specific subtask.
    DELETE: Remove a specific subtask.
    """
    try:
        subtodo = SubTodo.objects.select_related('todo').get(
            id=subtodo_id, todo__user=request.user
        )
    except SubTodo.DoesNotExist:
        return Response(
            {"error": "Sub-To-Do item not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'PATCH':
        serializer = SubTodoSerializer(subtodo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        subtodo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)