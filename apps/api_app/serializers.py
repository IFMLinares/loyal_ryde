from rest_framework_jwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from ..loyalRyde.models import CustomUser, CustomUserDriver


class UserSerializers(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    username = serializers.CharField(
        required=True,
        max_length = 32,
        validators = [UniqueValidator(queryset=CustomUser.objects.all())]
    )

    first_name = serializers.CharField(
        required=True,
        max_length = 32,
    )

    last_name = serializers.CharField(
        required=True,
        max_length = 32,
    )

    password = serializers.CharField(
        required=True,
        min_length=8,
        write_only=True,
    )
    
    class Meta:
        model = CustomUser
        fields = '__all__' 

class CustomUserDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserDriver
        fields = '__all__'