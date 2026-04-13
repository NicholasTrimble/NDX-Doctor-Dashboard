from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_dashboard, name='main_dashboard'),
    path('search/', views.doctor_search, name='doctor_search'),
    path('api/doctor-suggestions/', views.doctor_suggestions, name='doctor_suggestions'),
]