from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'address']
    readonly_fields = ['created_at']


class UserSchoolInline(admin.TabularInline):
    model = User
    extra = 0
    fields = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active']


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Custom admin for User model"""
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role and School', {'fields': ('role', 'school')}),
    )
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'school', 'is_staff', 'is_active')
    list_filter = ('role', 'school', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    def get_readonly_fields(self, request, obj=None):
        """Make some fields readonly for existing users"""
        readonly_fields = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly_fields.extend(['is_staff', 'is_superuser'])
        return readonly_fields