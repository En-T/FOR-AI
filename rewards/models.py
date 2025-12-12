from django.db import models
from django.contrib.auth.models import User


class Reward(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    points_required = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Rewarded(models.Model):
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.reward.title}"
