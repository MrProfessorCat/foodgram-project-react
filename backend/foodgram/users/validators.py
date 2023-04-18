import re

from django.core.exceptions import ValidationError


def only_letters_validator(value):
    if not re.fullmatch('[A-zА-яё- ]{2,}', value):
        raise ValidationError(
            (
                'Поле должно состоять из букв '
                'русского или английского алфавита или -'
            )
        )
