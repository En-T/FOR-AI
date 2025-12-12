from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rewarded/', views.rewarded_list, name='rewarded_list'),
    path('reward/add/', views.add_reward, name='add_reward'),
    path('rewarded/add/', views.add_rewarded, name='add_rewarded'),
    path('reward/edit/<int:pk>/', views.edit_reward, name='edit_reward'),
    path('rewarded/edit/<int:pk>/', views.edit_rewarded, name='edit_rewarded'),
    path('reward/delete/<int:pk>/', views.delete_reward, name='delete_reward'),
    path('rewarded/delete/<int:pk>/', views.delete_rewarded, name='delete_rewarded'),
    path('selection/', views.selection, name='selection'),
]
