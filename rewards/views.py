from django.shortcuts import render, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Reward, Rewarded
from .forms import RewardForm, RewardedForm


class RewardList(ListView):
    model = Reward
    template_name = 'rewards/reward_list.html'
    context_object_name = 'rewards'


class RewardDetail(DetailView):
    model = Reward
    template_name = 'rewards/reward_detail.html'
    context_object_name = 'reward'


class AddReward(CreateView):
    model = Reward
    form_class = RewardForm
    template_name = 'rewards/add_reward.html'
    success_url = reverse_lazy('reward-list')

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class UpdateReward(UpdateView):
    model = Reward
    form_class = RewardForm
    template_name = 'rewards/update_reward.html'
    context_object_name = 'reward'

    def get_success_url(self):
        return reverse_lazy('reward-detail', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class DeleteReward(DeleteView):
    model = Reward
    success_url = reverse_lazy('reward-list')


class RewardedList(ListView):
    model = Rewarded
    template_name = 'rewards/rewarded_list.html'
    context_object_name = 'rewarded_items'


class RewardedDetail(LoginRequiredMixin, DetailView):
    model = Rewarded
    template_name = 'rewards/rewarded_detail.html'
    context_object_name = 'rewarded'


class AddRewarded(LoginRequiredMixin, CreateView):
    model = Rewarded
    form_class = RewardedForm
    template_name = 'rewards/add_rewarded.html'
    success_url = reverse_lazy('rewarded-list')

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class Selection(LoginRequiredMixin, ListView):
    model = Reward
    template_name = 'rewards/selection.html'
    context_object_name = 'rewards'

    def post(self, request, *args, **kwargs):
        reward_id = request.POST.get('reward_id')
        if reward_id:
            try:
                reward = Reward.objects.get(pk=reward_id)
                Rewarded.objects.create(reward=reward, user=request.user)
                messages.success(request, f'Successfully redeemed {reward.title}!')
                return redirect('rewarded-list')
            except Reward.DoesNotExist:
                messages.error(request, 'Reward not found.')
        else:
            messages.error(request, 'Please select a reward.')
        return redirect('selection')
