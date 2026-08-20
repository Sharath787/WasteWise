from rest_framework import serializers

from users.models import AgentProfile, CustomerProfile, User
from users.validators import (
    validate_fullname,
    validate_otp,
    validate_phone_has_agent_profile,
    validate_phone_is_registered,
    validate_phone_no_agent_profile,
    validate_phone_not_registered,
    validate_phone_number,
)

# ── Mixins ────────────────────────────────────────────────────────────────────


class PhoneValidatorMixin:
    def validate_phone(self, value: str) -> str:
        value = value.strip().replace(" ", "").replace("-", "")
        validate_phone_number(value)
        return value


class OTPValidatorMixin:
    def validate_otp(self, value: str) -> str:
        value = value.strip()
        validate_otp(value)
        return value


class FullNameValidatorMixin:
    def validate_full_name(self, value: str) -> str:
        value = value.strip()
        validate_fullname(value)
        return value


# ── Serializers ───────────────────────────────────────────────────────────────


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "phone", "email", "full_name"]


class CheckPhoneSerializer(PhoneValidatorMixin, serializers.Serializer):
    phone = serializers.CharField(max_length=15)


class CustomerRegisterSerializer(
    PhoneValidatorMixin,
    FullNameValidatorMixin,
    serializers.Serializer,
):
    phone = serializers.CharField(max_length=15)
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()

    def validate_phone(self, value: str) -> str:
        value = super().validate_phone(value)  # type: ignore[misc]
        validate_phone_not_registered(value)
        return value


class CustomerRegisterVerifySerializer(
    PhoneValidatorMixin,
    OTPValidatorMixin,
    FullNameValidatorMixin,
    serializers.Serializer,
):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    def validate_phone(self, value: str) -> str:
        value = super().validate_phone(value)  # type: ignore[misc]
        validate_phone_not_registered(value)
        return value


class CustomerLoginSendOTPSerializer(PhoneValidatorMixin, serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value: str) -> str:
        value = super().validate_phone(value)  # type: ignore[misc]
        validate_phone_is_registered(value)
        return value


class CustomerLoginVerifySerializer(
    PhoneValidatorMixin,
    OTPValidatorMixin,
    serializers.Serializer,
):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

    def validate_phone(self, value: str) -> str:
        value = super().validate_phone(value)  # type: ignore[misc]
        validate_phone_is_registered(value)
        return value


class AgentRegisterSerializer(
    PhoneValidatorMixin,
    FullNameValidatorMixin,
    serializers.Serializer,
):
    phone = serializers.CharField(max_length=15)
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    license_number = serializers.CharField(max_length=50)
    vehicle_type = serializers.ChoiceField(choices=AgentProfile.VehicleType.choices)
    vehicle_registration_number = serializers.CharField(max_length=50)
    date_of_birth = serializers.DateField()

    def validate_phone(self, value: str) -> str:
        value = super().validate_phone(value)  # type: ignore[misc]
        validate_phone_no_agent_profile(value)
        return value


class AgentRegisterVerifySerializer(
    PhoneValidatorMixin,
    OTPValidatorMixin,
    FullNameValidatorMixin,
    serializers.Serializer,
):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    license_number = serializers.CharField(max_length=50)
    vehicle_type = serializers.ChoiceField(choices=AgentProfile.VehicleType.choices)
    vehicle_registration_number = serializers.CharField(max_length=50)
    date_of_birth = serializers.DateField()

    def validate_phone(self, value: str) -> str:
        value = super().validate_phone(value)  # type: ignore[misc]
        validate_phone_no_agent_profile(value)
        return value


class AgentLoginSendOTPSerializer(PhoneValidatorMixin, serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value: str) -> str:
        value = super().validate_phone(value)  # type: ignore[misc]
        validate_phone_has_agent_profile(value)
        return value


class AgentLoginVerifySerializer(
    PhoneValidatorMixin,
    OTPValidatorMixin,
    serializers.Serializer,
):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

    def validate_phone(self, value: str) -> str:
        value = super().validate_phone(value)  # type: ignore[misc]
        validate_phone_has_agent_profile(value)
        return value


class CustomerProfileSerializer(serializers.ModelSerializer[CustomerProfile]):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ["id", "user", "profile_picture", "created_at"]


class AgentProfileSerializer(serializers.ModelSerializer[AgentProfile]):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AgentProfile
        fields = [
            "id",
            "user",
            "profile_picture",
            "license_number",
            "vehicle_type",
            "vehicle_registration_number",
            "verification_status",
            "is_available",
            "created_at",
        ]
