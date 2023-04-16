import re

from django.core.exceptions import ValidationError


def validate_tag_color(value):
    if not re.fullmatch(r'#[\da-f]{3}|#[\da-f]{6}', value.lower()):
        raise ValidationError(
            'Поле color должен иметь HEX формат'
        )


def validate_ingredient(value):
    if not re.fullmatch(r'[А-яA-z- )(]+', value):
        raise ValidationError(
            (
                'Поле measurement_unit должно состоять '
                'из русских, английских букв и -'
            )
        )
