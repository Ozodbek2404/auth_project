from datetime import datetime

from django.shortcuts import render
from django.views.generic import UpdateView

from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, NEW, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE, DONE, PHOTO_DONE
from users.serializers import SignUpSerializer, UserChangeInfoSerializer, UserPhotoSerializer
from rest_framework import permissions, status


class SignUpView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)


class VerifyCode(APIView):
    permissions_classes = (permissions.IsAuthenticated,)

    def post(self, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify_code(user, code)
        data = {
            'success': True,
            'auth_status': user.auth_status,
            'access_token': user.token()['access'],
            'refresh': user.token()['refresh_token']
        }
        return Response(data)

    @staticmethod
    def check_verify_code(user, code):
        verify = user.verify_codes.filter(code=code, confirmed=False, expiration_time__gte=datetime.now())
        if not verify.exists():
            data = {
                'success': False,
                'message': 'Kod eskirgan yoki xato'
            }
            raise ValidationError(data)
        else:
            verify.update(confirmed=True)

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()

        return True


class NewVerifyCode(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        self.check_code(user)
        if user.auth_type == VIA_EMAIL:
            code = user.generate_code(VIA_EMAIL)
            print(code)
            # send_mail(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.generate_code(VIA_PHONE)
            print(code)
            # send_phone_number_sms(user.phone_number, code)
        else:
            data = {
                'success': 'False',
                'message': 'Telefon raqam uoki email togri kiriting'
            }
            raise ValidationError(data)
        data = {
            'success': True,
            'message': 'Kod yuborildi'
        }
        return Response(data)

    @staticmethod
    def check_code(user):
        verify = user.verify_codes.filter(confirmed=False, expiration_time__gte=datetime.now())
        if verify.exists():
            data = {
                'success': False,
                'message': 'Sizda active code mavjud'
            }
            raise ValidationError(data)
        if user.auth_status in [CODE_VERIFIED, DONE, PHOTO_DONE]:
            data = {
                'success': False,
                'message': 'Sizda code tasdiqlangan'
            }
            raise ValidationError(data)
        return True


class UserChangeView(UpdateView):
    permission_classes = (permissions.IsAuthenticated)
    queryset = User.objects.all()
    serializer_class = UserChangeInfoSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        data = {
            'success': False,
            'message': 'Malumotlaringiz yangilandi'
        }
        return Response(data)

    def partial_update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        data = {
            'success': False,
            'message': 'Malumotlaringiz qisman yangilandi'
        }
        return Response(data)


class UserPhotoUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        user = request.user

        if not request.FILES.get('photo'):
            data = {
                'success': False,
                'message': 'Rasm yuborilmadi'
            }
            raise ValidationError(data)

        serializer = UserPhotoSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            data = {
                'success': True,
                'message': 'Rasm muvaffaqiyatli yuklandi',
                'auth_status': user.auth_status
            }
            return Response(data)

        data = {
            'success': False,
            'message': serializer.errors
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)