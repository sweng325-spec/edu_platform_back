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