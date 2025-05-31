from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Дополнительные поля, если нужны (например, avatar, bio)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    # email должен быть уникальным для восстановления пароля и т.д.
    email = models.EmailField(unique=True)

    #USERNAME_FIELD = 'email' # Если хотим логиниться по email
    #REQUIRED_FIELDS = ['username'] # Убрать email если он USERNAME_FIELD

    def __str__(self):
        return self.username