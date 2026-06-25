from django.urls import include, path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('', views.main_dashboard, name='main_dashboard'),
    path('search/', views.doctor_search, name='doctor_search'),
    path('api/doctor-suggestions/', views.doctor_suggestions, name='doctor_suggestions'),

    path('', include('django.contrib.auth.urls')),  # Include built-in auth URLs for login, logout, password reset, etc.
]