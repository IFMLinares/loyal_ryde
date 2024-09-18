from rest_framework_jwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..loyalRyde.models import CustomUser, CustomUserDriver,TransferStop, Desviation, OTPCode, TransferRequest,PeopleTransfer, Rates, Desviation
User = get_user_model()

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
    image = serializers.ImageField(max_length=None, use_url=True)
    license = serializers.ImageField(max_length=None, use_url=True)

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

# Serializer for TransferRequest

class UserSerializer(serializers.ModelSerializer):
    company_image_url = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'company_image_url'] 
    
    def get_company_image_url(self, obj):
        if obj.company and obj.company.image:
            return obj.company.image.url
        return None


class PersonToTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeopleTransfer
        fields = ['name', 'phone', 'company']

class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rates
        fields = '__all__'

class DeviationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desviation
        fields = '__all__'

class TransferRequestSerializer(serializers.ModelSerializer):
    person_to_transfer = PersonToTransferSerializer(many=True, read_only=True)
    rate = RateSerializer(read_only=True)
    service_requested = UserSerializer(read_only=True)
    deviation = DeviationSerializer(many=True, read_only=True)

    class Meta:
        model = TransferRequest
        fields = '__all__'

class TransferRequestStatusUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=TransferRequest.STATUS_CHOICES)
