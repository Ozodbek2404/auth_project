from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, VIA_EMAIL, VIA_PHONE
from shared.utility import email_or_phone


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_type = serializers.CharField(read_only=True, required=False)
    auth_status = serializers.CharField(read_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(write_only=True, \
                                                                  required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'auth_type',
            'auth_status'
        ]

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
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
        user.save()
        return user

    def validate(self, data):
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number'))
        user_input_type = email_or_phone(user_input)
        print(user_input_type)
        if user_input_type == 'email':
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL
            }
        elif user_input_type == 'phone':
            data = {
                'phone_number': user_input,
                'auth_type': VIA_PHONE
            }
        else:
            data = {
                'success': 'False',
                'message': 'Telefon raqam yoki email kiriting'
            }
            raise ValidationError(data)

        return data

    def validate_email_phone_number(self, value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            raise ValidationError('Bu email allaqachon mavjud')
        elif value and User.objects.filter(phone_number=value).exists():
            raise ValidationError('Bu telefon raqam allaqachon mavjud')
        return value

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(isinstance)
        data.update(instance.token())
        return data