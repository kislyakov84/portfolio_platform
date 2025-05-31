from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    # Добавьте поля из CustomUser в fieldsets если нужно их редактировать в админке
    # Например:
    # fieldsets = UserAdmin.fieldsets + (
    #         (None, {'fields': ('bio', 'avatar')}),
    # )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #         (None, {'fields': ('bio', 'avatar')}),
    # )

admin.site.register(CustomUser, CustomUserAdmin)