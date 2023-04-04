import re

from django.core.exceptions import ValidationError


def validate_tag_color(value):
    if not isinstance(value, str):
        raise ValidationError(
            'color должен иметь тип str'
        )
    if not re.match(r'#[\da-f]{6}', value.lower()):
        raise ValidationError(
            'color должен иметь HEX формат'
        )


def validate_tag_slug(value):
    if not isinstance(value, str):
        raise ValidationError(
            'slug должен иметь тип str'
        )
    if not re.match('^[-a-zA-Z0-9_]+$', value):
        raise ValidationError(
            (
                'slug должен состоять из английских букв, '
                'цифр и нижнего тире'
            )
        )
