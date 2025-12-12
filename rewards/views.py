from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Reward, Rewarded
from .forms import RewardForm, RewardedForm
from .filters import RewardFilter, RewardedFilter


def index(request):
    rewards = Reward.objects.all()
    reward_filter = RewardFilter(request.GET, queryset=rewards)
    context = {
        'rewards': reward_filter.qs,
        'filter': reward_filter,
    }
    return render(request, 'rewarded/index.html', context)


def rewarded_list(request):
    rewarded_items = Rewarded.objects.select_related('reward').all()
    rewarded_filter = RewardedFilter(request.GET, queryset=rewarded_items)
    context = {
        'rewarded_items': rewarded_filter.qs,
        'filter': rewarded_filter,
    }
    return render(request, 'rewarded/rewarded.html', context)


def add_reward(request):
    if request.method == 'POST':
        form = RewardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reward added successfully!')
            return redirect('index')
    else:
        form = RewardForm()
    return render(request, 'rewarded/add_reward.html', {'form': form})


def add_rewarded(request):
    if request.method == 'POST':
        form = RewardedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rewarded item added successfully!')
            return redirect('rewarded_list')
    else:
        form = RewardedForm()
    return render(request, 'rewarded/add_rewarded.html', {'form': form})


def edit_reward(request, pk):
    reward = get_object_or_404(Reward, pk=pk)
    if request.method == 'POST':
        form = RewardForm(request.POST, instance=reward)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reward updated successfully!')
            return redirect('index')
    else:
        form = RewardForm(instance=reward)
    return render(request, 'rewarded/edit.html', {'form': form, 'reward': reward})


def edit_rewarded(request, pk):
    rewarded = get_object_or_404(Rewarded, pk=pk)
    if request.method == 'POST':
        form = RewardedForm(request.POST, instance=rewarded)
        if form.is_valid():
            rewarded_item = form.save(commit=False)
            if rewarded_item.status in ['approved', 'completed']:
                rewarded_item.processed_at = timezone.now()
            rewarded_item.save()
            messages.success(request, 'Rewarded item updated successfully!')
            return redirect('rewarded_list')
    else:
        form = RewardedForm(instance=rewarded)
    return render(request, 'rewarded/edit.html', {'form': form, 'rewarded': rewarded})


def delete_reward(request, pk):
    reward = get_object_or_404(Reward, pk=pk)
    if request.method == 'POST':
        reward.delete()
        messages.success(request, 'Reward deleted successfully!')
        return redirect('index')
    return render(request, 'rewarded/delete_reward.html', {'reward': reward})


def delete_rewarded(request, pk):
    rewarded = get_object_or_404(Rewarded, pk=pk)
    if request.method == 'POST':
        rewarded.delete()
        messages.success(request, 'Rewarded item deleted successfully!')
        return redirect('rewarded_list')
    return render(request, 'rewarded/delete_rewarded.html', {'rewarded': rewarded})


def selection(request):
    rewards = Reward.objects.filter(is_active=True)
    reward_filter = RewardFilter(request.GET, queryset=rewards)
    context = {
        'rewards': reward_filter.qs,
        'filter': reward_filter,
    }
    return render(request, 'rewarded/selection.html', context)
