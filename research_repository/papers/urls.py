# papers/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_papers, name='list_papers'),
    path('add/', views.add_paper, name='add_paper'),
    path('delete/', views.delete_paper, name='delete_paper'),
]