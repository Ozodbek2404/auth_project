import re
from rest_framework.exceptions import ValidationError

email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
phone_regex = re.compile(r"^(?:\+998[ -]?)?(?:[1-9]\d{1,2}|[5789]\d)\s?\d{3}\s?\d{2}\s?\d{2}$")


def email_or_phone_number(email_phone_number):
    if re.fullmatch(email_regex, email_phone_number):
        email_or_phone = 'email'
    elif re.fullmatch(phone_regex, email_phone_number):
        email_or_phone = 'phone'
    else:
        data = {
            'succes': 'False',
            'message':'Telefon raqam yoki email xato kiritildi'
        }
        raise ValidationError(data)
    return email_or_phone