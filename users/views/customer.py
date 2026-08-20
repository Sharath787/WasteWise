from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomerProfile, User
from users.serializers import (
    CheckPhoneSerializer,
    CustomerLoginSendOTPSerializer,
    CustomerLoginVerifySerializer,
    CustomerRegisterSerializer,
    CustomerRegisterVerifySerializer,
    UserSerializer,
)
from users.utils import (
    OTP_COOLDOWN_TIME,
    can_send_otp,
    generate_otp,
    send_otp,
    store_otp,
    verify_otp,
)


class CustomerCheckPhoneView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = CheckPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        user = User.objects.filter(phone=phone).first()

        if not user:
            return Response(
                {
                    "user_exists": False,
                    "prefill": None,
                    "otp_cooldown_seconds": OTP_COOLDOWN_TIME,
                },
                status=status.HTTP_200_OK,
            )

        has_customer_profile = hasattr(user, "customer_profile")

        if has_customer_profile:
            return Response(
                {
                    "user_exists": True,
                    "prefill": None,
                    "otp_cooldown_seconds": OTP_COOLDOWN_TIME,
                },
                status=status.HTTP_200_OK,
            )

        # user exists but no customer profile
        # this means they registered as agents first
        # prefill basic details
        return Response(
            {
                "user_exists": True,
                "prefill": {
                    "full_name": user.full_name,
                    "email": user.email,
                    "phone": user.phone,
                },
                "otp_cooldown_seconds": OTP_COOLDOWN_TIME,
            },
            status=status.HTTP_200_OK,
        )


class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = CustomerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        can_send, message, retry_after = can_send_otp(phone)

        if not can_send:
            return Response(
                {
                    "error": message,
                    "retry_after": retry_after,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        otp = generate_otp()
        store_otp(phone, otp)
        send_otp(phone, otp)

        return Response(
            {
                "message": "OTP sent successfully",
            },
            status=status.HTTP_200_OK,
        )


class CustomerRegisterVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = CustomerRegisterVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]
        full_name = serializer.validated_data["full_name"]
        email = serializer.validated_data["email"]
        profile_picture = serializer.validated_data.get("profile_picture", None)

        verify_otp(phone, otp)

        try:
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    "full_name": full_name,
                    "email": email,
                },
            )
        except IntegrityError:
            user = User.objects.get(phone=phone)
            created = False

        if created:
            user.set_unusable_password()
            user.save()

        # Create or get CustomProfile
        profile, _ = CustomerProfile.objects.get_or_create(user=user)

        # Add profile picture if provided

        if profile_picture:
            profile.profile_picture = profile_picture
            profile.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Registration Successfull",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomerLoginSendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = CustomerLoginSendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        can_send, message, retry_after = can_send_otp(phone)

        if not can_send:
            return Response(
                {
                    "error": message,
                    "retry_after": retry_after,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        otp = generate_otp()
        store_otp(phone, otp)
        send_otp(phone, otp)

        return Response(
            {
                "message": "OTP sent successfuly",
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class CustomerLoginVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = CustomerLoginVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]

        # Verify OTP — raises ValidationError if invalid
        verify_otp(phone, otp)

        # Fetch user and generate tokens
        user = User.objects.get(phone=phone)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
