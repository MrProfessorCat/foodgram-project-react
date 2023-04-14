import re

from django.core.exceptions import ValidationError


def only_letters_validator(value):
    if not re.fullmatch('[A-zА-я-]{2,}', value):
        raise ValidationError(
            (
                'Имя и Фамилия должны состоять из букв '
                'русского или английского алфавита или -'
            )
        )
