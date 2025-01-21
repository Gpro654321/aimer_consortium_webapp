from django.urls import path

from . import views  # Import views from your app's views.py

urlpatterns = [
    path('', views.registration_view, name='registration'),
    path('payment_success/', views.payment_success, name='payment_success'),
]
