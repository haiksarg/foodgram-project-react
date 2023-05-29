from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.validators import validate_username


class User(AbstractUser):
    username = models.SlugField(
        validators=(validate_username,),
        max_length=settings.NAME_LIMIT,
        unique=True,
    )
    email = models.EmailField(
        max_length=settings.EMAIL_LIMIT,
        unique=True,
    )
    first_name = models.CharField(
        'имя',
        max_length=settings.NAME_LIMIT,
    )
    last_name = models.CharField(
        'фамилия',
        max_length=settings.NAME_LIMIT,
    )
    password = models.CharField(
        'пароль',
        max_length=settings.NAME_LIMIT,
    )

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ('first_name', 'last_name',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='который подписывается',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='на которого подписываются',
    )

    class Meta:
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                name='unique_following',
                fields=["user", "author"],),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F("author")),),
        ]

    def __str__(self):
        return (f'Пользователь {self.user.username}'
                f'подписан на {self.author.username}')
