import re

from rest_framework import serializers

from .models import User

# field level validators for phone number, otp and full name


def validate_phone_number(value):
    # remove any spaces and replace - with empty string

    value = value.strip().replace(" ", "").replace("-", "")

    # check if the phone number is digits only and 10 digits long

    if value.isdigit() and len(value) == 10:
        return value
    else:
        raise serializers.ValidationError(
            "Phone number must be 10 digits long and contain only numbers."
        )


def validate_otp(value):
    value = value.strip()

    # check if the otp is digits only and 6 digits long
    if value.isdigit() and len(value) == 6:
        return value
    else:
        raise serializers.ValidationError(
            "OTP must be 6 digits long and contain only numbers."
        )


def validate_fullname(value):
    value = value.strip()

    # check if the full name contains only alphabets and spaces
    if re.match("^[A-Za-z ]+$", value) and len(value) > 2:
        return value
    else:
        raise serializers.ValidationError(
            "Full name must contain only alphabets and spaces."
        )


# DB validation for user_exists and user_does_not_exist and has_agent_profile and doesnt_have_agent_profile


def validate_phone_not_registered(value):
    if User.objects.filter(phone=value).exists():
        raise serializers.ValidationError(
            "An account with this phone number already exists. Please login instead."
        )
    return value


def validate_phone_is_registered(value):
    if not User.objects.filter(phone=value).exists():
        raise serializers.ValidationError(
            "No account found with this phone number. Please register first."
        )
    return value


def validate_phone_has_agent_profile(value):
    user = User.objects.filter(phone=value).first()

    if not user:
        raise serializers.ValidationError("No account found with this phone number.")

    if not user and not hasattr(user, "agent_profile"):
        raise serializers.ValidationError(
            "No agent profile found. Please register as agent first."
        )

    return value


def validate_phone_no_agent_profile(value):
    user = User.objects.filter(phone=value).first()

    if user and hasattr(user, "agent_profile"):
        raise serializers.ValidationError(
            "An agent account already exists with this phone number. Please login instead."
        )

    return value
