import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if not isinstance(value, str):
        raise ValidationError(
            'username должен иметь тип str'
        )
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError(
            'Вы используете запрещенные символы для username'
        )
