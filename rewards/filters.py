import django_filters
from .models import Reward, Rewarded


class RewardFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Reward Name')
    points_required = django_filters.NumberFilter(label='Points Required')
    points_min = django_filters.NumberFilter(field_name='points_required', lookup_expr='gte', label='Min Points')
    points_max = django_filters.NumberFilter(field_name='points_required', lookup_expr='lte', label='Max Points')
    is_active = django_filters.BooleanFilter(label='Active Only')

    class Meta:
        model = Reward
        fields = ['name', 'points_required', 'is_active']


class RewardedFilter(django_filters.FilterSet):
    user_name = django_filters.CharFilter(lookup_expr='icontains', label='User Name')
    user_email = django_filters.CharFilter(lookup_expr='icontains', label='User Email')
    status = django_filters.ChoiceFilter(choices=Rewarded.STATUS_CHOICES, label='Status')
    reward = django_filters.ModelChoiceFilter(queryset=Reward.objects.all(), label='Reward')
    requested_at = django_filters.DateFilter(label='Requested Date')

    class Meta:
        model = Rewarded
        fields = ['user_name', 'user_email', 'status', 'reward']
