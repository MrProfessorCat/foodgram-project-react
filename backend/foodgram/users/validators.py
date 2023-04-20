import re

from django.core.exceptions import ValidationError


def only_letters_validator(value):
    if not re.fullmatch('[A-zА-я- ]{2,}', value):
        raise ValidationError(
            (
                'Поле должно состоять из букв '
                'русского или английского алфавита или -'
            )
        )


def username_validator(value):
    if value.lower() == 'me':
        raise ValidationError(
            f'username не может быть "{value}"'
        )
