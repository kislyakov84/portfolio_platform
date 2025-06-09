# Файл: apps/projects/admin.py

from django.contrib import admin
from .models import Project, Technology, Comment, Like, ProjectMedia


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # ... (код без изменений)
    list_display = ("title", "owner", "created_at", "slug")
    list_filter = ("owner", "technologies", "tags", "created_at")
    search_fields = ("title", "description", "owner__username")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ProjectMedia)
class ProjectMediaAdmin(admin.ModelAdmin):
    # ... (код без изменений)
    list_display = ("project", "file_type", "caption", "uploaded_at")
    list_filter = ("project", "file_type")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("project", "author", "text_summary", "created_at")
    list_filter = ("project", "author", "created_at")
    search_fields = ("text", "author__username", "project__title")

    # Используем современный, идиоматичный и type-safe способ
    @admin.display(description="Text")
    def text_summary(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    # Старую строку 'text_summary.short_description = ...' удаляем


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "created_at")
    list_filter = ("project", "user", "created_at")
