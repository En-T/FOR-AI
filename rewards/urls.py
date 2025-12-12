from django.urls import path
from . import views

urlpatterns = [
    # Reward URLs
    path('', views.RewardList.as_view(), name='reward-list'),
    path('<int:pk>/', views.RewardDetail.as_view(), name='reward-detail'),
    path('add/', views.AddReward.as_view(), name='reward-add'),
    path('<int:pk>/update/', views.UpdateReward.as_view(), name='reward-update'),
    path('<int:pk>/delete/', views.DeleteReward.as_view(), name='reward-delete'),

    # Rewarded URLs
    path('rewarded/', views.RewardedList.as_view(), name='rewarded-list'),
    path('rewarded/<int:pk>/', views.RewardedDetail.as_view(), name='rewarded-detail'),
    path('rewarded/add/', views.AddRewarded.as_view(), name='rewarded-add'),
    path('selection/', views.Selection.as_view(), name='selection'),
]
