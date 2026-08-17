from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'role': self.user.role,
            'username': self.user.username,
        }
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')

    def validate_role(self, value):
        # Restrict registration to STUDENT or TEACHER roles
        valid_roles = [getattr(User.Role, 'STUDENT', 'STUDENT'), getattr(User.Role, 'TEACHER', 'TEACHER')]
        if value not in valid_roles:
            raise serializers.ValidationError("Role must be either STUDENT or TEACHER.")
        return value

    def create(self, validated_data):
        default_role = getattr(User.Role, 'STUDENT', 'STUDENT')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', default_role)
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_active')
        read_only_fields = ('id', 'username', 'email', 'role', 'is_active')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_active')
        read_only_fields = ('id', 'username', 'email', 'role')
        
        
from rest_framework import serializers
from .models import Todo

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ('id', 'user', 'title', 'completed', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')
        
        
from rest_framework import serializers
from .models import Todo, SubTodo


class SubTodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTodo
        fields = ('id', 'todo', 'title', 'completed', 'created_at')
        read_only_fields = ('id', 'todo', 'created_at')


class TodoSerializer(serializers.ModelSerializer):
    subtasks = SubTodoSerializer(many=True, required=False)

    class Meta:
        model = Todo
        fields = (
            'id', 
            'user', 
            'title', 
            'completed', 
            'deadline_date', 
            'expected_duration_hours', 
            'subtasks', 
            'created_at'
        )
        read_only_fields = ('id', 'user', 'created_at')

    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        todo = Todo.objects.create(**validated_data)
        for subtask_data in subtasks_data:
            SubTodo.objects.create(todo=todo, **subtask_data)
        return todo

    def update(self, instance, validated_data):
        subtasks_data = validated_data.pop('subtasks', None)
        instance.title = validated_data.get('title', instance.title)
        instance.completed = validated_data.get('completed', instance.completed)
        instance.deadline_date = validated_data.get('deadline_date', instance.deadline_date)
        instance.expected_duration_hours = validated_data.get('expected_duration_hours', instance.expected_duration_hours)
        instance.save()

        if subtasks_data is not None:
            instance.subtasks.all().delete()
            for subtask_data in subtasks_data:
                SubTodo.objects.create(todo=instance, **subtask_data)

        return instance