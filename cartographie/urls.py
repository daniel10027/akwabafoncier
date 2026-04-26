from django.urls import path
from . import views

urlpatterns = [
    path('', views.carte_principale, name='carte'),
]
