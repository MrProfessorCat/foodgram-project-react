import re

from django.core.exceptions import ValidationError


def validate_tag_color(value):
    if not isinstance(value, str):
        raise ValidationError(
            'color должен иметь тип str'
        )
    if not re.fullmatch(r'#[\da-f]{3}|#[\da-f]{6}', value.lower()):
        raise ValidationError(
            'color должен иметь HEX формат'
        )
