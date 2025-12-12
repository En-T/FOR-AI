"""
Original views with architectural and security issues.
This file is kept for reference to show what needs to be fixed.
"""
from django.shortcuts import redirect
from django.views.generic import ListView, DeleteView
from django.contrib.auth.models import User
from .models import Reward, Rewarded
from .forms import RewardForm, RewardedForm


class RewardList(ListView):
    model = Reward
    template_name = 'rewards/reward_list.html'
    context_object_name = 'rewards'


class RewardDetail(ListView):
    """Wrong: Inherits ListView but shows single object"""
    model = Reward
    template_name = 'rewards/reward_detail.html'

    def get_queryset(self):
        # Wrong: Using string parsing instead of kwargs
        pk = self.request.path.split('/')[-2]
        return Reward.objects.filter(pk=pk)


class AddReward(ListView):
    """Wrong: Inherits ListView but implements form logic (CreateView)"""
    model = Reward
    template_name = 'rewards/add_reward.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RewardForm()
        return context

    def post(self, request, *args, **kwargs):
        form = RewardForm(request.POST)
        if form.is_valid():
            form.save()
            # Wrong: Hard-coded redirect
            return redirect('/rewards/')
        # Wrong: Silent redirect on error - no error handling
        return redirect('/rewards/add')


class UpdateReward(ListView):
    model = Reward
    template_name = 'rewards/update_reward.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Wrong: Using string parsing
        pk = self.request.path.split('/')[-2]
        reward = Reward.objects.get(pk=pk)
        context['form'] = RewardForm(instance=reward)
        context['reward'] = reward
        return context

    def post(self, request, *args, **kwargs):
        # Wrong: Using string parsing
        pk = self.request.path.split('/')[-2]
        reward = Reward.objects.get(pk=pk)
        form = RewardForm(request.POST, instance=reward)
        if form.is_valid():
            form.save()
            # Wrong: Hard-coded redirect
            return redirect(f'/rewards/{pk}/')
        # Wrong: Silent redirect on error
        return redirect(f'/rewards/{pk}/update')


class DeleteReward(DeleteView):
    model = Reward

    def post(self, request, *args, **kwargs):
        # Wrong: Custom post override
        reward = self.get_object()
        reward.delete()
        # Wrong: Hard-coded redirect
        return redirect('/rewards/')


class RewardedList(ListView):
    model = Rewarded
    template_name = 'rewards/rewarded_list.html'
    context_object_name = 'rewarded_items'


class RewardedDetail(ListView):
    """Wrong: Missing LoginRequiredMixin, uses ListView for single object"""
    model = Rewarded
    template_name = 'rewards/rewarded_detail.html'

    def get_queryset(self):
        # Wrong: Using string parsing
        pk = self.request.path.split('/')[-2]
        return Rewarded.objects.filter(pk=pk)


class AddRewarded(ListView):
    """Wrong: Inherits ListView but implements form logic (CreateView)"""
    model = Rewarded
    template_name = 'rewards/add_rewarded.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RewardedForm()
        return context

    def post(self, request, *args, **kwargs):
        form = RewardedForm(request.POST)
        if form.is_valid():
            form.save()
            # Wrong: Hard-coded redirect
            return redirect('/rewards/rewarded/')
        # Wrong: Silent redirect on error
        return redirect('/rewards/rewarded/add')


class Selection(ListView):
    """Wrong: Missing LoginRequiredMixin"""
    model = Rewarded
    template_name = 'rewards/selection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Wrong: Conflicting context variable names
        context['rewards'] = Reward.objects.all()
        context['object_list'] = Rewarded.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        reward_id = request.POST.get('reward_id')
        reward = Reward.objects.get(pk=reward_id)
        Rewarded.objects.create(reward=reward, user=request.user)
        # Wrong: Hard-coded redirect
        return redirect('/rewards/rewarded/')
