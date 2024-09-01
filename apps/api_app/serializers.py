from rest_framework_jwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from ..loyalRyde.models import CustomUser, CustomUserDriver,TransferStop, Desviation, OTPCode


class UserSerializers(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    class Meta:
        model = CustomUser
        fields = '__all__' 

class CustomUserDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserDriver
        fields = '__all__'

class TransferStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferStop
        fields = '__all__'

class DesviationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desviation
        fields = '__all__'

class OTPCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPCode
        fields = '__all__'
