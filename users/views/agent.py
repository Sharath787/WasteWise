from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User, AgentProfile
from django.db import IntegrityError

from users.serializers import (
    AgentRegistrationSerializer,
    AgentRegistrationVerifySerializer,
    checkPhoneSerializer,
    AgentLoginVerifySerializer,
    AgentProfileSerializer,
    UserSerializer,
    AgentLoginSendOTPSerializer,
)
from users.utils import (
    generate_otp,
    send_otp,
    can_send_otp,
    store_otp,
    verify_otp,
)


class AgentCheckPhoneView(APIView):
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
                    'agent_exists': False,
                    'prefill': None,
                }, status=status.HTTP_200_OK
            )

        has_agent_profile = hasattr(user, 'agent_profile')

        #Send otp if agentprofile exists

        if has_agent_profile:
            return Response(
                {
                    'user_exists': True,
                    'agent_exists': True,
                    'prefill': None,
                }, status=status.HTTP_200_OK
            )

        return Response(
            {
                'user_exists': True,
                'agent_exists': False,
                'prefill': {
                    'phone': user.phone,
                    'email': user.email,
                    'full_name': user.full_name,
                }
            }, status=status.HTTP_200_OK
        )


class AgentRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AgentRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data[phone]

        can_send, message = can_send_otp(phone)

        if not can_send:
            return Response({
                'error': message,
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        otp = generate_otp
        send_otp(phone, otp)
        store_otp(phone, otp)

        return Response({
            'message': 'OTP sent successfully'
        }, status=status.HTTP_200_OK)


class AgentRegisterVerifiyView(APIView)
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AgentRegistrationVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone                       = serializer.validated_data['phone']
        otp                         = serializer.validated_data['otp']
        full_name                   = serializer.validated_data['full_name']
        email                       = serializer.validated_data['email']
        license_number              = serializer.validated_data['license_number']
        vehicle_type                = serializer.validated_data['vehicle_type']
        vehicle_registration_number = serializer.validated_data['vehicle_registration_number']
        date_of_birth               = serializer.validated_data['date_of_birth']

        verify_otp(phone, otp)

        #get or create user
        try:
            user, created = User.objects.get_or_create(
                phone = phone,
                defaults = {
                    'full_name': full_name,
                    'email': email,
                }
            )
        except IntegrityError:
            user = User.objects.get(phone=phone)
            created = False

        if created:
            user.set_unusable_password()
            user.save()

        AgentProfile.objects.create(
            user = user,
            license_number = license_number,
            vehicle_type = vehicle_type,
            vehicle_registration_number = vehicle_registration_number,
            date_of_birth = date_of_birth,
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
            'message': 'Agent registration successfull',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED
        )

class AgentLoginSentOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AgentLoginSendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data[phone]

        can_send, message = can_send_otp(phone)

        if not can_send:
            return Response(
                {'error': message},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        otp = generate_otp()
        store_otp(phone, otp)
        send_otp(phone, otp)

        return Response(
            {
                'message': 'Successfully sent OTP',
            }, status=status.HTTP_200_OK
        )

class AgentLoginVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AgentLoginVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data[phone]
        otp = serializer.validated_data[otp]

        verify_otp(phone, otp)

        user = User.objects.get(phone=phone)
        refresh = RefreshToken.for_user(user)


        return Response(
            {
                'message': 'Login Successful.',
                'access_token': refresh.access_token,
                'refresh_token': refresh,
                'user': UserSerializer(user).data,
            }, status=status.HTTP_200_OK
        )


