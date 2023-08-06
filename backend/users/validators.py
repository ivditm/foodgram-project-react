import re

from django.core.exceptions import ValidationError

PATTERN_USER = r'^[\w.@+-]+\Z'
USERNAME_VALIDATION_ERROR_MESSAGE = ('Имя пользователя не соответствует '
                                     'паттерну')


def validate_username(value):
    if not re.match(PATTERN_USER, value):
        raise ValidationError(USERNAME_VALIDATION_ERROR_MESSAGE)
    return value
