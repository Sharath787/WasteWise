from rest_framework import serializers
import re


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
