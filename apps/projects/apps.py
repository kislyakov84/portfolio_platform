from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.projects"  # <--- ИЗМЕНИТЬ ЗДЕСЬ
    label = "projects"  # <--- Явно указать label для Django
