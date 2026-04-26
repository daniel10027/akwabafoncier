from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('a-propos/', views.a_propos, name='a_propos'),
    path('tarifs/', views.tarifs, name='tarifs'),
    path('contact/', views.contact, name='contact'),
]
