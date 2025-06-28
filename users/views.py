from django.db import transaction
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.generics import CreateAPIView
from users.models import CustomUser
from .serializers import (
    RegisterValidateSerializer,
    AuthValidateSerializer,
    ConfirmationSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from users.serializers import CustomToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.cache import cache
from users.tasks import send_otp_email
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import store_verification_code

class AuthorizationAPIView(TokenObtainPairView):
    serializer_class = CustomToken

    # def post(self, request):
    #     serializer = AuthValidateSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     user = authenticate(**serializer.validated_data)

    #     if user:
    #         if not user.is_active:
    #             return Response(
    #                 status=status.HTTP_401_UNAUTHORIZED,
    #                 data={"error": "User account is not activated yet!"},
    #             )

    #         token, _ = Token.objects.get_or_create(user=user)
    #         return Response(data={"key": token.key})

    #     return Response(
    #         status=status.HTTP_401_UNAUTHORIZED,
    #         data={"error": "User credentials are wrong!"},
        # )


class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data.get("email")
            username = serializer.validated_data.get("username")
            birthday = serializer.validated_data.get("birthday")
            password = serializer.validated_data["password"]
            confirmation_code = store_verification_code(email)
            # Use transaction to ensure data consistency
            with transaction.atomic():
                user = CustomUser.objects.create_user(
                    email=email,
                    username=username,
                    password=password,
                    birthday=birthday,
                    is_active=False,
                    # confirmation_code=confirmation_code,
                )
                send_otp_email.delay(email, confirmation_code)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
                status=status.HTTP_201_CREATED,
                data={"user_id": user.id, "confirmation_code": confirmation_code},
            )


class ConfirmUserAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ConfirmationSerializer)
    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data.get("user_id")

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()

        cache_key = f'verify:{user.email}'
        cache.delete(cache_key)

        refresh = RefreshToken.for_user(user)
        return Response(
            status=status.HTTP_200_OK,
            data={
                "message": "User аккаунт успешно активирован",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomToken
