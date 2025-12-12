from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Reward(models.Model):
    name = models.CharField(max_length=200, verbose_name='Reward Name')
    description = models.TextField(blank=True, verbose_name='Description')
    points_required = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Points Required'
    )
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reward'
        verbose_name_plural = 'Rewards'

    def __str__(self):
        return self.name


class Rewarded(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    reward = models.ForeignKey(
        Reward,
        on_delete=models.CASCADE,
        related_name='rewarded_items',
        verbose_name='Reward'
    )
    user_name = models.CharField(max_length=200, verbose_name='User Name')
    user_email = models.EmailField(verbose_name='User Email')
    points_used = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Points Used'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='Requested At')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Processed At')

    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'Rewarded Item'
        verbose_name_plural = 'Rewarded Items'

    def __str__(self):
        return f"{self.user_name} - {self.reward.name}"
