from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, CustomerProfile
from users.serializers import (
    checkPhoneSerializer,
    CustomerLoginSendOTPSerializer,
    CustomerLoginVerifySerializer,
    CustomerRegistrationVerifySerializer,
    CustomerRegistrationSerializer,
    UserSerializer,
)

from users.utils import (
    generate_otp,
    send_otp,
    verify_otp,
    can_send_otp,
    store_otp,
)

class CustomerCheckPhoneView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = checkPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data[phone]

        user = User.objects.filter(phone=phone).first()

        if not user:
            return Response(
                {
                    'user_exists': False,
                    'prefill': None,
                }, status=status.HTTP_200_OK
            )

        has_customer_profile = hasattr(user, 'customer_profile')

        if has_customer_profile:
            return Response(
                {
                    'user_exists': True,
                    'prefill': None
                }, status=status.HTTP_200_OK
            )

        #user exists but no customer profile
        #this means they registered as agents first
        #prefill basic details
        return Response(
            {
                'user_exists': True,
                'prefill': {
                    'full_name': user.full_name,
                    'email': user.email,
                    'phone': user.phone,
                },
            }, status=status.HTTP_200_OK
        )


class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data[phone]

        can_send, message = can_send_otp(phone)

        if not can_send:
            return Response(
                {
                    'error': message,
                }, status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        otp = generate_otp()
        store_otp(phone, otp)
        send_otp(phone, otp)

        return Response(
            {
                'message': "OTP sent successfully",
            }, status=status.HTTP_200_OK

        )


class CustomerRegisterVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(request, data):
        serializer = CustomerRegistrationVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data[phone]
        otp = serializer.validated_data[otp]
        full_name = serializer.validated_data[full_name]
        email = serializer.validated_data[email]
        profile_picture = serializer.validated_data[profile_picture]

        verify_otp(phone, otp)

        user, created = User.objects.get_or_create(
            'phone': phone,
        )
