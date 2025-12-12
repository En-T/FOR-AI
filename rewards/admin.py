from django.contrib import admin
from .models import Reward, Rewarded


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_required', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Rewarded)
class RewardedAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'reward', 'points_used', 'status', 'requested_at', 'processed_at']
    list_filter = ['status', 'requested_at', 'reward']
    search_fields = ['user_name', 'user_email', 'reward__name']
    list_editable = ['status']
    ordering = ['-requested_at']
    readonly_fields = ['requested_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user_name', 'user_email')
        }),
        ('Reward Details', {
            'fields': ('reward', 'points_used')
        }),
        ('Status', {
            'fields': ('status', 'notes', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('requested_at',)
        }),
    )
