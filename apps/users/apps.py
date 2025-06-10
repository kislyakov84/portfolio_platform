from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"  # <--- ИЗМЕНИТЬ ЗДЕСЬ
    label = "users"  # <--- Явно указать label для Django
