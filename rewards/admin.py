from django.contrib import admin
from .models import Reward, Rewarded


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('title', 'points_required', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)


@admin.register(Rewarded)
class RewardedAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'redeemed_at')
    search_fields = ('user__username', 'reward__title')
    list_filter = ('redeemed_at',)
