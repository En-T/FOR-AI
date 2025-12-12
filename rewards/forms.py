from django import forms
from .models import Reward, Rewarded


class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ['name', 'description', 'points_required', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter reward name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description'}),
            'points_required': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RewardedForm(forms.ModelForm):
    class Meta:
        model = Rewarded
        fields = ['reward', 'user_name', 'user_email', 'points_used', 'status', 'notes']
        widgets = {
            'reward': forms.Select(attrs={'class': 'form-control'}),
            'user_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter user name'}),
            'user_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'points_used': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }
