import re

from django.core.exceptions import ValidationError

from core import constants


def validate_username(value):
    invalid_characters = re.sub(constants.USERNAME_PATTERN, '', value)
    if invalid_characters:
        raise ValidationError(
            f'Недопустимые символы: {invalid_characters}')
    if value == 'me':
        raise ValidationError(
            'Имя пользователя не может быть <me>.',
            params={'value': value},
        )
    return value


def validate_hexname(value):
    invalid_characters = re.sub(constants.HEX_NAME_PATTERN, '', value)
    if invalid_characters:
        raise ValidationError(
            f'Недопустимые символы: {invalid_characters}')
