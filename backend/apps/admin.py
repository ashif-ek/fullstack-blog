from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

class CustomUserAdmin(UserAdmin):
    ordering = ('email',)
    list_display = ('email', 'is_staff', 'is_active')
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'is_staff', 'is_active'),
        }),
    )

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'institution')
    search_fields = ('user__email', 'full_name')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
