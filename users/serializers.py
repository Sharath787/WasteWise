from rest_framework import serializers
from .models import User, CustomerProfile, AgentProfile
from .validators import (
    validate_phone_number,
    validate_otp,
    validate_fullname,
    validate_phone_not_registered,
    validate_phone_is_registered,
    validate_phone_has_agent_profile,
    validate_phone_no_agent_profile
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone", "email", "full_name"]


class checkPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15, validators=[validate_phone_number])


# customer registratio Page 1 - (Collect details and send otp)
class CustomerRegistrationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=15, validators=[validate_phone_number, validate_phone_not_registered]
    )
    full_name = serializers.CharField(max_length=255, validators=[validate_fullname])
    email = serializers.EmailField()


# customer registration page 2 - (verify otp and create user)
class CustomerRegistrationVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15, validators=[validate_phone_number, validate_phone_not_registered]
    )
    otp = serializers.CharField(max_length=6, validators=[validate_otp])
    full_name = serializers.CharField(max_length=255, validators=[validate_fullname])
    email = serializers.EmailField()
    profile_picture = serializers.ImageField(required=False, allow_null=True)

#Customer login send otp serializer
class CustomerLoginSendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15, validators=[validate_phone_number, validate_phone_is_registered]
    )

# Customer login verify otp serializer
class CustomerLoginVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15, validators=[validate_phone_number, validate_phone_is_registered]
    )
    otp = serializers.CharField(max_length=6, validators=[validate_otp])


# Agent registration page 1 - (Collect details and send otp)
class AgentRegistrationSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15, validators=[validate_phone_number, validate_phone_no_agent_profile]
    )
    full_name = serializers.CharField(max_length=255, validators=[validate_fullname])
    email = serializers.EmailField()
    license_number = serializers.CharField(max_length=50)
    vehicle_type = serializers.ChoiceField(choices=AgentProfile.VehicleType.choices)
    vehicle_registration_number = serializers.CharField(max_length=50)
    date_of_birth = serializers.DateField()


# Agent registration page 2 - (verify OTP and create agent profile)
class AgentRegistrationVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15, validators=[validate_phone_number, validate_phone_no_agent_profile]
    )
    otp = serializers.CharField(max_length=6, validators=[validate_otp])
    full_name = serializers.CharField(max_length=255, validators=[validate_fullname])
    email = serializers.EmailField()
    license_number = serializers.CharField(max_length=50)
    vehicle_type = serializers.ChoiceField(choices=AgentProfile.VehicleType.choices)
    vehicle_registration_number = serializers.CharField(max_length=50)
    date_of_birth = serializers.DateField()


# Agent login verify otp serializer(existing agent)
class AgentLoginVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15,
        validators=[
            validate_phone_number,
            validate_phone_is_registered,
            validate_phone_has_agent_profile,
        ],
    )
    otp = serializers.CharField(max_length=6, validators=[validate_otp])

class AgentLoginSendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=15,
        validators=[validate_phone_number, validate_phone_has_agent_profile]
    )

class AgentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AgentProfile
        fields = [
            "user",
            "profile_picture",
            "license_number",
            "date_of_birth",
            "vehicle_type",
            "vehicle_registration_number",
            "verification_status",
            "cur_latitude",
            "cur_longitude",
        ]
