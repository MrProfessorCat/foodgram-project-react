from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(validate_username,),
        verbose_name='Никнейм пользователя',
        help_text='Укажите никнейм'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта',
        help_text='Укажите электронную почту'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Укажите имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Укажите фамилию'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
        help_text='Укажите пароль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return (
            f'{self.username} '
            f'({self.first_name} {self.last_name}) '
            f'с email: {self.email}'
        )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='followers',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='followings',
        verbose_name='Автор, на которого подписываемся',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='follow_unique'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='follow_user_author_constraint'
            )
        )
