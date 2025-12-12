from django import forms
from .models import Reward, Rewarded


class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ['title', 'description', 'points_required']


class RewardedForm(forms.ModelForm):
    class Meta:
        model = Rewarded
        fields = ['reward', 'user']
