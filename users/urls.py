from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from users.views import (
    AgentCheckPhoneView,
    AgentLoginSendOTPView,
    AgentLoginVerifyView,
    AgentRegisterVerifyView,
    AgentRegisterView,
    CustomerCheckPhoneView,
    CustomerLoginSendOTPView,
    CustomerLoginVerifyView,
    CustomerRegisterVerifyView,
    CustomerRegisterView,
)

urlpatterns = [
    # Customer auth
    path(
        "customer/check-phone/",
        CustomerCheckPhoneView.as_view(),
        name="customer-check-phone",
    ),
    path("customer/register/", CustomerRegisterView.as_view()),
    path("customer/register/verify/", CustomerRegisterVerifyView.as_view()),
    path("customer/login/send_otp/", CustomerLoginSendOTPView.as_view()),
    path("customer/login/verify/", CustomerLoginVerifyView.as_view()),
    # Agent auth
    path("agent/check-phone/", AgentCheckPhoneView.as_view()),
    path("agent/register/", AgentRegisterView.as_view()),
    path("agent/register/verify/", AgentRegisterVerifyView.as_view()),
    path("agent/login/send_otp/", AgentLoginSendOTPView.as_view()),
    path("agent/login/verify/", AgentLoginVerifyView.as_view()),
    # Token management
    # name gives the url the unique identifier, so we can reference it by reverse('name')
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
]
