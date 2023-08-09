from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q
from django.db.models.constraints import CheckConstraint, UniqueConstraint

from .validators import validate_username

USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
FIRST_NAME_MAX_LENGTH = 150
LAST_NAME_MAX_LENGTH = 150
PASSWORD_MAX_LENGHT = 150


class User(AbstractUser):

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text='Введите имя пользователя',
        validators=[validate_username]
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        help_text='Введите email'
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        help_text='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        help_text='Фамилия',
        blank=True
    )
    password = models.CharField(
        max_length=PASSWORD_MAX_LENGHT,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        verbose_name="Активирован",
        default=True,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_fields'
            )
        ]

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    following = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  related_name="followings",
                                  verbose_name='автор')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower",
                             verbose_name='подписчик',)

    class Meta:
        constraints = [
            CheckConstraint(check=~Q(user=F('following')),
                            name='could_not_follow_itself'),
            UniqueConstraint(fields=['user', 'following'],
                             name='unique_follower')
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        default_related_name = 'follow'

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.following}'
